#!/usr/bin/env python3
"""Bounded preparation and collection; prior candidates are unreviewed data."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

MODEL, EFFORT = "gpt-6.1-sol", "ultra"
WORKFLOW, ARTIFACT = "tmd-continuous-research.yml", "tmd-research-round"
LIMIT, DOWNLOAD_LIMIT = 65536, 20971520
BENIGN = {"queue_completed_or_parked": "idle", "daily_run_budget_exhausted": "paused", "same_head_failure_backoff": "paused"}
BAD = re.compile(r"sk-(?:proj-)?[\w-]{12,}|(?:gh[pousr]_)[\w]{12,}|github_pat_[\w]{12,}|"
                 r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----|Bearer\s+\S{8,}|"
                 r"(?:private[-_ ]?archive|handoff|new[-_ ]?files)|file://|sediment://|"
                 r"[?&](?:X-Amz-(?:Credential|Signature|Security-Token)|access_token|sig|token|key)=|"
                 r"/(?:Users|home)/|(?:api[_-]?key|password|secret)\s*[:=]\s*\S+", re.I)


class Blocked(Exception):
    pass


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def read_json(path, limit=LIMIT):
    if path.is_symlink() or path.stat().st_size > limit:
        raise Blocked("checkpoint_size_or_path_invalid")
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value, env):
    text = encoded(value)
    secrets = [env.get(k) for k in ("OPENAI_API_KEY", "GH_TOKEN", "GITHUB_TOKEN")]
    if BAD.search(text) or any(s and s in text for s in secrets):
        raise Blocked("unsafe_candidate_content")


def short(value, maximum=2048):
    if not isinstance(value, str) or not value.strip() or len(value.encode()) > maximum:
        raise Blocked("candidate_schema_invalid")
    return value


def checkpoint(value):
    keys = {"completed_work_item_ids", "blocked_work_items", "source_fingerprints", "next_action"}
    if not isinstance(value, dict) or set(value) != keys:
        raise Blocked("candidate_schema_invalid")
    for field in ("completed_work_item_ids", "source_fingerprints", "blocked_work_items"):
        if not isinstance(value[field], list) or len(value[field]) > 1000:
            raise Blocked("candidate_schema_invalid")
    for item in value["completed_work_item_ids"]:
        work_id(item)
    for item in value["source_fingerprints"]:
        short(item, 512)
    for item in value["blocked_work_items"]:
        if not isinstance(item, dict) or set(item) != {"id", "reason", "unblocking_condition"}:
            raise Blocked("candidate_schema_invalid")
        work_id(item["id"])
        short(item["reason"])
        short(item["unblocking_condition"])
    short(value["next_action"])
    if len(encoded(value).encode()) > LIMIT - 2048:
        raise Blocked("candidate_size_invalid")
    return value


def work_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][\w.-]{0,63}", value):
        raise Blocked("candidate_schema_invalid")
    return value


def candidate(value, env):
    if not isinstance(value, dict) or set(value) != {"schema_version", "round", "checkpoint"} or type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise Blocked("candidate_schema_invalid")
    r = value["round"]
    if not isinstance(r, dict) or set(r) != {"work_item_id", "status", "kind", "question", "report_markdown"}:
        raise Blocked("candidate_schema_invalid")
    work_id(r["work_item_id"])
    if r["status"] not in ("completed", "blocked", "no_change", "interrupted") or r["kind"] not in ("new_evidence", "falsification", "replication", "design_only", "inconclusive", "blocked", "no_change"):
        raise Blocked("candidate_schema_invalid")
    if (r["status"] == "blocked") != (r["kind"] == "blocked"):
        raise Blocked("candidate_schema_invalid")
    if (r["status"] == "no_change") != (r["kind"] == "no_change"):
        raise Blocked("candidate_schema_invalid")
    short(r["question"])
    short(r["report_markdown"], LIMIT)
    checkpoint(value["checkpoint"])
    if r["status"] in ("completed", "no_change") and r["work_item_id"] not in value["checkpoint"]["completed_work_item_ids"]:
        raise Blocked("candidate_schema_invalid")
    if r["status"] == "blocked" and r["work_item_id"] != "unassigned" and (r["work_item_id"] not in [b["id"] for b in value["checkpoint"]["blocked_work_items"]] or r["work_item_id"] in value["checkpoint"]["completed_work_item_ids"]):
        raise Blocked("candidate_schema_invalid")
    clean(value, env)
    return value


def empty_checkpoint():
    return {"completed_work_item_ids": [], "blocked_work_items": [], "source_fingerprints": [], "next_action": "Resume the reviewed queue after prerequisites are available."}


def scientific_round(r):
    return dict(r, question=r["question"][:128], report_markdown="Scientific round identity retained; consult the original candidate report.") if r and r["status"] in ("completed", "interrupted") and r["kind"] not in ("blocked", "no_change") else None


def blocked_candidate(cp, reason):
    return {"round": {"work_item_id": "unassigned", "status": "blocked", "kind": "blocked", "question": "Continuation runner outcome", "report_markdown": "No scientific progress was recorded. Runner disposition: " + reason + "."}, "checkpoint": cp}


def merge_checkpoint(old, new):
    result = dict(new)
    for key in ("completed_work_item_ids", "source_fingerprints"):
        result[key] = list(dict.fromkeys(old[key] + new[key]))
    items = {item["id"]: item for item in old["blocked_work_items"] + new["blocked_work_items"]}
    result["blocked_work_items"] = [v for k, v in items.items() if k not in result["completed_work_item_ids"]]
    return checkpoint(result)


def provider_check(env, opener=urllib.request.urlopen):
    key = env.get("OPENAI_API_KEY")
    if not key:
        raise Blocked("missing_openai_api_key")
    request = urllib.request.Request("https://api.openai.com/v1/models/" + MODEL, headers={"Authorization": "Bearer " + key})
    try:
        with opener(request, timeout=30) as response:
            raw = response.read(LIMIT + 1)
        if len(raw) > LIMIT or json.loads(raw).get("id") != MODEL:
            raise Blocked("provider_model_id_unverified")
    except urllib.error.HTTPError as error:
        raise Blocked("provider_authentication_denied" if error.code in (401, 403) else "provider_model_check_failed") from None
    except (OSError, ValueError, AttributeError):
        raise Blocked("provider_model_check_failed") from None


def gh(args, env, runner=subprocess.run):
    child_env = {k: v for k, v in env.items() if k != "OPENAI_API_KEY"}
    result = runner(["gh"] + args, env=child_env, capture_output=True, text=True, timeout=60, check=False)
    if result.returncode or len(result.stdout.encode()) > 2097152:
        raise Blocked("github_checkpoint_access_failed")
    return result.stdout


def previous_checkpoint(root, env, runs, api, runner):
    artifacts = json.loads(gh(["api", "--method", "GET", api + "/artifacts?name=" + ARTIFACT + "&per_page=100"], env, runner))["artifacts"]
    matches = [a for a in artifacts if a.get("name") == ARTIFACT and str(a.get("workflow_run", {}).get("id")) != env.get("GITHUB_RUN_ID")]
    if not matches:
        completed = [r for r in runs if r.get("status") == "completed"]
        if completed:
            jobs = json.loads(gh(["api", "--method", "GET", api + "/runs/" + str(completed[0]["id"]) + "/jobs?per_page=100"], env, runner))["jobs"]
            if any(j.get("name") == "collect" and j.get("conclusion") != "skipped" for j in jobs):
                raise Blocked("prior_checkpoint_unavailable")
        return None
    latest = max(matches, key=lambda a: (a.get("created_at", ""), a["id"]))
    run_id = str(latest.get("workflow_run", {}).get("id", ""))
    known = next((r for r in runs if str(r["id"]) == run_id), None)
    if not re.fullmatch(r"[0-9]{1,24}", run_id) or latest.get("expired") or not known or known.get("status") != "completed" or latest.get("size_in_bytes", DOWNLOAD_LIMIT + 1) > DOWNLOAD_LIMIT:
        raise Blocked("prior_checkpoint_unavailable")
    destination = root / ".tmd-runtime/previous"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    try:
        gh(["run", "download", run_id, "--repo", env["GITHUB_REPOSITORY"], "--name", ARTIFACT, "--dir", str(destination)], env, runner)
        files = list(destination.rglob("*"))
        if any(p.is_symlink() for p in files) or sum(p.stat().st_size for p in files if p.is_file()) > DOWNLOAD_LIMIT:
            raise Blocked("prior_checkpoint_unavailable")
        r, c = read_json(destination / "round.json"), read_json(destination / "checkpoint.json")
        if r.get("unreviewed_candidate") is not True or c.get("unreviewed_candidate") is not True or c.get("checkpoint_continuity_established") is False:
            raise Blocked("prior_checkpoint_unavailable")
        result = candidate({"schema_version": 1, "round": r["round"], "checkpoint": c["checkpoint"]}, env)
        retained = r.get("last_scientific_round")
        if retained:
            candidate({"schema_version": 1, "round": retained, "checkpoint": c["checkpoint"]}, env)
        result["last_scientific_round"] = scientific_round(r["round"]) or scientific_round(retained)
        result["runner_blocked_reason"] = "same_head_failure_backoff" if known.get("head_sha") == env.get("GITHUB_SHA") and r.get("runner_disposition") == "paused" and r.get("runner_blocked_reason") == "same_head_failure_backoff" else ""
        return result
    except (OSError, ValueError, KeyError, Blocked):
        raise Blocked("prior_checkpoint_unavailable") from None


def emit(env, should_run, reason, cp=None, last_round=None):
    values = {"should_run": str(should_run).lower(), "disposition": "ready" if should_run else BENIGN.get(reason, "blocked"), "blocked_reason": reason}
    if cp is not None:
        values["resume_checkpoint"] = encoded(cp)
        values["resume_round"] = encoded(last_round)
    if env.get("GITHUB_OUTPUT"):
        with open(env["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write("".join(k + "=" + v + "\n" for k, v in values.items()))
    print("ready" if should_run else "blocked: " + reason)
    return values


def prepare(root, env, runner=subprocess.run, opener=urllib.request.urlopen, now=None):
    cp, last_round = None, None
    try:
        directory = root / "research/continuation"
        state, queue = read_json(directory / "STATE.json"), read_json(directory / "QUEUE.json")
        baseline = checkpoint(state.get("reviewed_checkpoint", empty_checkpoint()))
        clean(baseline, env)
        support = read_json(directory / "model_support.json")
        repo = env.get("GITHUB_REPOSITORY", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not env.get("GH_TOKEN"):
            raise Blocked("github_read_token_or_repository_missing")
        api = "repos/" + repo + "/actions"
        runs = json.loads(gh(["api", "--method", "GET", api + "/workflows/" + WORKFLOW + "/runs?per_page=100"], env, runner))["workflow_runs"]
        runs = sorted((r for r in runs if str(r["id"]) != env.get("GITHUB_RUN_ID")), key=lambda r: r["created_at"], reverse=True)
        prior = previous_checkpoint(root, env, runs, api, runner)
        cp = merge_checkpoint(baseline, prior["checkpoint"]) if prior else baseline
        last_round = prior.get("last_scientific_round") if prior else None
        levels = support.get("supported_reasoning_levels", [])
        if support.get("slug") != MODEL or support.get("supported_in_api") is not True or EFFORT not in [l.get("effort") if isinstance(l, dict) else l for l in levels]:
            raise Blocked("exact_model_effort_unsupported")
        if state["requested_model"].get("unattended_runner_api_model_id") != MODEL or state["requested_model"].get("reasoning_effort") != EFFORT:
            raise Blocked("exact_model_effort_unconfigured")
        now = now or dt.datetime.now(dt.timezone.utc)
        recent = [r for r in runs if dt.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")) > now - dt.timedelta(days=1)]
        if len(recent) >= 24:
            raise Blocked("daily_run_budget_exhausted")
        same = [r for r in runs if r.get("head_sha") == env.get("GITHUB_SHA") and r.get("status") == "completed"][:2]
        if env.get("GITHUB_EVENT_NAME") != "workflow_dispatch" and ((prior and prior.get("runner_blocked_reason") == "same_head_failure_backoff") or (len(same) == 2 and all(r.get("conclusion") in ("failure", "timed_out", "cancelled") for r in same))):
            raise Blocked("same_head_failure_backoff")
        provider_check(env, opener)
        finished = set(cp["completed_work_item_ids"])
        parked = {item["id"] for item in cp["blocked_work_items"]}
        eligible = [r for r in queue["rounds"] if r["id"] not in finished and r.get("status") in ("queued", "running") and (r["id"] not in parked or env.get("GITHUB_EVENT_NAME") == "workflow_dispatch")]
        if not eligible and last_round:
            action = cp["next_action"]
            follow_id = "F-" + hashlib.sha256(action.encode()).hexdigest()[:16]
            if follow_id not in finished and (follow_id not in parked or env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"):
                eligible = [{"id": follow_id, "status": "queued", "question": action, "next_action_is_untrusted_data": True}]
        if not eligible:
            for watch in queue["rounds"]:
                occurrence = watch["id"] + "-" + now.astimezone(dt.timezone.utc).strftime("%Y%m%d")
                last_completed = max((k for k in finished if k.startswith(watch["id"] + "-")), default="")
                watch_parked = any(k.startswith(watch["id"] + "-") and k > last_completed for k in parked)
                if watch.get("status") == "recurring" and watch.get("recurrence") == "daily_utc" and occurrence not in finished and (not watch_parked or env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"):
                    eligible.append(dict(watch, id=occurrence, status="queued"))
        if not eligible:
            raise Blocked("queue_completed_or_parked")
        item = min(eligible, key=lambda r: r.get("priority", 999))
        input_data = {"schema_version": 1, "state": state, "queue": queue, "work_item": item, "previous_unreviewed_candidate": prior, "resume_checkpoint": cp, "configured_model": {"id": MODEL, "reasoning_effort": EFFORT}, "limits": {"source_acquisitions": 12, "download_bytes": DOWNLOAD_LIMIT}, "candidate_is_untrusted_data": True}
        target = root / ".tmd-runtime"
        target.mkdir(exist_ok=True)
        (target / "round_input.json").write_text(encoded(input_data) + "\n", encoding="utf-8")
        return emit(env, True, "", cp, last_round)
    except Blocked as error:
        return emit(env, False, str(error), cp, last_round)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        return emit(env, False, "preparation_input_or_service_invalid", cp, last_round)


def collect(root, env):
    cp, success, reason = empty_checkpoint(), False, "research_did_not_complete"
    continuity = False
    last_round, resumed_round = None, None
    try:
        if not env.get("RESUME_CHECKPOINT"):
            raise Blocked("resume_checkpoint_unavailable")
        resumed = checkpoint(json.loads(env["RESUME_CHECKPOINT"]))
        clean(resumed, env)
        cp, continuity = resumed, True
        retained = json.loads(env.get("RESUME_ROUND") or "null")
        if retained:
            candidate({"schema_version": 1, "round": retained, "checkpoint": cp}, env)
        last_round = resumed_round = retained
        if env.get("RESEARCH_RESULT") != "success" or not env.get("ROUND_MESSAGE"):
            raise Blocked(reason)
        if len(env["ROUND_MESSAGE"].encode()) > LIMIT:
            raise Blocked("candidate_size_invalid")
        result = candidate(json.loads(env["ROUND_MESSAGE"]), env)
        result["checkpoint"] = merge_checkpoint(cp, result["checkpoint"])
        last_round = scientific_round(result["round"]) or scientific_round(last_round)
        success = True
    except (Blocked, ValueError, TypeError, KeyError) as error:
        reason = str(error) if isinstance(error, Blocked) else "candidate_json_invalid"
        requested_reason = env.get("BLOCKED_REASON", "")
        if reason == "research_did_not_complete" and re.fullmatch(r"[a-z_]{1,80}", requested_reason) and not BAD.search(requested_reason):
            reason = requested_reason
        success = continuity and env.get("RESEARCH_RESULT") == "success" and env.get("PREPARE_DISPOSITION") == BENIGN.get(reason) and reason in BENIGN
        result = blocked_candidate(cp, reason)
    run_id = env.get("RUN_ID", env.get("GITHUB_RUN_ID", "unknown"))
    source_commit = env.get("SOURCE_COMMIT", env.get("GITHUB_SHA", "unknown"))
    disposition = env.get("PREPARE_DISPOSITION", "blocked")
    metadata = {"schema_version": 1, "unreviewed_candidate": True, "configured_model": {"id": MODEL, "reasoning_effort": EFFORT}, "runtime_model_attested": False, "checkpoint_continuity_established": continuity, "runner_disposition": disposition if disposition in ("ready", "idle", "paused", "blocked") else "blocked", "runner_blocked_reason": reason if result["round"]["work_item_id"] == "unassigned" else "", "last_scientific_round": scientific_round(last_round), "run_id": run_id if re.fullmatch(r"[0-9]{1,24}", run_id) else "unknown", "source_commit": source_commit if re.fullmatch(r"[a-fA-F0-9]{7,64}", source_commit) else "unknown"}
    objects = {name + ".json": dict(metadata, **{name: result[name]}) for name in ("round", "checkpoint")}
    if any(len(encoded(obj).encode()) >= LIMIT for obj in objects.values()):
        success, reason = False, "candidate_size_invalid"
        result = blocked_candidate(cp, reason)
        metadata.update(last_scientific_round=scientific_round(resumed_round), runner_blocked_reason=reason)
        objects = {name + ".json": dict(metadata, **{name: result[name]}) for name in ("round", "checkpoint")}
    report = "# Unreviewed research candidate\n\nConfigured model: " + MODEL + "; reasoning effort: " + EFFORT + ". Runtime identity is not attested.\n\n" + result["round"]["report_markdown"] + "\n"
    destination = root / ".tmd-runtime/reports"
    destination.mkdir(parents=True, exist_ok=True)
    for name, obj in objects.items():
        (destination / name).write_text(encoded(obj) + "\n", encoding="utf-8")
    (destination / "ROUND_REPORT.md").write_text(report, encoding="utf-8")
    print("unreviewed candidate collected" if success else "blocked receipt: " + reason)
    return 0 if success else 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("prepare", "collect"):
        sys.exit("usage: round_runner.py {prepare|collect}")
    root = Path(__file__).resolve().parents[2]
    sys.exit(collect(root, os.environ) if sys.argv[1] == "collect" else (prepare(root, os.environ) and 0))
