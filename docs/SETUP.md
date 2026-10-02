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

Never commit real credentials. This version uses operator-configured product access;
a merchant OAuth onboarding service is not included. [Shopify background](research/SHOPIFY_DEV_APP.md).

### Research: reuse Hermes

Iris uses native `web_search` and `web_extract`, including Hermes's provider selection,
cache, website policy and fallback. Configure the same working web provider as the default
profile with Hermes; keep provider credentials private in the profile. No separate search
service is required by Iris.

```sh
hermes -p iris tools
```

For an existing profile, remove the old `web.search_backend: searxng` override and remove
`SEARXNG_URL` if it was added only for Iris. Removing the config override alone can still
leave Hermes autodetecting SearXNG from that environment variable. Preserve deliberately
chosen provider settings. Verify a real store query and product-page extraction, not only
HTTP reachability. Profile settings are separate: a fresh Iris profile does not automatically
inherit the default profile's credentials.

### Product reader dependencies

The profile plugin declares `extruct` and `price-parser`. On the tested Hermes revision,
manifest dependencies are checked but profile installation does not install them automatically.
Run with the same Python Hermes uses, then verify with the doctor:

```sh
python -m pip install 'extruct>=0.18,<1' 'price-parser>=0.5,<1'
```

### Browser for JavaScript product pages

Iris uses Hermes's local browser in chat. The tested `c1488ac` has no `hermes pm` command;
with Node.js/npx available, prepare the native CLI and Playwright cache:

```sh
npx --ignore-scripts -y agent-browser@0.26.0 --version
npx playwright install --with-deps chromium
```

The tested Hermes browser probe looks for Playwright's `chromium-*` cache directories;
`agent-browser install` alone can install Chrome in a cache that this revision misses.
Set the profile's `.env` (quote the value, including spaces):

```dotenv
AGENT_BROWSER_ARGS="--user-agent=IrisBot/1.0 (market watch for a store owner; read-only)"
```

For a root/container host that needs sandbox flags, use comma-separated arguments:

```dotenv
AGENT_BROWSER_ARGS="--no-sandbox,--disable-dev-shm-usage,--user-agent=IrisBot/1.0 (market watch for a store owner; read-only)"
```

`browser.cloud_provider: local` and `browser.backend: "off"` select native read tools and
exclude `browser_exec`. Iris's pre-tool hook allows navigate, snapshot, scroll, back, images
and vision; it blocks browser actions, private addresses and robots-disallowed navigation.
Cron has no browser toolset. Check the actual request User-Agent and guard on your installed
revision before relying on browser reads. Report blocks; never bypass a challenge.

## 3. Verify the connection

From the repository, use Hermes's Python environment:

```sh
python tools/iris_doctor.py --profile-home ~/.hermes/profiles/iris --live
hermes -p iris gateway status
```

The doctor needs Hermes's `python-dotenv` and safe web client. Verify the chosen model with an
actual Iris reply. Open the bot, tap **Start**, then ask: **“What products do I sell?”**
Iris should read the connected catalog. Ask her to research competitors and approve specific
product pages to watch.

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
Daily structured price/stock checks do not automatically detect page-only promotions.

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
