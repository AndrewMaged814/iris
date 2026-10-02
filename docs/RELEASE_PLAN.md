# Finish Iris: one decision, one verified action

Decision plan, 2 October 2026. This is a proposed release scope, not a claim that the live workflow has passed.

Implementation update: the owner prioritized recommendation quality before the offer demo.
The shared recommendation process is now deployed and has isolated behavioral checks; see
[current status](STATUS.md#recommendation-update--2-october-2026). Next is the owner's live
Telegram test. The offer execution and recording gates below remain separate, unfinished work.

**Next: finish the market-to-action experience, then package and film it.** Composio gives Iris reach; the demo must show what that reach accomplishes for one owner. Finishing remains the primary goal. Novelty is not a release gate.

Definition of done: **A 2–3 minute video shows Iris turn sourced competitor evidence and the owner's confirmed product economics into one owner-requested response offer, verify it in a connected demo store, produce a usable announcement, and recall the chosen action in a later session; the repository accurately documents that tested release.**

Out of scope: new dashboards, new Iris tools/scripts, custom app adapters or approval bridges, autonomous repricing/publishing, additional categories, connector-count demonstrations, Reddit trend analysis, order analytics, multi-owner support, generated campaign images, new branding, and claimed sales lift.

## Diagnosis

- At planning time, the offer comparison and contribution arithmetic were tested in separate examples. The public [demo page](DEMO.md) now shows one connected decision, while the owner-requested app action and readback remain to be demonstrated.
- `docs/STATUS.md` records connected Sheets and Reddit reads, but no verified live Composio write and no owner-confirmed catalog. Connection is not completed onboarding or a tested action.
- Existing `draft-move`, setup, memory and weekly-brief instructions already describe most of the desired experience. Change them only where a rehearsal exposes a failure. Preserve Hermes and direct Composio.
- The earlier [prior-art decision](research/IRIS_FEATURE_PRIOR_ART.md) already selected market evidence → decision → requested commerce action. Finish that experience through the current integration rather than reopen feature selection.
- Presentation has drifted: README says four tools and 96 tests; the plugin exposes three and this audit ran 59. The README's next-step text describes removed offer controls. The architecture SVG still centers Shopify. Setup documents two scheduled jobs, while `setup_jobs.sh` creates three including the offer check.
- Most experimental local clutter is under ignored `output/`, with no files there listed by `git ls-files`. Tracked research and historical evaluations are the separate public-repo cleanup problem.

## 1. Prove the final action before polishing

Use Mira Nile, one sunscreen SKU and one owner. Keep costs/catalog in the confirmed source, using the already connected Sheets account if the owner selects it. Use a separate demo commerce store for the offer; Shopify is the first candidate because the existing story already uses it. Do not edit a real merchant's prices or offers during rehearsal.

1. In Telegram, select and confirm the exact catalog, product, currency, costs and stock meanings. Verify saved source/profile recall in a fresh session. Preload only owner-confirmed context; do not script replies.
2. Through native Composio, discover the commerce toolkit and schemas, connect the intended demo account, and check support for creating, reading and deactivating one product-specific discount code. Confirm the product exists and matches the catalog. Do not assume connector availability proves these operations.
3. Settle the supported offer terms: product, discount, dates, eligibility, redemption limit and stacking behavior. Use a simple discount, not multi-buy creation. Establish a minimum acceptable per-item contribution from owner inputs.
4. Have the owner request those exact terms. Create once, read the saved terms back, open the resulting offer in the app, then deactivate it and verify that state. If supported by the demo platform, check an eligible and an ineligible basket as well; an admin record alone does not prove checkout behavior.
5. Save the private evidence: requested terms, returned record, independent readback, app screenshot, cleanup result and actual turn times. Exclude credentials and account/customer data from public artifacts.

**Gate:** creation, readback and deactivation must work through the actual Telegram agent. If an operation is unsupported, this is a capability blocker to resolve before promising or filming it. Do not rebuild the removed bridge or quietly substitute a spreadsheet row and call it an active offer.

Specific dependency found in research: [Composio's Shopify toolkit](https://docs.composio.dev/toolkits/shopify) lists discount operations but says Composio-managed OAuth is unavailable. Check whether the existing native Connect flow can authorize the demo store before implementation. Keep credential handling with the provider's supported connection flow; no Iris token/client code. If this native path cannot support Shopify, revise the release decision explicitly rather than spending the release on an integration project.

Use native authorization controls already available in Hermes. The current status explicitly says the public bot exposes shared app reads/writes, while owner recognition is prompt-based. For this recorded release, use an owner-restricted demo profile with demo accounts; do not publish an unrestricted write-capable bot as the try-it link. This does not require multi-owner engineering.

## 2. Rehearse one coherent conversation

**Hook:** “Forward a competitor's offer. Iris works out your response—and carries it out when you ask.”

Use an owner-forwarded product link or screenshot as the trigger. This is repeatable without inventing a spontaneous market change. A proactive alert can replace it only if a real recorded change and actual delivery are captured.

The conversation must contain:

1. A fresh first-party competitor observation with its source and check date.
2. The surprising fact that affects the decision: basket economics, offer eligibility or a genuine availability difference. Never assume an advertised bundle is eligible or that different products are equivalent.
3. One feasible response using the owner's actual confirmed cost inputs. A discount does not have to beat the competitor; Iris must explain its narrower purpose and remain within the owner's contribution floor. If no discount makes sense, say so and choose a different honest recording case rather than force a bad recommendation.
4. One short request to execute settled terms, followed by the verified app action.
5. A requested Egyptian Arabic announcement using only supported facts and verified offer terms.
6. A chosen-action memory entry with status, success measure and review date; a fresh session must recall it without asking the owner to repeat everything. No made-up result.

The EGP360 / buy-two-get-two example in the old demo is historical. Later repository evidence reported a different price and missing multi-buy. Re-read the original page and reconcile current evidence before using any of those numbers. An explicitly labeled historical screenshot is acceptable evidence of an old offer, not a current offer or newly detected change.

Polish the existing skills/SOUL only when rehearsal exposes an issue: unnecessary questions, overlong answers, unsupported matching, repeated demo caveats, or premature success claims. Keep Iris's normal answer near its existing 70-word target and make the app destination easy to open. No new orchestration framework.

**Rehearsal acceptance:** complete twice in fresh conversations; record response times and every manual correction. Verify no duplicate write on a repeated/failure-recovery turn. If creation status is uncertain, read before retrying. Check that a readback mismatch produces an unresolved result rather than a success claim. Run these checks only against the demo account.

Also verify one actual scheduled check and Telegram delivery under the current Composio setup, plus a quiet/no-new-facts check. Existing offline tests and historical transport evidence do not establish the current live path. Use native job management and existing jobs; do not rerun setup to create duplicates.

## 3. Clean the release surface

Do this after the workflow passes so the docs describe demonstrated behavior.

| Surface | Planned change |
| --- | --- |
| `README.md` | Lead with the hook, a short video/GIF preview and three steps: observe, decide, act. Keep a compact setup link and architecture. Fix tool/test counts and remove obsolete next-step/approval claims. Describe Composio's breadth as potential, separate from workflows verified in Iris. |
| `docs/DEMO.md` | Replace the disconnected examples with the exact recording runbook, prerequisites, current evidence and expected visible results. |
| `docs/STATUS.md` | Keep one current verified/unverified checklist, including test/runtime revision and live action/transport evidence. |
| `docs/EVALUATION.md` | Replace the chronological development diary with the current release acceptance matrix. Preserve useful historical evidence outside the public release tree or in Git history. Do not imply removed tests prove current behavior. |
| `docs/SETUP.md`, `docs/TESTING.md` | Keep reproducible current install/verification instructions; fix the three-job discrepancy and demonstrate a fresh-profile setup without overwriting the live profile. Link to current evidence rather than historical controls. |
| `docs/HANDOFF_ANY_STORE.md`, `docs/research/` | Remove obsolete handoff and superseded exploration from the final public tree after a recoverable checkpoint. Retain only research needed to explain a current decision, linked from the plan. Check inbound links before removal. |
| `assets/architecture.svg`, `.png`, `assets/README.md` | Replace the obsolete diagram with one small README Mermaid diagram: Telegram → Hermes/Iris → native Composio + native web research + Iris watch history. Remove redundant diagram exports if unused. Keep the existing mascot and credit. |
| `output/` | Keep out of Git. Inventory and privately archive valuable reports before deleting scratch downloads/build outputs. Never upload this directory to make the repo look complete. |
| Runtime, fixtures and tests | Keep used files. Shopify/WooCommerce fixtures still test public competitor readers; their names do not make them obsolete app clients. Retain `_iris_paths.py` and delivery reconciliation. Do not simplify functioning code for cosmetic file-count reduction. |

Preserve the substantial pre-existing working changes. Separate the runtime/rehearsal fixes from documentation cleanup in reviewable commits. Check the actual staged/public diff for private data; the existing validator passes but is not a comprehensive secret/history audit. Confirm repository visibility and usable viewer links before calling the release public.

## The 2:40 recording

| Time | Screen and story |
| --- | --- |
| 0:00–0:12 | Telegram and the competitor offer: “My competitor just launched this. Should I respond?” Start with the business problem. |
| 0:12–0:40 | Iris reads the offer and the confirmed catalog/cost source. Show the single fact that changes the decision, with evidence. |
| 0:40–1:05 | Iris recommends one bounded response and states what the owner keeps per item. Show the tradeoff, not a lengthy analysis. |
| 1:05–1:40 | Owner requests the exact offer. Iris executes and reads it back. Cut to the actual commerce app showing matching terms. This is the main reveal. |
| 1:40–2:05 | Request the announcement; show concise usable Egyptian Arabic copy with the actual offer terms. |
| 2:05–2:25 | Clearly labeled later/fresh session: “What did we decide?” Iris recalls the action and its agreed review measure. Unknown outcomes stay unknown. |
| 2:25–2:40 | Closing frame: “Your market moves. Iris helps you respond.” Brief Hermes + Composio credit and working repository link. |

Record real interactions; edit out waiting with visible cuts and disclose condensed timing. Do not imply the edit demonstrates end-to-end latency. Record app authorization beforehand; a long OAuth flow is not the hook. Show only the apps used in the story. If the scheduled follow-up is not yet observed, do not present a manual session as autonomous delivery.

## Release gate and stopping point

- Offline suite and validator pass after changes; record counts from the run rather than old copy.
- Current Telegram path proves catalog recall, evidence, exact requested write, readback and deactivation; no obsolete enforced-approval claims.
- Actual scheduled delivery and no-new-facts behavior checked; later-session action recall checked separately.
- One complete rehearsal produces correct output without manual data repair; a second fresh-session run repeats the result.
- Video is under three minutes, readable on a phone and truthful about demo data, historical evidence, cuts and later sessions.
- README, setup, diagram, status and video tell the same current story; links work for the intended audience.

Stop adding features when these pass. The next learning step is one merchant trying one action and reporting whether it saved work, not another pre-release feature cycle.

Audit verification on 2 October: `python -m unittest discover -s tests` passed **59 tests**; `python tools/validate_repo.py` returned `ok`. `python3` is not registered on this Windows host, so the installed Python 3.12 `python` command was used. No live app writes, deployment, deletion or video recording were performed in this planning pass. Research sources: [release research](research/RELEASE_RESEARCH.md).
