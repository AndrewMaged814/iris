# Status

## Built and tested offline

- Four tools; read-only market discovery plus optional, owner-approved Shopify response codes.
- Change signals (new product, sale started/ended, price move ≥5%/≥10%, out of/back in stock, removed),
  with urgency limited to the owner's product types.
- Daily check with the `{"wakeAgent": false}` gate and acknowledgement after confirmed delivery;
  persistent warning after 3 failed checks. Unknown sends are held for operator investigation.
- Weekly data collection. SOUL, four skills, validator, doctor, CI. 116 tests, no network.
- Exact product links return that product with description and page evidence for advertised offers.
- Market history includes successful-check coverage so Iris can distinguish a baseline from a quiet week.
- Chat and scheduled briefs share dated evidence, source URLs and profile-local timestamps.
- Product review reads image/alt metadata, descriptions, variant prices and availability; no store edits.
- Owner-confirmed actions and reported results use native Hermes memory and the existing weekly brief.
- Profile-scoped store credentials and data paths; quoted environment settings checked by the doctor.
- Offer proposals check Shopify cost, stock, existing discounts and contribution assumptions.
  Creation/deactivation require fresh authenticated native owner confirmation; cron and CLI writes
  fail closed. Exact readback, uncertain-result reconciliation, stale-fact checks and ledger claims
  have offline coverage. Brand language comes from owner preference or an explicit request.

## Any-store continuation (2026-10-02)

- Added owner-confirmed Market profile setup and category references for beauty, fashion,
  electronics, food, home and other products. Comparisons use category-specific confirmed keys
  and units. Unreadable products route to Hermes extraction/browser reads; robots denials stop.
- Doctor checks reader imports, honest browser UA and optional monitor credentials/authenticated
  reachability. Setup documents manual profile-plugin dependency installation on `c1488ac`.
- 116 offline tests pass on Windows and Hermes's Python; repository validation passes. Repository validation passes.
- Real changedetection.io container (`sha256:34df3680db1cbffc45ac1e9c1514bc0507dd0c5b5fde47d1992fe6f14a7b40e4`)
  created/deleted a temporary Infinity product watch with Iris UA configured. Its watch API
  omits native `restock` properties: adapter now reads authenticated cached HTML snapshots
  (`history/latest?html=1`) and returns EGP 360, available true, dated observation.
  Actual monitor request UA verified through httpbin: the full IrisBot/1.0 identifier.
- Native local browser navigate/snapshot returned httpbin's received `IrisBot/1.0` UA. Real
  PluginManager loads Iris and its hook: clicks/private addresses blocked, snapshots allowed.
  Browser actions remain visible in the native inventory but fail at execution through the hook.
  Node, agent-browser and Playwright Chromium were prepared; no fingerprint bypass was used.
- Installed extruct/price-parser into Hermes's Python. Native hook/provider imports pass;
  existing SearXNG service returns HTTP 200 JSON search results. No production profile deployment.
- Candidate doctor live read returned Mira Nile's 6 products, Likemoon 627, Source Beauty 79,
  Deoora 958 and the exact Infinity sunscreen. Infinity's whole catalog was blocked. Doctor
  exit 1 also reflects the intentionally removed Telegram token; this is not deployment readiness.
- Seven isolated native Luna cases completed: four supplied hypothetical category-expansion
  comparisons and three Mira Nile regressions. See EVALUATION for the reviewed limits.
- Missing product types stay `other`: option names/title words alone do not establish a category.
  Iris uses product details and the confirmed Market profile for comparisons.
- Original 30-store measurement discarded its URL manifest, so an exact cohort rerun is not
  reproducible yet. Six reconstructed store URLs were probed; TV-IT now yields a labelled
  sitemap sample. The coverage doc preserves blocks and gaps rather than claiming a 30-store gain.

## Verified on the host (2026-09-30)

