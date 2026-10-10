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
  <a href="#connect-your-tools">Connect your tools</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#observability">Observability</a> ·
  <a href="#run-iris">Run Iris</a>
</p>

## Business value

Running a small store leaves little time to keep up with the market. Iris brings the
research into one conversation: what competitors are offering, how it relates to your
business, and what deserves your attention.

**Iris helps owners spend less time checking competitors, avoid unnecessary spending,
and spot opportunities to earn more.**

| Outcome | How Iris helps |
| --- | --- |
| **Save time** | Gather relevant sources, compare competitors and prepare a briefing; carry context into follow-up questions. |
| **Reduce costs** | Check whether a competing offer is actually comparable before recommending a price or campaign response; consider your costs and stock. |
| **Create revenue opportunities** | Find relevant gaps in competing offers, connect them to available products and help prepare a focused customer message. |

These match the hackathon’s [published business-impact criteria](docs/HACKATHON_RULES.md#judging).

## How Iris helps

**Observe → Connect → Understand → Recommend → Review**

| Ask Iris | The work she supports |
| --- | --- |
| **“What should I know about my market this week?”** | Bring selected watch history and new research into a briefing with sources, priorities and coverage gaps. |
| **“What are my competitors offering, and how do we compare?”** | Investigate public products, offers and availability; compare relevant alternatives across competitors. |
| **“What might explain this move?”** | Look for official explanations and relevant context, distinguishing confirmed facts from hypotheses. |
| **“What makes sense for my store?”** | Connect findings to your catalog, stock, costs and goals; recommend a practical next step and draft copy when asked. |
| **“What did we decide, and did it help?”** | Remember your chosen move and review the results you report against a baseline. |

Scheduled monitoring covers the product pages you choose; wider market research runs on
request. Current listings show public activity. Dated observations support change claims.
Competitor sales and hidden motives need their own evidence.
[Product promise and boundaries](docs/PRODUCT.md).

## Connect your tools

> **“Iris, connect my Shopify store.”**

For apps supported by [Composio Connect](https://docs.composio.dev/docs/composio-connect),
Iris finds the integration and guides you through connecting your account:

1. **Ask Iris** to connect the tool you use.
2. **Open the authorization link** Iris receives from Composio and shares in the chat.
3. **Approve access** through Composio’s connection flow.
4. **Continue with Iris.** She verifies the connection, then uses the app for your requested task.

**Ask → Authorize → Verify → Use**

Your catalog, spreadsheet or other supported business tool becomes context Iris can work
with. Connecting an app is separate from choosing which catalog or sheet she should use.
[Connection flow](https://docs.composio.dev/toolkits/meta-tools/manage_connections) ·
[Setup](docs/SETUP.md).

## Architecture

![Iris architecture: Hermes runs Iris, Composio connects business tools, and a Langfuse observability layer tracks response time, tool calls and usage.](assets/architecture.png)

[Editable SVG](assets/architecture.svg)

| Layer | Responsibility |
| --- | --- |
| [Hermes](https://github.com/NousResearch/hermes-agent) | Conversation, sessions, memory, native web research, vision, schedules and delivery. The tested deployment uses Luna and Telegram. |
| Iris skills | Market investigations, interpretation, recommendations, requested drafts and reviews. Iris writes the business advice. |
| Four Iris tools | `read_store`, `watchlist`, `market_changes`, `market_math`: structured public product facts, selected history and calculations. |
| Native [Composio](https://composio.dev/) | App discovery, authorization links and connected-app operations. Scheduled checks only read apps. |
| Observability layer | Hermes’s Langfuse plugin records response time, model/tool calls and token usage, grouped by user and session. |

For requested app changes, Iris confirms the terms and checks the saved result by readback.
[Technical setup and boundaries](docs/SETUP.md).

## Observability

**Follow a request from tool selection to the final response—and see where the time and tokens went.**

Iris has an observability layer powered by the [Langfuse plugin in Hermes](https://github.com/NousResearch/hermes-agent/tree/c1488ac947c9bc33fd65ec464548dc9d8edd6122/plugins/observability/langfuse).
It records model and tool activity so we can inspect an investigation and improve it.

| What we track | What it tells us |
| --- | --- |
| **Response time** | How long an agent turn takes and which model or tool calls account for the wait. |
| **Tokens and model usage** | Input, output and reported cache usage for model calls. |
| **Usage by user and session** | Activity grouped by the profile’s owner label and conversation, with evaluations labeled separately. |
| **Tool calls, failures and retries** | The path Iris took, the sources she accessed and where execution needs attention. |

Cloud traces use metadata capture; private session reports retain the source evidence for
answer review. Evaluation exports also flag cited URLs without a captured source read.

[Inspect a recorded trace check](docs/evidence/cloud-release-final.json) ·
[Tracing setup and reporting](docs/OBSERVABILITY.md) ·
[Langfuse user tracking](https://langfuse.com/docs/observability/features/users).

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

[Evidence priorities](docs/EVALUATION.md#highest-value-remaining-proof) · [Submission requirements](docs/HACKATHON_RULES.md).

## License

[MIT](LICENSE) · [Third-party notices](NOTICE) · [Asset credits](assets/README.md)
