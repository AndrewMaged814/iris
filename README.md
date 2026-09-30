<p align="center">
  <img src="assets/iris-logo.png" alt="Iris — AI growth scout" width="180">
</p>

<h1 align="center">Iris</h1>
<p align="center"><strong>Your market moves. Move smarter.</strong></p>
<p align="center">Your AI growth scout. Iris watches your market, spots opportunities for your store,<br>and brings your next move to Telegram.</p>

<p align="center">
  <a href="docs/DEMO.md">See Iris in action</a> ·
  <a href="docs/SETUP.md">Connect your store</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="docs/EVALUATION.md">Business cases</a>
</p>

<p align="center">Built on <a href="https://github.com/NousResearch/hermes-agent">Hermes</a> · Shopify · Telegram · English & Egyptian Arabic</p>

## From a competitor move to your next move

A competitor's price is only part of the story. Iris connects prices, promotions and availability
to **your products**, helps you weigh the decision, and drafts the next step when you ask.

> **You:** “Can I say my sunscreen is cheaper than Infinity's?”
>
> **Iris:** One bottle: yours **EGP 320**, theirs **EGP 360**.
> But their advertised **buy 2, get 2** deal makes four bottles **EGP 720**,
> versus your **EGP 1,280**, if the offer applies.
>
> **The decision:** A lower single-bottle price doesn't support an unqualified “cheaper” claim.

## What you can do with Iris

| Bring Iris a question | Get something you can use |
| --- | --- |
| **“What's changed in my market?”** | Relevant price, markdown and stock changes, connected to your products |
| **“Should I lower my price?”** | Product and offer comparisons, plus margin math from your cost inputs |
| **“What should I improve?”** | One useful product-listing fix based on its photos and catalog details |
| **“Write it in Egyptian Arabic.”** | A caption, product line or reply using the facts your store supplies |
| **“Let's do this. Remember it.”** | A saved chosen action and a weekly review of what you report happened |
| **“Prepare a response offer.”** | A margin-checked code proposal; exact owner approval before creation and Shopify readback |

Iris checks daily and brings a weekly brief. Quiet daily checks stay quiet.
You choose the competitors and the actions. Optional response codes require fresh approval in
Telegram; base prices stay unchanged and announcement publishing stays with you.

## Quick start

You'll need Hermes, a model provider, a Telegram bot and a Shopify product connection.

```sh
git clone https://github.com/AndrewMaged814/iris.git
cd iris
hermes profile install . --name iris
hermes -p iris setup
```

Then connect your catalog and Telegram, and enable the daily and weekly checks.
**[Follow the setup guide →](docs/SETUP.md)** The repository currently requires access.

## Architecture

Iris supplies the business judgment, skills and tools. Hermes supplies the agent runtime.

![Iris architecture: Telegram connects to Hermes, which runs Iris and scheduled checks; Iris reads Shopify, competitor storefronts and saved market evidence.](assets/architecture.png)

The four tools read your catalog, inspect competitors, manage the watchlist and retrieve changes.
The own-store tool also handles bounded response codes when offer access is enabled.
Public readers support Shopify, WooCommerce and structured product pages.
Saved observations distinguish today's listings from changes recorded over time.

## Project structure

```text
iris/
├── SOUL.md             Iris's voice and business judgment
├── config.yaml         Hermes profile settings
├── plugins/iris/        Four tools, product readers and market evidence
├── skills/             Setup, market watch, weekly brief and drafting
├── scripts/            Daily checks, weekly data and schedule setup
├── tools/              Connection doctor, validator and business evaluator
├── tests/              Offline regression tests
├── docs/               Demo, setup, evaluations and product direction
└── assets/             Iris mascot and its creation prompt
```

## Proof & next steps

**92 offline tests. 22 reusable business cases.** Native Luna runs exercise comparisons,
drafting and remembered actions; Telegram delivery and scheduled checks have been verified.
[Expected vs. actual](docs/EVALUATION.md) · [Deployment status](docs/STATUS.md)

- **Next:** enable the narrow offer permissions and verify the approved-create-stop flow through
  Telegram, then measure a real merchant pilot.
- Improve promotion coverage and weekly follow-up from the cases that expose gaps.

[Product direction](docs/PRODUCT.md) · [Testing guide](docs/TESTING.md)

## Contributing & license

Review [AGENTS.md](AGENTS.md), then run `python3 -m unittest discover -s tests` and
`python3 tools/validate_repo.py` before proposing a change. Business-case failures are especially useful.

[License](LICENSE) · [Third-party credits](NOTICE) · [Logo & prompt](assets/README.md)
