# Model and recurring-run support evidence

Checked 1 October 2026 (America/Los_Angeles; 2 October UTC). This memo reports documentation and metadata checks. No API inference was requested, no recurring runner was activated, and no secrets were copied.

## Exact requested model

The official Codex 0.160.0 source catalog identifies model slug `gpt-6.1-sol`, display name `GPT-6.1-Sol`, `supported_in_api: true`, and the `ultra` effort in `supported_reasoning_levels`. These are observed public source fields, not an inferred mapping from a ChatGPT product label. The source declaration does not establish availability under an individual provider API account or its quota.

Immutable source: https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/models-manager/models.json

The official release `rust-v0.160.0`, published 1 October 2026, dereferences to that source commit: https://github.com/openai/codex/releases/tag/rust-v0.160.0

The locally saved `codex_model_metadata_0_160_0.json` retains metadata for all 11 models in the catalog, with `model_messages` and `guardian` omitted because recurring-run model validation does not need model instructions or guardian configuration. The original response SHA-256 and metadata SHA-256 are in `automation_support_manifest.json`. The original catalog SHA is provenance evidence; the metadata file is a filtered derivative.

Both official npm packages `@openai/codex` and `@openai/codex-responses-api-proxy` reported current version `0.160.0` in read-only registry metadata checks. No package was installed during this review. Package pages: https://www.npmjs.com/package/@openai/codex and https://www.npmjs.com/package/@openai/codex-responses-api-proxy

Public protocol source explicitly handles `ultra`: https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/protocol/src/openai_models.rs

## Valid official action configuration

The dereferenced official `openai/codex-action@v1` commit is `86365089eb2b84e0a8fb0717b304f8bdcb13b20e`. Its action definition supports `openai-api-key`, `prompt-file`, `output-file`, `working-directory`, `model`, `effort`, `codex-version`, `codex-args`, `permission-profile`, and `safety-strategy`.

Definition: https://github.com/openai/codex-action/blob/86365089eb2b84e0a8fb0717b304f8bdcb13b20e/action.yml

Documentation: https://github.com/openai/codex-action/blob/86365089eb2b84e0a8fb0717b304f8bdcb13b20e/README.md

Use a disposable Linux GitHub-hosted runner, `safety-strategy: drop-sudo`, `permission-profile: ":workspace"`, `codex-version: "0.160.0"`, `model: gpt-6.1-sol`, and `effort: ultra`. `codex-args: '["--ephemeral", "--search"]'` is documented as a supported safe argument form. Native `--search` supplies live web search; the workspace permission profile does not allow arbitrary direct shell networking. Retrieve pinned research dependencies and run required preflight checks before Codex begins.

`permission-profile` is an action input that sets the CLI `default_permissions` configuration. It is not evidence that `codex exec --permission-profile` is a supported global CLI flag. The action rejects simultaneous `permission-profile` and legacy `sandbox` inputs. `safety-strategy: read-only` should not be combined with a permission profile; use `drop-sudo` and `permission-profile: ":read-only"` for a read-only report if all required checks work under that profile.

The action exposes `final-message` directly as a step output after a successful `codex exec`. Pass it to a separate report job through a job output and an environment variable, then serialize it with a language library. Do not interpolate model text into shell source. Keep only an original public-source report as the artifact, rather than uploading the whole checkout or runner directory.

Official recommendation: run the Codex action as the last step in its job. This is a documented security recommendation, not a mandatory workflow parser rule. A separate job receives the final message without depending on files or hooks that the model could alter in the model job. See: https://github.com/openai/codex-action/blob/86365089eb2b84e0a8fb0717b304f8bdcb13b20e/docs/security.md

Verified additional action pins:

- `actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09` (`v5`). Set `persist-credentials: false`.
- `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02` (`v4`).

Keep the model job's GitHub permissions at `contents: read`. It should receive no GitHub write token, Zenodo token, private archive, or copied ChatGPT credential. Preflight code can consume the provider secret only in the trusted preflight step. The Codex action forwards its API credential through its protected Responses proxy.

## Provider validation and secure prerequisites

The action documentation requires a provider API key stored as a GitHub Actions secret. The cloud chat's injected GitHub proxy authentication and ChatGPT subscription login do not provision that separate secret.

A trusted preflight can check the exact configured slug using authenticated provider `GET /v1/models` (or `GET /v1/models/gpt-6.1-sol`) and require a returned matching ID, without printing the credential or response headers. OpenAI model-list endpoints generally prove IDs, not reasoning-effort support. Therefore combine the account-specific model-ID check with the pinned source declaration for `ultra`, and invoke the exact model and effort. Treat any runtime provider rejection as failure; never select a default or lower-effort fallback and label it the requested model.

Public model endpoint reference: https://platform.openai.com/docs/api-reference/models

The Codex app-server `model/list` protocol returns `model`, `displayName`, and `supportedReasoningEfforts`, with cursor-based pagination. It does **not** expose a `supportedInApi` field in its public response schema. Internal model presets have `supported_in_api`, and API authentication filters use it. App-server metadata may be bundled or cached depending on discovery configuration, so mere listing should not be reported as proof of a fresh provider acceptance.

Protocol: https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/app-server-protocol/schema/json/v2/ModelListResponse.json

Discovery/cache behavior: https://github.com/openai/codex/blob/a956835d020762cb2b570053af06f643a11c0ecc/codex-rs/models-manager/src/manager.rs

Local runner evidence: `/opt/codex/bin/codex --version` reported `codex-cli 0.159.0-alpha.3`; `codex login status` reported a ChatGPT login; the exported variable name `OPENAI_API_KEY` was absent. A metadata-only app-server startup failed because its configured home is read-only and SQLite state could not initialize. It started no thread and made no inference request. This does not prove the requested model is unavailable, and no credential files were read or relocated to work around it.

## Scheduling and scientific review

An hourly cron such as `17 * * * *` creates bounded recurring opportunities across the day. Each run needs a time limit, a single active-run concurrency group, a repository enable switch initially disabled, failure reporting, and API project spending controls. A timeout limits wall-clock duration; it does not by itself enforce an exact monetary budget.

GitHub `schedule` runs only when the workflow is on the default branch, at its latest commit. Queues can be delayed or dropped under high load; avoiding minute zero reduces one documented load hotspot. In a public repository, 60 days without repository activity disables scheduled workflows. Thus an hourly GitHub workflow provides recurring best-effort rounds rather than a guaranteed continuously running 24/7 process.

Official schedule reference: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

Supporting official source: https://github.com/github/docs/blob/main/data/reusables/actions/schedule-delay.md

A workflow included only in a draft research PR is prepared for review and is not yet an active schedule. Activation depends on the established maintainer review and merge workflow, API-secret configuration, explicit enablement, and a successful bounded manual run. Do not auto-merge, deploy the website, publish to Zenodo, or relabel synthetic/check-only outputs as new biological evidence. The scheduled report should use exclusively authorized public sources and retain uncertainties and source provenance.

No callable automation-creation or scheduler tool was exposed in this cloud conversation. A chat task cannot claim to remain an indefinitely running worker after its turn ends. Codex app automations may be an alternative if available to the user, but app scheduling and device/cloud execution requirements were not verified here; no app automation was created.

Original support memo: Ricardo Maldonado, prepared with AI assistance; CC BY 4.0. Official sources retain their own attribution and terms. The saved catalog file is metadata, with vendor model instructions excluded.
