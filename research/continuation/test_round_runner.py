"""Offline behavioral tests; these do not attest actual API inference."""
import contextlib
import datetime as dt
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import urllib.error

import round_runner as runner


class Response:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def read(self, limit):
        return json.dumps(self.value).encode()[:limit]


class RoundRunnerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "research/continuation").mkdir(parents=True)
        self.env = {"OPENAI_API_KEY": "sentinel-provider-secret", "GH_TOKEN": "sentinel-actions-token", "GITHUB_REPOSITORY": "owner/repo", "GITHUB_RUN_ID": "99", "GITHUB_SHA": "a" * 40, "GITHUB_EVENT_NAME": "schedule", "GITHUB_OUTPUT": str(self.root / "outputs")}
        self.now = dt.datetime(2026, 10, 2, 12, tzinfo=dt.timezone.utc)
        self.runs, self.artifacts, self.calls = [], [], []
        self.prior = None
        self.prior_metadata = {}
        self.jobs = []
        self.write("STATE.json", {"requested_model": {"unattended_runner_api_model_id": runner.MODEL, "reasoning_effort": runner.EFFORT}})
        self.write("QUEUE.json", {"rounds": [{"id": "R1", "status": "queued", "priority": 1}, {"id": "R2", "status": "queued", "priority": 2}]})
        self.write("model_support.json", {"slug": runner.MODEL, "supported_in_api": True, "supported_reasoning_levels": [{"effort": runner.EFFORT}]})

    def write(self, name, value):
        (self.root / "research/continuation" / name).write_text(json.dumps(value))

    def value(self, report="Measured public-source result."):
        return {"schema_version": 1, "round": {"work_item_id": "R1", "status": "completed", "kind": "new_evidence", "question": "What is measured?", "report_markdown": report}, "checkpoint": {"completed_work_item_ids": ["R1"], "blocked_work_items": [], "source_fingerprints": ["doi:10.1234/test sha256:abc"], "next_action": "Measure R2."}}

    def fake_gh(self, args, **kwargs):
        self.calls.append(args)
        self.assertNotIn("OPENAI_API_KEY", kwargs["env"])
        self.assertNotIn("shell", kwargs)
        if args[1:3] == ["run", "download"]:
            target = Path(args[args.index("--dir") + 1])
            for name in ("round", "checkpoint"):
                (target / (name + ".json")).write_text(json.dumps(dict(self.prior_metadata, unreviewed_candidate=True, **{name: self.prior[name]})))
            output = ""
        elif "/workflows/" in args[-1]:
            output = json.dumps({"workflow_runs": self.runs})
        elif "/jobs?" in args[-1]:
            output = json.dumps({"jobs": self.jobs})
        else:
            output = json.dumps({"artifacts": self.artifacts})
        return subprocess.CompletedProcess(args, 0, output, "")

    def prepare(self, opener=None):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            result = runner.prepare(self.root, self.env, runner=self.fake_gh, opener=opener or (lambda *a, **k: Response({"id": runner.MODEL})), now=self.now)
        self.output = stream.getvalue()
        return result

    def collect(self, value=None, **updates):
        env = dict(self.env, ROUND_MESSAGE=json.dumps(value if value is not None else self.value()), RESEARCH_RESULT="success", RESUME_CHECKPOINT=json.dumps(runner.empty_checkpoint()))
        env.update(updates)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            result = runner.collect(self.root, env)
        self.output = stream.getvalue()
        return result

    def reports(self):
        path = self.root / ".tmd-runtime/reports"
        self.assertEqual({p.name for p in path.iterdir()}, {"round.json", "checkpoint.json", "ROUND_REPORT.md"})
        return json.loads((path / "round.json").read_text()), json.loads((path / "checkpoint.json").read_text())

    def run_info(self, ident=1, conclusion="success", head=None):
        return {"id": ident, "created_at": "2026-10-02T11:00:00Z", "status": "completed", "conclusion": conclusion, "head_sha": head or self.env["GITHUB_SHA"]}

    def install_prior(self):
        self.prior = self.value()
        self.runs = [self.run_info()]
        self.artifacts = [{"id": 7, "name": runner.ARTIFACT, "created_at": "2026-10-02T11:30:00Z", "workflow_run": {"id": 1}, "expired": False, "size_in_bytes": 1000}]

    def test_missing_key_never_calls_provider(self):
        del self.env["OPENAI_API_KEY"]
        result = self.prepare(lambda *a, **k: self.fail("provider called"))
        self.assertEqual(result["blocked_reason"], "missing_openai_api_key")
        self.assertEqual(len(self.calls), 2)

    def test_provider_wrong_id_fails_closed(self):
        result = self.prepare(lambda *a, **k: Response({"id": "gpt-6.1-other"}))
        self.assertEqual(result["blocked_reason"], "provider_model_id_unverified")
        self.assertEqual(len(self.calls), 2)

    def test_provider_401_never_echoes_body_or_credentials(self):
        def denied(*a, **k):
            raise urllib.error.HTTPError("https://api.openai.com", 401, "sentinel-provider-secret", {}, io.BytesIO(b"sentinel-actions-token"))
        result = self.prepare(denied)
        self.assertEqual(result["blocked_reason"], "provider_authentication_denied")
        self.assertNotIn("sentinel", self.output + (self.root / "outputs").read_text())

    def test_catalog_requires_exact_ultra(self):
        self.write("model_support.json", {"slug": runner.MODEL, "supported_in_api": True, "supported_reasoning_levels": [{"effort": "high"}]})
        self.assertEqual(self.prepare()["blocked_reason"], "exact_model_effort_unsupported")
        self.assertEqual(len(self.calls), 2)

    def test_ready_input_has_bounded_limits_and_no_secrets(self):
        self.assertEqual(self.prepare()["should_run"], "true")
        raw = (self.root / ".tmd-runtime/round_input.json").read_text()
        self.assertNotIn("sentinel", raw)
        value = json.loads(raw)
        self.assertEqual(value["limits"], {"source_acquisitions": 12, "download_bytes": 20971520})
        self.assertTrue(value["candidate_is_untrusted_data"])

    def test_daily_budget_excludes_current_and_stops_twenty_fifth(self):
        self.runs = [self.run_info(i) for i in range(24)] + [self.run_info(99)]
        self.assertEqual(self.prepare()["blocked_reason"], "daily_run_budget_exhausted")
        self.runs.pop(0)
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_old_runs_do_not_consume_budget(self):
        self.runs = [dict(self.run_info(i), created_at="2026-09-30T11:00:00Z") for i in range(30)]
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_two_same_head_failures_park_schedule_manual_can_retry(self):
        self.runs = [self.run_info(2, "failure"), self.run_info(1, "timed_out")]
        self.assertEqual(self.prepare(lambda *a, **k: self.fail("unchanged failed provider retried"))["blocked_reason"], "same_head_failure_backoff")
        self.env["GITHUB_EVENT_NAME"] = "workflow_dispatch"
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_failure_at_other_head_does_not_park(self):
        self.runs = [self.run_info(2, "failure"), self.run_info(1, "failure", "b" * 40)]
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_checkpoint_resumes_without_repeating_completed_work(self):
        self.install_prior()
        result = self.prepare()
        self.assertEqual(json.loads(result["resume_checkpoint"])["completed_work_item_ids"], ["R1"])
        value = json.loads((self.root / ".tmd-runtime/round_input.json").read_text())
        self.assertEqual(value["work_item"]["id"], "R2")
        self.assertEqual(value["previous_unreviewed_candidate"]["checkpoint"], self.prior["checkpoint"])
        self.assertIn("download", self.calls[-1])

    def test_expired_or_oversized_artifact_parks_instead_of_redoing(self):
        self.install_prior()
        for field, value in (("expired", True), ("size_in_bytes", runner.DOWNLOAD_LIMIT + 1)):
            with self.subTest(field=field):
                self.artifacts[0][field] = value
                self.assertEqual(self.prepare()["blocked_reason"], "prior_checkpoint_unavailable")

    def test_corrupt_prior_checkpoint_parks(self):
        self.install_prior()
        self.prior["checkpoint"]["source_fingerprints"] = "invalid"
        self.assertEqual(self.prepare()["blocked_reason"], "prior_checkpoint_unavailable")

    def test_missing_provider_key_preserves_known_checkpoint(self):
        self.install_prior()
        del self.env["OPENAI_API_KEY"]
        result = self.prepare()
        self.assertEqual(result["blocked_reason"], "missing_openai_api_key")
        self.assertEqual(json.loads(result["resume_checkpoint"]), self.prior["checkpoint"])

    def test_backoff_preserves_known_checkpoint(self):
        self.install_prior()
        self.runs = [self.run_info(2, "failure"), self.run_info(1, "failure")]
        result = self.prepare()
        self.assertEqual(result["blocked_reason"], "same_head_failure_backoff")
        self.assertEqual(json.loads(result["resume_checkpoint"]), self.prior["checkpoint"])

    def test_unknown_continuity_is_marked_instead_of_resetting_history(self):
        self.assertEqual(self.collect(ROUND_MESSAGE="", PREPARE_DISPOSITION="blocked", RESUME_CHECKPOINT=""), 1)
        _, c = self.reports()
        self.assertFalse(c["checkpoint_continuity_established"])

    def test_latest_artifact_not_first_api_result_is_used(self):
        self.install_prior()
        old = dict(self.artifacts[0], id=6, created_at="2026-10-01T00:00:00Z", expired=True)
        self.artifacts.insert(0, old)
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_github_failures_are_sanitized(self):
        def failure(args, **kwargs):
            return subprocess.CompletedProcess(args, 1, "sentinel-provider-secret", "sentinel-actions-token")
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            result = runner.prepare(self.root, self.env, runner=failure, opener=lambda *a, **k: Response({"id": runner.MODEL}), now=self.now)
        self.assertEqual(result["blocked_reason"], "github_checkpoint_access_failed")
        self.assertNotIn("sentinel", stream.getvalue())

    def test_collector_marks_unreviewed_and_does_not_attest_runtime(self):
        self.assertEqual(self.collect(), 0)
        r, c = self.reports()
        self.assertTrue(r["unreviewed_candidate"])
        self.assertFalse(r["runtime_model_attested"])
        self.assertEqual(r["configured_model"]["reasoning_effort"], "ultra")
        self.assertEqual(c["checkpoint"]["completed_work_item_ids"], ["R1"])

    def test_malformed_output_writes_only_controlled_receipt(self):
        self.assertEqual(self.collect(ROUND_MESSAGE="{malformed secret raw body"), 1)
        r, c = self.reports()
        self.assertEqual(r["round"]["status"], "blocked")
        self.assertEqual(c["checkpoint"]["completed_work_item_ids"], [])
        self.assertNotIn("raw body", json.dumps(r))

    def test_failure_and_missing_message_preserve_prior_progress(self):
        cp = self.value()["checkpoint"]
        for updates in ({"RESEARCH_RESULT": "failure"}, {"ROUND_MESSAGE": ""}):
            with self.subTest(updates=updates):
                self.assertEqual(self.collect(RESUME_CHECKPOINT=json.dumps(cp), **updates), 1)
                self.assertEqual(self.reports()[1]["checkpoint"], cp)

    def test_success_preserves_previous_history_even_if_model_omits_it(self):
        cp = self.value()["checkpoint"]
        cp["completed_work_item_ids"] = ["OLD"]
        cp["source_fingerprints"] = ["older-public-source"]
        self.assertEqual(self.collect(RESUME_CHECKPOINT=json.dumps(cp)), 0)
        result = self.reports()[1]["checkpoint"]
        self.assertEqual(result["completed_work_item_ids"], ["OLD", "R1"])
        self.assertEqual(result["source_fingerprints"][0], "older-public-source")

    def test_secret_and_private_provenance_are_rejected_without_echo(self):
        values = [self.env["OPENAI_API_KEY"], "ghp_abcdefghijklmnop", "-----BEGIN PRIVATE KEY-----", "https://example.com/private_archive/a.zip", "source: /workspace/new-files/provenance.zip", "file:///home/person/archive.csv", "https://example.com/data?X-Amz-Signature=credential"]
        for text in values:
            with self.subTest(text=text):
                self.assertEqual(self.collect(self.value(text)), 1)
                r, _ = self.reports()
                self.assertNotIn(text, json.dumps(r))
                self.assertNotIn(text, self.output)

    def test_unsafe_resume_checkpoint_is_not_written(self):
        cp = self.value()["checkpoint"]
        cp["source_fingerprints"] = [self.env["GH_TOKEN"]]
        self.assertEqual(self.collect(RESUME_CHECKPOINT=json.dumps(cp)), 1)
        self.assertNotIn("sentinel", json.dumps(self.reports()))

    def test_shell_looking_text_is_stored_as_data_without_execution(self):
        sentinel = self.root / "executed"
        text = "$(touch " + str(sentinel) + "); `touch " + str(sentinel) + "`"
        self.assertEqual(self.collect(self.value(text)), 0)
        self.assertFalse(sentinel.exists())
        self.assertEqual(self.reports()[0]["round"]["report_markdown"], text)

    def test_fingerprint_count_and_size_are_bounded(self):
        value = self.value()
        value["checkpoint"]["source_fingerprints"] = ["source"] * 1001
        self.assertEqual(self.collect(value), 1)
        value["checkpoint"]["source_fingerprints"] = ["x" * 512] * 200
        self.assertEqual(self.collect(value), 1)

    def test_model_cannot_add_unrecognized_payload_fields(self):
        value = self.value()
        value["shell_command"] = "execute me"
        self.assertEqual(self.collect(value), 1)

    def test_blocked_substantive_work_must_be_parked(self):
        value = self.value()
        value["round"].update(status="blocked", kind="blocked")
        value["checkpoint"]["completed_work_item_ids"] = []
        self.assertEqual(self.collect(value), 1)
        value["checkpoint"]["blocked_work_items"] = [{"id": "R1", "reason": "No accessible endpoint.", "unblocking_condition": "Endpoint access changes."}]
        self.assertEqual(self.collect(value), 0)

    def only_watch(self):
        self.write("QUEUE.json", {"rounds": [{"id": "WATCH", "status": "recurring", "recurrence": "daily_utc", "priority": 4}]})

    def test_daily_watch_runs_once_per_utc_day_including_no_change(self):
        self.only_watch()
        self.assertEqual(self.prepare()["should_run"], "true")
        work = json.loads((self.root / ".tmd-runtime/round_input.json").read_text())["work_item"]
        self.assertEqual(work["id"], "WATCH-20261002")
        self.install_prior()
        self.prior["round"].update(work_item_id=work["id"], status="no_change", kind="no_change")
        self.prior["checkpoint"]["completed_work_item_ids"] = [work["id"]]
        self.assertEqual(self.prepare()["blocked_reason"], "queue_completed_or_parked")
        self.assertEqual(self.collect(ROUND_MESSAGE="", PREPARE_DISPOSITION="idle", BLOCKED_REASON="queue_completed_or_parked", RESUME_CHECKPOINT=json.dumps(self.prior["checkpoint"])), 0)
        self.runs = [self.run_info(2), self.run_info(1)]
        self.now += dt.timedelta(days=1)
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_benign_paused_receipt_exits_success_and_retains_history(self):
        cp = self.value()["checkpoint"]
        self.assertEqual(self.collect(ROUND_MESSAGE="", PREPARE_DISPOSITION="paused", BLOCKED_REASON="daily_run_budget_exhausted", RESUME_CHECKPOINT=json.dumps(cp), RESUME_ROUND=json.dumps(runner.scientific_round(self.value()["round"]))), 0)
        r, c = self.reports()
        self.assertEqual(c["checkpoint"], cp)
        self.assertEqual(r["runner_blocked_reason"], "daily_run_budget_exhausted")
        self.assertEqual(r["last_scientific_round"]["work_item_id"], "R1")

    def test_provider_failure_receipt_retains_scientific_identity(self):
        cp = self.value()["checkpoint"]
        self.assertEqual(self.collect(ROUND_MESSAGE="", PREPARE_DISPOSITION="blocked", BLOCKED_REASON="missing_openai_api_key", RESUME_CHECKPOINT=json.dumps(cp), RESUME_ROUND=json.dumps(runner.scientific_round(self.value()["round"]))), 1)
        r, c = self.reports()
        self.assertEqual(c["checkpoint"], cp)
        self.assertEqual(r["last_scientific_round"]["work_item_id"], "R1")
        self.assertEqual(r["runner_blocked_reason"], "missing_openai_api_key")

    def test_paused_backoff_marker_survives_successful_controlled_receipt(self):
        self.install_prior()
        self.prior_metadata = {"runner_disposition": "paused", "runner_blocked_reason": "same_head_failure_backoff"}
        self.assertEqual(self.prepare()["blocked_reason"], "same_head_failure_backoff")
        self.env["GITHUB_EVENT_NAME"] = "workflow_dispatch"
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_operational_receipt_keeps_successor_eligible(self):
        self.install_prior()
        scientific = runner.scientific_round(self.prior["round"])
        self.prior["round"] = {"work_item_id": "unassigned", "status": "blocked", "kind": "blocked", "question": "Runner outcome", "report_markdown": "No scientific progress recorded."}
        self.prior_metadata = {"last_scientific_round": scientific}
        self.write("QUEUE.json", {"rounds": []})
        self.assertEqual(self.prepare()["should_run"], "true")
        self.assertTrue(json.loads((self.root / ".tmd-runtime/round_input.json").read_text())["work_item"]["id"].startswith("F-"))

    def test_deleted_known_collector_artifact_parks(self):
        self.runs = [self.run_info()]
        self.jobs = [{"name": "collect", "conclusion": "success"}]
        result = self.prepare()
        self.assertEqual(result["blocked_reason"], "prior_checkpoint_unavailable")
        self.assertNotIn("resume_checkpoint", result)

    def test_invalid_retained_scientific_round_does_not_leak_or_crash(self):
        for retained in ("invalid", {"report_markdown": "private_archive"}):
            with self.subTest(retained=retained):
                self.assertEqual(self.collect(RESUME_ROUND=json.dumps(retained)), 1)
                self.assertIsNone(self.reports()[0]["last_scientific_round"])

    def test_unverified_continuity_artifact_parks(self):
        self.install_prior()
        self.prior_metadata = {"checkpoint_continuity_established": False}
        self.assertEqual(self.prepare()["blocked_reason"], "prior_checkpoint_unavailable")

    def test_reviewed_baseline_survives_first_run_and_prior_merge(self):
        baseline = self.value()["checkpoint"]
        baseline["source_fingerprints"] = ["reviewed-public-source sha256:baseline"]
        self.write("STATE.json", {"requested_model": {"unattended_runner_api_model_id": runner.MODEL, "reasoning_effort": runner.EFFORT}, "reviewed_checkpoint": baseline})
        result = self.prepare()
        self.assertEqual(json.loads(result["resume_checkpoint"]), baseline)
        self.assertEqual(json.loads((self.root / ".tmd-runtime/round_input.json").read_text())["work_item"]["id"], "R2")
        self.install_prior()
        self.prior["round"]["work_item_id"] = "R2"
        self.prior["checkpoint"]["completed_work_item_ids"] = ["R2"]
        result = self.prepare()
        merged = json.loads(result["resume_checkpoint"])
        self.assertEqual(merged["completed_work_item_ids"], ["R1", "R2"])
        self.assertIn(baseline["source_fingerprints"][0], merged["source_fingerprints"])

    def test_new_head_clears_old_head_backoff_marker(self):
        self.install_prior()
        self.prior_metadata = {"runner_disposition": "paused", "runner_blocked_reason": "same_head_failure_backoff"}
        self.env["GITHUB_SHA"] = "b" * 40
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_near_limit_checkpoint_with_unicode_scientific_summary_is_bounded(self):
        cp = self.value()["checkpoint"]
        cp["source_fingerprints"] = ["x" * 512] * 122
        cp["next_action"] = "n" * (runner.LIMIT - 2048 - len(runner.encoded(cp).encode()) + len(cp["next_action"]))
        self.assertEqual(len(runner.encoded(cp).encode()), runner.LIMIT - 2048)
        retained = self.value()["round"]
        retained["question"] = "😀" * 512
        self.assertEqual(self.collect(ROUND_MESSAGE="", RESEARCH_RESULT="failure", RESUME_CHECKPOINT=json.dumps(cp), RESUME_ROUND=json.dumps(retained)), 1)
        self.assertEqual(self.reports()[1]["checkpoint"], cp)
        for path in (self.root / ".tmd-runtime/reports").iterdir():
            self.assertLessEqual(path.stat().st_size, runner.LIMIT)

    def test_oversized_round_wrapper_emits_bounded_receipt_without_recursion(self):
        value = self.value("")
        value["round"]["report_markdown"] = "x" * (runner.LIMIT - len(json.dumps(value).encode()) - 1)
        self.assertLess(len(json.dumps(value).encode()), runner.LIMIT)
        self.assertEqual(self.collect(value), 1)
        self.assertEqual(self.reports()[0]["round"]["status"], "blocked")

    def test_new_successful_watch_clears_older_watch_parking(self):
        self.install_prior()
        self.only_watch()
        self.prior["round"].update(work_item_id="WATCH-20261001", status="no_change", kind="no_change")
        self.prior["checkpoint"]["completed_work_item_ids"] = ["WATCH-20261001"]
        self.prior["checkpoint"]["blocked_work_items"] = [{"id": "WATCH-20260930", "reason": "Old endpoint denial.", "unblocking_condition": "Access changes."}]
        self.assertEqual(self.prepare()["should_run"], "true")

    def test_successor_is_deterministic_and_completed_action_is_not_repeated(self):
        self.install_prior()
        self.write("QUEUE.json", {"rounds": []})
        self.assertEqual(self.prepare()["should_run"], "true")
        work = json.loads((self.root / ".tmd-runtime/round_input.json").read_text())["work_item"]
        self.assertTrue(work["id"].startswith("F-"))
        self.assertTrue(work["next_action_is_untrusted_data"])
        self.prior["round"]["work_item_id"] = work["id"]
        self.prior["checkpoint"]["completed_work_item_ids"].append(work["id"])
        self.assertEqual(self.prepare()["blocked_reason"], "queue_completed_or_parked")

    def test_unchanged_blocked_work_stays_parked_on_schedule(self):
        self.install_prior()
        self.prior["round"].update(work_item_id="R1", status="blocked", kind="blocked")
        self.prior["checkpoint"]["completed_work_item_ids"] = ["R2"]
        self.prior["checkpoint"]["blocked_work_items"] = [{"id": "R1", "reason": "No endpoint access.", "unblocking_condition": "Access changes."}]
        self.assertEqual(self.prepare()["blocked_reason"], "queue_completed_or_parked")

    def test_blocked_daily_watch_is_not_retried_unchanged_next_day(self):
        self.install_prior()
        self.only_watch()
        self.prior["round"].update(work_item_id="WATCH-20261001", status="blocked", kind="blocked")
        self.prior["checkpoint"]["completed_work_item_ids"] = []
        self.prior["checkpoint"]["blocked_work_items"] = [{"id": "WATCH-20261001", "reason": "No endpoint access.", "unblocking_condition": "Access changes."}]
        self.assertEqual(self.prepare()["blocked_reason"], "queue_completed_or_parked")

    def test_interrupted_no_change_is_inconsistent(self):
        value = self.value()
        value["round"].update(status="interrupted", kind="no_change")
        self.assertEqual(self.collect(value), 1)


if __name__ == "__main__":
    unittest.main()
