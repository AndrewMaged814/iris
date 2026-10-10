<p align="center">
  <img src="assets/iris-logo.png" alt="Iris mascot" width="144">
</p>

<h1 align="center">Iris</h1>
<p align="center"><strong>Your AI market watcher.</strong></p>
<p align="center">Know what’s changing. See what matters. Make your next move.</p>
<p align="center">Iris brings competitor activity, market research and your store’s context together<br>so you can see the bigger picture and decide what to do—right in Telegram.</p>

<p align="center">
  <a href="docs/DEMO.md">Demo plan</a> ·
  <a href="#what-iris-can-help-you-do">Capabilities</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#observability">Observability</a> ·
  <a href="#whats-next">What’s next</a> ·
  <a href="docs/SETUP.md">Setup</a>
</p>

## Close the gap between your business and your market

You know your store. Keeping up with everything around it takes another kind of work:
checking competitors, comparing offers, following availability and figuring out which
signals deserve your attention.

Iris is your market analyst in the conversation you already use. Ask for a market briefing,
drill into a competitor, or explore an opportunity. She connects what she finds to your
products, stock and goals, then helps you turn it into a practical next move.

**Observe → Connect → Understand → Recommend → Review**

## What Iris can help you do

| Your question | Iris’s role |
| --- | --- |
| **“What’s happening in my market?”** | Bring selected watch history and on-demand research into a focused briefing, with sources and priorities. |
| **“How is Infinity doing right now?”** | Investigate its public product pages, offers and availability; explain what the evidence says and what remains uncertain. |
| **“How do we compare?”** | Bring relevant products from several competitors into one comparison, accounting for format, quantity and offer conditions. |
| **“Why might they be making that move?”** | Look for official explanations and relevant external context. Keep supported facts and possible explanations distinct. |
| **“Where should I focus this week?”** | Connect market signals to your catalog, stock, costs and goal; recommend a practical priority. |
| **“Help me respond.”** | Draft grounded product or campaign copy in English or Egyptian Arabic, remember your chosen move and help review reported results. |

Scheduled checks cover the product pages you choose. On-demand investigations can explore
additional competitors and public sources. Coverage and dates stay visible; competitor
sales, motives and market demand are not inferred from a product listing.
Supported connected-app changes require your request and readback; live writes remain unverified.

## A morning with Iris

An Egyptian skincare owner wants to plan the week:

> **“Give me a market briefing for sunscreen and moisturizers. Look at Infinity and two
> other relevant stores. What should I pay attention to?”**

Iris reads the store’s catalog, researches relevant competitor pages and brings the findings
together. The owner follows up:

> **“Go deeper on Infinity. Is this a broader campaign? What can we actually tell?”**

Then:

> **“What’s the best move for my store this week? Turn it into a short Arabic message.”**

The owner chooses a response. Iris remembers it, ready for the next conversation and a later
review. This is the broader [demo scenario](docs/DEMO.md); the new recording remains to be made.
[Evidence and actual trial results](docs/EVALUATION.md) distinguish live reads from controlled examples.
The latest broad rehearsals still contain unsupported claims; repeatable briefing accuracy
remains an open evaluation item.

## Built around the owner

- **A view across competitors.** Group relevant findings around your products and priorities.
- **Context for your business.** Connect outside evidence with your catalog and owner-confirmed goals.
- **Useful follow-through.** Move from a briefing to a supported draft, chosen action and review.
- **A conversation with memory.** Ask follow-ups and revisit decisions without rebuilding the context.
- **Evidence you can inspect.** Sources, observation history and operator traces support checking an answer.

Existing competitive-intelligence products demonstrate the value of connecting research to
decisions. Iris brings that ambition to a small store owner in Telegram.
[Product promise and boundaries](docs/PRODUCT.md).

## Architecture

![Iris architecture: an owner in Telegram, Hermes and the Iris profile, competitor research, native Composio, selected-product history, calculations and native Langfuse tracing.](assets/architecture.png)

[Editable SVG](assets/architecture.svg) · [Product](docs/PRODUCT.md)

| Layer | Responsibility |
| --- | --- |
| [Hermes](https://github.com/NousResearch/hermes-agent) | Telegram, Luna in the tested deployment, sessions, memory, native web research, vision, schedules and delivery. |
| Iris skills | Market investigations, evidence interpretation, recommendations, drafts and reviews. Iris writes the owner-facing advice. |
| Four Iris tools | `read_store`, `watchlist`, `market_changes`, `market_math`: public product facts, selected history and sourced calculations. |
| Native [Composio](https://composio.dev/) | Authorized reads and owner-requested operations in connected apps. |
| Native Langfuse plugin | Model/tool timelines, timing and usage for operator review. |

Scheduled checks read connected apps. Requested writes and readback are instruction boundaries,
not an enforced transaction policy. See [current status](docs/STATUS.md) for verification.

## Observability

Langfuse distinguishes the owner profile from private test runs using user labels.
[User attribution and recorded Cloud checks](docs/OBSERVABILITY.md#user-attribution).

A real owner Telegram session and eight private turns were reconciled with Langfuse:
**10 turns, 24 main model calls, 14 tool requests**, matching canonical token totals and
no duplicate observation IDs in that sample.

The latest private check also reconciles **12 turns, 39 main model completions and 53 tool
requests**, with failed attempts counted separately.
[Readback](docs/evidence/cloud-release-final.json).

Private native reports retain source URLs, content hashes, arguments and replies.
Cloud metadata mode shows the call timeline without raw owner/app payloads.
Complete auxiliary usage and actual provider charges remain unreconciled.
[Tracing, costs and reliability](docs/OBSERVABILITY.md) ·
[Sanitized run summary](docs/evidence/run-summary.json)

## What’s next

- **A clearer market picture:** stronger product matching and persistent grouping across competitors.
- **Richer strategic context:** broaden recorded signals to relevant campaigns, catalog and policy changes.
- **Better investigations:** improve source freshness, resolve conflicts and reduce repeated discovery.
- **Learning from use:** measure owner time saved and review which recommendations actually helped.

These are development priorities, not claims of already delivered features.
[Evidence priorities](docs/EVALUATION.md#highest-value-remaining-proof)

## Run Iris

The [hosted owner bot](https://t.me/IrisMarketWatcherBot) is restricted to its configured owner.
A separate judge access route is still required.

With Hermes installed, a model provider and your own Telegram/Composio authorization:

```sh
git clone https://github.com/AndrewMaged814/iris.git
cd iris
hermes profile install . --name iris
hermes -p iris setup
```

Follow [setup](docs/SETUP.md) to install reader dependencies, connect the catalog and verify
a reply. Fresh-machine setup with OAuth has not been demonstrated in under five minutes.

Local contracts need no credentials or network:

```sh
python -m unittest discover -s tests
python tools/validate_repo.py
```

The offline contracts pass; the [current verification record](docs/STATUS.md) gives the test count. Connected reads, private investigations, chosen-action memory
and real Telegram calculation have evidence. Merchant impact, live app writes and the complete
new demo journey need further verification.
[Evaluation](docs/EVALUATION.md) · [Testing](docs/TESTING.md) · [Status](docs/STATUS.md)

## Hackathon

The new [2–3 minute demo](docs/DEMO.md), judge access and measured-impact deck are submission
priorities. The obsolete animation and slide drafts have been archived; working footage and measured impact are still required.
[Official requirements](docs/HACKATHON_RULES.md) · [Evidence ledger](docs/EVALUATION.md)

## License

[MIT](LICENSE) · [Third-party notices](NOTICE) · [Asset credits](assets/README.md)
