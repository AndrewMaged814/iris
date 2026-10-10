# Testing Iris

## Local contracts

```sh
python -m unittest discover -s tests
python tools/validate_repo.py
git diff --check
```

The suite needs no network, model or credentials. It checks product reads, variant-price
ambiguity, currency-safe changes, persistence, delivery reconciliation, source snapshots,
search-result reuse, calculations and native plugin registration. It also checks the
recorded failed-model/retry trace. These contracts do not establish answer quality.
Install the reader dependencies listed in [setup](SETUP.md#product-reader-dependencies),
plus `PyYAML` and `python-dotenv` for doctor checks, on a bare Python installation.
GitHub Actions runs these same checks on pushes and pull requests.

## Native behavior evaluations

`tools/evaluate_iris.py` uses Hermes's native chat entry point and the profile's configured
model/tools. `--isolate` copies the installed profile, removes its Telegram delivery token,
uses a separate database/memory directory and the documented `evaluation` tracing environment.
A follow-up shares its case conversation; a `fresh_session` turn tests memory without the
previous transcript. Independent cases reset memory to the copied owner's starting notes.

Use the Python environment running Hermes, with access to its CLI:

```sh
HERMES_LANGFUSE_CAPTURE=metadata python tools/evaluate_iris.py \
  --profile-home ~/.hermes/profiles/iris --isolate \
  --candidate-from PATH_TO_IRIS --output PRIVATE_UNUSED_DIRECTORY \
  --cases sme-natural-overview-and-stock sme-market-brief-journey
```

The first case checks greeting → casual overview → explicit detailed briefing → product
availability → recall → correction of a mistaken sold-out assumption. It uses saved watch
history and supplied product facts. The second uses the staged connected catalog and current
public pages for three businesses/two product families, then investigates Infinity,
prioritizes, drafts on request, saves a chosen move and recalls it in a fresh session.
The roster in [market_brief.json](../tools/fixtures/market_brief.json) supplies research targets,
not predetermined conclusions. Both cases are private rehearsals, not merchant outcomes.

Other useful cases include `sme-position-then-advice`, `sme-basket-quantity`,
`comparison-format-unknown` and `sme-owner-decision-loop`. Use `--cases` to select only the
behavior affected by a change. Review final replies and their source/tool arguments manually.
An exit code of zero is completion, not a factual pass. Do not run write cases on real apps.

## Reproduce composition separately from retrieval

A private snapshot keeps actual extracted pages, hashes, timestamps and bounded connected
catalog fields with their original JSON paths. Credentials and failed reads are excluded.
Missing fields remain unknown. Never publish the raw snapshot.

```sh
python tools/report_iris_cases.py --root PRIVATE_EVALUATIONS --pattern RUN_NAME \
  --snapshot-output PRIVATE_PACKET.json
python tools/evaluate_iris.py --profile-home ~/.hermes/profiles/iris --isolate \
  --output PRIVATE_UNUSED_DIRECTORY --snapshot-input PRIVATE_PACKET.json \
  --cases sme-market-brief-snapshot-1 sme-market-brief-snapshot-2 sme-market-brief-snapshot-3
```

The evaluator validates content/field hashes and records the whole packet hash. Frozen
cases forbid fresh retrieval and isolate interpretation; pair them with current-source
runs before accepting a runtime change. Three samples are not a general accuracy rate.

## Native dispatch and Cloud readback

On the Hermes host, with its repository on `PYTHONPATH`:

```sh
python tools/check_research_hooks.py --profile-home PRIVATE_PROFILE
python tools/check_workflow_cloud.py --profile-home ~/.hermes/profiles/iris \
  --baseline PRIVATE_BASELINE/results.json --candidate PRIVATE_CANDIDATE/results.json \
  --output PRIVATE_UNUSED_CLOUD_REPORT.json
```

The hook check mocks only network-provider execution. Real native discovery, hooks,
dispatch and calculation handlers run. It verifies distinct queries, completed-result reuse,
new-turn scope and failed-search retry. It does not test retrieval quality.

The Cloud checker groups resumed turns by session and compares successful generations with
native `api_calls`. Failed attempts are listed separately; empty failure usage is unknown.
Known failure usage is retained. It compares roots/tools and reported totals with canonical
token buckets; a mismatch remains visible. It records environments, not provider charges.
Its bounded readback covers the last six hours and refuses truncated
responses. `check_workflow_cloud.py` retains its existing operator filename; the retired
workflow engine is no longer shipped.

## Publishable evidence and live verification

```sh
python tools/report_iris_cases.py --root PRIVATE_EVALUATIONS --pattern RUN_NAME \
  --json-output REVIEW.json
```

This export omits app payloads, arguments, memory and raw transport output. Questions and
replies still require a privacy review before publication. Keep source evidence private.
The citation review flags links without a captured read in that conversation; it preserves
variant query strings and resets read coverage on fresh sessions. It does not judge whether
a read supports the claim. Failed and empty extraction results are labeled in new native traces.
See [the evidence ledger](EVALUATION.md) for completed runs and failures.

Before updating live Iris, back up affected files and SQLite state; preserve configuration,
OAuth, owner identity, memories and job IDs. Verify copied hashes, native tool inventory,
owner-only Telegram controls and gateway health. Private CLI runs exercise the agent; only
actual Telegram replies establish the owner's received experience. See [setup](SETUP.md).
