<p align="center">
  <img src="assets/iris-logo.png" alt="Iris mascot" width="144">
</p>

<h1 align="center">Iris</h1>
<p align="center"><strong>Your AI market watcher.</strong></p>
<p align="center">Know what’s changing. See what matters. Make your next move.</p>
<p align="center">Iris connects competitor activity, market research and your store’s context<br>to help you see opportunities, understand threats and decide where to focus.</p>

<p align="center">
  <a href="#business-value">Business value</a> ·
  <a href="#how-iris-helps">Capabilities</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#observability">Observability</a> ·
  <a href="docs/DEMO.md">Demo plan</a> ·
  <a href="#run-iris">Run Iris</a>
</p>

## Business value

Running a small store leaves little time to keep up with the market. Iris brings the
research into one conversation: what competitors are offering, how it relates to your
business, and what deserves your attention.

**Iris helps owners spend less time checking competitors, avoid unnecessary spending,
and spot opportunities to earn more.** These are the outcomes we’re building toward;
time saved, cost saved and revenue gains have not yet been measured.

| Outcome | How Iris can help | What we will measure |
| --- | --- | --- |
| **Save time** | Gather relevant sources, compare competitors and prepare a briefing; carry context into follow-up questions. | Manual research time versus time with Iris, including checking and correcting the answer. |
| **Reduce costs** | Check whether a competing offer is actually comparable before recommending a price or campaign response; consider your costs and stock. | Spending avoided or margin retained after an owner uses the advice, accounting for Iris’s running cost. |
| **Create revenue opportunities** | Find relevant gaps in competing offers, connect them to available products and help prepare a focused customer message. | Enquiries, orders and revenue against a comparable baseline; separate observed changes from claims that Iris caused them. |

These match the hackathon’s [published business-impact criteria](docs/HACKATHON_RULES.md#judging).
Agent response time is recorded in evaluations; it is not a measurement of owner time saved.

## How Iris helps

**Observe → Connect → Understand → Recommend → Review**

| Ask Iris | The work she supports |
| --- | --- |
| **“What should I know about my market this week?”** | Bring selected watch history and new research into a briefing with sources, priorities and coverage gaps. |
| **“What is Infinity offering, and how do the other stores compare?”** | Investigate public products, offers and availability; compare relevant alternatives across competitors. |
| **“What might explain this move?”** | Look for official explanations and relevant context, distinguishing confirmed facts from hypotheses. |
| **“What makes sense for my store?”** | Connect findings to your catalog, stock, costs and goals; recommend a practical next step and draft copy when asked. |
| **“What did we decide, and did it help?”** | Remember your chosen move and review the results you report against a baseline. |

Scheduled monitoring covers the product pages you choose; wider market research runs on
request. Current listings show public activity. Dated observations support change claims.
Competitor sales and hidden motives need their own evidence.
[Product promise and boundaries](docs/PRODUCT.md).

## Architecture

![Iris architecture: Hermes and the Iris profile connect the owner to competitor research, native Composio, selected-product history, calculations and native Langfuse tracing.](assets/architecture.png)

[Editable SVG](assets/architecture.svg)

| Layer | Responsibility |
| --- | --- |
| [Hermes](https://github.com/NousResearch/hermes-agent) | Conversation, sessions, memory, native web research, vision, schedules and delivery. The tested deployment uses Luna and Telegram. |
| Iris skills | Market investigations, interpretation, recommendations, requested drafts and reviews. Iris writes the business advice. |
| Four Iris tools | `read_store`, `watchlist`, `market_changes`, `market_math`: structured public product facts, selected history and calculations. |
| Native [Composio](https://composio.dev/) | Authorized connected-app reads and owner-requested changes. Scheduled checks only read apps. |
| Native Langfuse plugin | Model and tool timelines, timing, usage and failures for operator review. |

Requested app changes require exact terms and readback through instructions; this release
has no enforced transaction bridge, and live app writes remain unverified.

## Observability

Each investigation can be reviewed through its tool sequence, sources, final reply,
elapsed time and token usage. Private source reports let us check whether the evidence
supports the recommendation. Langfuse separates owner activity from private evaluations.
Evaluation exports flag citations without a captured source read for review.

The latest Cloud readback reconciles **12 private turns, 39 main model completions and
53 tool requests**, with failed attempts tracked separately.
[Recorded readback](docs/evidence/cloud-release-final.json).

Metadata capture keeps raw owner/app payloads out of Cloud. Actual provider charges and
complete auxiliary usage are still unreconciled. Traces show what ran; source review
establishes whether the answer was supported.
[Tracing, costs and reliability](docs/OBSERVABILITY.md).

## Current evidence

Native rehearsals demonstrate connected catalog reads, research across three businesses,
requested Arabic drafting and fresh-session recall of a chosen move. Owner Telegram
replies and sanitized execution records are also retained.

**Broad briefing accuracy remains a release priority:** the latest rehearsal still made
an unsupported promotion claim. Offline tests passing does not establish answer accuracy.
Merchant impact has not been measured; the working demo recording and judge access route
are still pending. [Replies and critique](docs/EVALUATION.md) · [Current status](docs/STATUS.md).

## Run Iris

With Hermes installed, a model provider and your own Telegram/Composio authorization:

```sh
git clone https://github.com/AndrewMaged814/iris.git
cd iris
hermes profile install . --name iris
hermes -p iris setup
```

Follow [setup](docs/SETUP.md) to install reader dependencies, connect the catalog and verify
a reply. The [hosted bot](https://t.me/IrisMarketWatcherBot) is restricted to its configured
owner. A separate judge route and fresh-machine setup under five minutes still need verification.

Local checks need no credentials or network:

```sh
python -m unittest discover -s tests
python tools/validate_repo.py
```

[Testing and native evaluations](docs/TESTING.md).

## What’s next

- **Reliable briefings:** resolve product/variant and source conflicts before drawing conclusions.
- **A broader market picture:** stronger grouping across competitors and richer campaign, catalog and policy history.
- **Proof of value:** a timed owner workflow, a working 2–3 minute demo and verified judge access.

[Demo storyboard](docs/DEMO.md) · [Evidence priorities](docs/EVALUATION.md#highest-value-remaining-proof) · [Submission requirements](docs/HACKATHON_RULES.md).

## License

[MIT](LICENSE) · [Third-party notices](NOTICE) · [Asset credits](assets/README.md)
