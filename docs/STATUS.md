# Status

## Built and tested offline

- Four read-only tools; Shopify, WooCommerce and JSON-LD page reading; honest block reporting.
- Change signals (new product, sale started/ended, price move ≥5%/≥10%, out of/back in stock, removed),
  with urgency limited to the owner's product types.
- Daily check with the `{"wakeAgent": false}` gate and acknowledgement after confirmed delivery;
  persistent warning after 3 failed checks. Unknown sends are held for operator investigation.
- Weekly data collection. SOUL, four skills, validator, doctor, CI. 61 tests, no network.
- Exact product links return that product with description and page evidence for advertised offers.
- Market history includes successful-check coverage so Iris can distinguish a baseline from a quiet week.
- Chat and scheduled briefs share dated evidence, source URLs and profile-local timestamps.
- Product review reads image/alt metadata, descriptions, variant prices and availability; no store edits.
- Owner-confirmed actions and reported results use native Hermes memory and the existing weekly brief.
- Profile-scoped store credentials and data paths; quoted environment settings checked by the doctor.

## Verified on the host (2026-09-30)

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