- Installed the native SOUL supported-request rule and the existing market skill's scope check.
  The final 30-case / 33-turn Luna matrix observed no unrelated answers or tool calls, including
  Arabic, Arabizi, mixed requests and native resumed follow-ups. Six business regressions still
  completed. No reduced search cap or custom guard framework was added. One discovery result
  was an unpriced official brand page, and arithmetic sometimes triggered unnecessary search;
  these response-quality limits are recorded in [EVALUATION](EVALUATION.md).
- Verified the new policy against a private copy of the existing owner conversation: native
  prompt refresh preserved all 44 prior messages and Luna, and the resumed personal-car request
  returned a redirect with no tool calls. Deployed the same refresh through Hermes's public
  session API for 29 saved prompt snapshots, backed up privately, and stopped/started the
  gateway natively. Live instruction hashes match the candidate; history, model settings,
  credentials, configuration and owner memory were preserved. The gateway is active.
  This is instruction-level scope control; the next actual owner Telegram exchange is separate
  from the private native tests.

- Live response-offer prerequisites now pass: the installed app grants `write_discounts`, and
  the sunscreen's 50 ml variant has owner-approved demo cost EGP 160, 20 tracked units and
  overselling disabled. The owner authorized deactivation of the two existing demo promotions;
  Shopify readback found no active/scheduled discounts. Offers are enabled and Hermes restarted
  gracefully; Luna configuration, credentials and owner memory were preserved. This setup does
  not establish native Telegram approval or successful Iris-created discount execution.
- Two isolated native Luna previews used these live store facts and saved proposals only.
  Both returned EGP288 discounted price, EGP109.36 contribution and 37.97% margin with 3% fee
  and EGP10 extra cost assumptions. A small skill adjustment corrected an unsupported skin-type
  match in the first answer; the rerun stated the unconfirmed attributes separately.

- Response-offer validation: all 92 offline tests passed on Hermes' Python, including fresh
  approval, recovery and implied-scope regressions. Five isolated Luna cases verified English brand
  preference, a one-off Arabic override, English recall from an Arabic prompt, prerequisite
  reporting and denial of approval instructions from competitor content. Fixed Shopify read
  queries passed schema validation and returned expected missing-access errors. The native
  guard denied an enabled unattended apply before any API call, and the question queue rejected
  a stale question ID. No live discount was created or deactivated by these checks.

- Installed verified Shopify feed currencies and the less repetitive demo policy. All 65 offline
  tests pass on the host. Native Luna comparisons use confirmed EGP; a fresh session with the
  owner's saved preference omits routine demo reminders. The old transcript is retained.
- Installed the final distribution as `iris`; removed the two earlier Iris profiles and stopped their
  legacy services after making a private host backup.
- A native Hermes turn returned the expected response using Luna through Azure Foundry.
- The own-store reader returned six synthetic Mira Nile skincare products, priced in EGP.
- Telegram resolves exactly the four Iris tools, web search, vision, memory and skill reads.
  Scheduled runs resolve only the four Iris tools and skill reads; no terminal or store-write tools.
- Hermes' safe web client is importable. Telegram is connected to IrisMarketWatcherBot; an owner message
  and Luna reply are recorded. Seven business cases were run with Luna in isolated native sessions
  using Telegram's toolsets; baseline responses and targeted reruns were captured privately.
  These runs do not verify Telegram transport or continuation of an existing owner conversation.
- Daily (08:00 Cairo) and Sunday (10:00 Cairo) jobs are active. Infinity Clinic Pharma is watched.
  The weekly job completed and recorded Telegram delivery at 03:39 Cairo. The daily job completed
  with a no-wake gate and suppressed delivery at 03:48. The resulting two successful observations
  span about ninety minutes, so a week of changes cannot yet be established.
- The product-review case moved from requesting a screenshot to reading actual image metadata and
  native vision, finding a missing saved alt description. It did not claim a conversion problem.
