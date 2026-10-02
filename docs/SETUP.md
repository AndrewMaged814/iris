# Connect your store to Iris

Set up one Hermes profile for one store owner, then talk to Iris in Telegram.

## What you need

- [Hermes](https://github.com/NousResearch/hermes-agent) with profile distributions and a model provider.
- A Telegram bot token and the owner's numeric Telegram ID.
- A Shopify app installed on the store, with **`read_products`** access.
- Access to this repository. Iris is currently private.

The tested installation uses Hermes commit `c1488ac` and Luna through Azure Foundry.
The distribution lets you select your own provider; model settings and credentials belong on the host.

## 1. Install a fresh profile

```sh
git clone https://github.com/AndrewMaged814/iris.git
cd iris
hermes profile install . --name iris
hermes -p iris setup
```

Choose your model and configure Telegram through Hermes. Keep the bot token private.
If Iris is already installed, use the verification steps below rather than reinstalling.

## 2. Connect Shopify and authorize the owner

Use [`.env.EXAMPLE`](../.env.EXAMPLE) as the checklist for the profile's `.env`:

| Setting | Value |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | The bot token from BotFather |
| `TELEGRAM_ALLOWED_USERS` | The owner's numeric Telegram ID |
| `SHOPIFY_STORE` | The store's `your-store.myshopify.com` address |
| `SHOPIFY_CLIENT_ID` + `SHOPIFY_CLIENT_SECRET` | Installed Shopify app credentials |
| `SHOPIFY_ADMIN_TOKEN` | Alternative to the client-credential pair |

| `SEARXNG_URL` | Your SearXNG instance, for free competitor search |

Never commit real credentials. This version uses operator-configured product access;
a merchant OAuth onboarding service is not included. [Shopify background](research/SHOPIFY_DEV_APP.md).

### Competitor search (SearXNG)

Iris finds competitors with Hermes `web_search` through a self-hosted
[SearXNG](https://docs.searxng.org/) instance: free, no API key, results from several engines.
`config.yaml` selects it with `web.search_backend: searxng`; Hermes does not fall back to another
backend, so search fails visibly if SearXNG is unreachable. Page reading (`web_extract`) keeps
Hermes's own backend selection.

```sh
docker run -d --name searxng --restart unless-stopped -p 127.0.0.1:8888:8080 searxng/searxng
```

In the instance's `settings.yml`, add `json` to `search.formats` (Hermes requests JSON results)
and restart it. Then set `SEARXNG_URL=http://127.0.0.1:8888` in the profile's `.env`. Keep it bound
to localhost; it doesn't need to be public.

## 3. Verify the connection

From the repository, use Hermes's Python environment:

```sh
python tools/iris_doctor.py --profile-home ~/.hermes/profiles/iris --live
hermes -p iris gateway status
```

The doctor needs Hermes's `python-dotenv` and safe web client. Verify the chosen model with an
actual Iris reply. Open the bot, tap **Start**, then ask: **“What products do I sell?”**
Iris should read the connected catalog. Ask her to suggest competitors and approve the ones to watch.

Gateway ownership depends on your Hermes setup. The tested host uses one shared gateway for
all profiles; it does not need a separate Iris service. Use Hermes's native gateway management.

## 4. Enable daily checks and the weekly brief

Run this **once**, replacing the example number with the authorized owner's Telegram ID:

```sh
OWNER_CHAT_ID=123456789 bash scripts/setup_jobs.sh
hermes -p iris cron list --all
```

Expect `iris-daily-check` at **08:00** and `iris-weekly-brief` on **Sunday at 10:00**, Cairo time.
The setup enables native delivery mirroring so the owner's reply can refer to the report.
Daily catalog checks do not automatically detect every page-only promotion.

## Updating an existing Iris

- Preserve its model/provider configuration, `.env`, `memories/`, `state.db` and `iris/iris.db`.
- Apply reviewed changes to distribution-owned runtime files. Do not force-install the blank
  template over a configured profile: it can replace `config.yaml`.
- Verify the doctor, model reply and tool inventory; gracefully reload the gateway when needed.
- Existing conversations can retain frozen instructions and earlier response patterns. If a
  fresh session is needed, use Hermes's native session reset; retain the earlier transcript and memory.
- Check the existing jobs. Rerunning `setup_jobs.sh` creates duplicates.

When reusing a previously deleted profile name on the tested Hermes revision, create its empty
home first with `hermes profile create iris --no-skills --no-alias`. Installation with `--force`
is only for that empty profile, before configuring credentials or the model.

## Optional response offers

Catalog reading needs only `read_products`. Enable Iris's first store action separately:

1. In the installed Shopify app, add `write_discounts` (includes discount reads).
   Release/install the app's updated permissions. Refresh its token if the cached grant still has
   the old scopes. Existing `read_products` covers costs and aggregate variant stock; no inventory,
   orders, customers or product-write access is added. For analysis alone, use `read_discounts`.
2. In Shopify, enter the selected variant's unit cost in store currency. Enable inventory tracking,
   supply its actual available stock and disable selling when out of stock. The first slice needs
   tax-exclusive pricing and no other active/scheduled discount; existing markdowns also block it.
   Offer arithmetic currently supports EGP, USD, EUR, GBP, CAD and AUD; catalog reads are unchanged.
3. Set `IRIS_ENABLE_OFFERS=1` in the profile's private `.env` and reload Hermes gracefully.
   Keep `TELEGRAM_ALLOWED_USERS` set to the single owner's numeric ID. Preserve provider settings.
4. Ask Iris to assess a market response. Supply variable payment fees, packaging/shipping subsidy
   per unit and the minimum contribution margin. Review the code, variant, percentage, start/end,
   redemption limit and assumptions. Creation requires **Approve** on the fresh native Telegram
   prompt, even if a prior chat message said yes. **Cancel**, timeout or changed facts means no write.
5. Iris verifies the saved Shopify configuration and offers copy in your chosen brand language.
   Readback does not test checkout eligibility. To stop the code, ask Iris and approve its separate
   deactivation prompt. Past orders remain unchanged.

The native approval bridge is tested against Hermes `c1488ac`: it uses the live gateway runner's
clarification primitive with a unique question ID. If this API changes or the owner/session cannot
be established, execution fails closed. Revalidate it after upgrading Hermes. Cron, CLI evaluation,
group chats and other users cannot execute offers, even with the enable flag set.

An uncertain write is not retried. Ask for its status to reconcile the exact code and terms;
investigate unresolved cases in Shopify. Keep a newly prepared proposal separate from the original.
No automatic campaign publishing, base-price editing or customer-data access is included.

[Try the demo cases →](DEMO.md) · [Current deployment](STATUS.md) · [Testing](TESTING.md)