- Four separate isolated native sessions verified a planned action, weekly follow-up, simulated
  reported result and subsequent recall. Scheduled toolsets could read memory but had no memory write.
  Simulation records and credentials remained in a private test copy; the live owner's memory was preserved.
- Three harder business cases passed: conditional bulk offers, contribution break-even arithmetic
  and unsupported ad claims. The fifteen-case [expected-versus-actual review](EVALUATION.md) retains
  partial results instead of assigning an automatic quality score.
- Eleven isolated native scheduler runs verified generation/transport failure, recovery and quiet
  checks after acknowledgement. Actual script and execution records; simulated model/send boundaries.
- Two native weekly runs before and two after the brief adjustment used actual Luna and local
  output only. Previous output was injected on the second run. The latest pair retained the
  simulated plan and unknown result without a generic draft offer. The initial measure question
  was still omitted, so follow-up wording remains a partial result.
- The updated live weekly job completed with confirmed Telegram delivery at 04:27 Cairo. The
  08:00 daily job completed with suppressed delivery and no error. Both existing jobs now opt
  into native chat mirroring; Hermes' target eligibility was verified. One already-delivered
  weekly report was backfilled through Hermes' mirror into the active Telegram transcript,
  without resending it. Future scheduled mirror delivery and the owner's subsequent reply
  remain separate from this verified backfill.

## Remaining live checks

- A real-owner action through Telegram, follow-up and measured task time or business result. The
  simulation and successful delivery do not prove real SME revenue uplift or time saved.
- Approved Shopify create/readback/deactivate through actual owner Telegram controls. The current
  app has discount-write access and the sunscreen demo prerequisites pass. Creation is enabled
  but still requires the fresh authenticated owner's native approval; this live action remains
  unverified.
- Failure recovery with real provider/Telegram interruptions beyond the injected boundaries;
  resolve uncertain sends manually and recheck native ledger compatibility after Hermes upgrades.
- Consistent first weekly question about the chosen measure, and longer-term retention. The
  short continuity pairs don't establish behavior over successive real weeks.

- `hermes cron create --script` finds the scripts in the profile's `scripts/` folder. (Confirmed in the Hermes
  source: the installer copies every folder listed in `distribution_owned`, and `scripts` isn't a reserved name.)
- `tools.url_safety` is importable in the plugin and in cron script runs (otherwise the basic guard is used).
- Web search results and `display.platforms.telegram.tool_progress: "off"` behave as expected in chat.
- Hermes' own system messages (errors, restarts) are English and technical; plugins can't change them.

- Memory: the owner's name and preferences are saved and come back in a new chat (`/new`).
  Hermes also runs a periodic background memory review; check it never saves text that came from a website.

## Not built (by choice)

Multiple stores per Iris, Meta/Instagram APIs, ad libraries, automatic actions.

## Full goal audit

| Requirement | Current evidence | Remaining proof |
| --- | --- | --- |
| SME can find a revenue opportunity | Public comparisons, stock/offer evidence and action drafts exercised | Real owner validates a feasible opportunity against their product, margin and customers and reports its outcome |
| SME can save time | Listing review removes a screenshot handoff; simulated action reports retained | Timed manual versus Iris-assisted repeated task for a real owner |
| Iris works end to end | Prior inbound Telegram exchanges; live weekly delivery and daily quiet gate; isolated native action memory chain, recovery boundaries and weekly continuity | Updated owner action and follow-up through Telegram; real interrupted transport recovery and longer-term checks |
| Research and useful proactive additions | Sourced SME/commercial-agent brief; listing review and weekly chosen-action follow-up implemented | Pilot feedback on relevance and whether the actions are used |
| Compelling repo and accurate positioning | AI growth scout title, task-led README, dated demo and repository description | Keep proof current as remaining gates pass |

The goal remains active. No real SME uplift, measured time saving or complete updated owner
action conversation has been established by this distribution's current evidence.
