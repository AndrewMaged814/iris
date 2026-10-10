# Connect your store to Iris

Set up one Hermes profile for one store owner, then talk to Iris in Telegram.

## What you need

- [Hermes](https://github.com/NousResearch/hermes-agent) with profile distributions and a model provider.
- A Telegram bot token and the owner's numeric Telegram ID.
- A Composio account and an app containing the owner's product information.
- Access to this public repository.

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

## 2. Authorize the owner and connect Composio

Use [`.env.EXAMPLE`](../.env.EXAMPLE) for the Telegram bot token, allowed owner ID and browser
user agent. There are no Iris-specific Shopify credentials or app API clients.
Keep `TELEGRAM_ALLOW_ALL_USERS=false` for an owner profile; an owner ID alone does not close
public access when that flag is enabled.

Hermes connects to `https://connect.composio.dev/mcp` with native OAuth. Enable the shipped
`mcp_servers.composio` entry and authenticate with `hermes -p iris mcp login composio`.
On a remote host, use Hermes's SSH callback forwarding. Keep tokens private in the profile.
Telegram and cron select the native server toolset by its name, `composio`.

Ask Iris to connect the app where your products live. Authorize the link in Telegram. Iris
verifies the connection, discovers and reads candidate sources, and confirms the catalog and
ambiguous fields with you. She saves its location and field meanings in Hermes memory.
Connecting another app later follows the same process. Missing facts stay unknown.

The owner-authorized demo exposes connected app reads and writes directly through Composio.
There is no custom action allowlist, catalog adapter, Shopify fallback, offer ledger or native
discount confirmation bridge. Iris uses requested terms and readback; this is agent instruction,
not an enforced discount policy. Scheduled market checks are instructed to read apps only.
Supported operations depend on the toolkit and authorized account; connecting an app does not
prove every operation works. No Composio developer API key is needed for this Connect setup.

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

### Optional operator tracing

Hermes includes a native `observability/langfuse` plugin. Enable it with your Langfuse project
credentials to inspect model/tool timelines. The current Iris host uses metadata capture;
private case reports retain the detailed evidence. Follow [the observability guide](OBSERVABILITY.md)
for native setup, the gateway capture setting and verified limits.

### Product reader dependencies

The profile plugin declares `extruct` and `price-parser`. On the tested Hermes revision,
manifest dependencies are checked but profile installation does not install them automatically.
Run with the same Python Hermes uses, then verify with the doctor:

```sh
python -m pip install 'extruct>=0.18,<0.19' 'price-parser>=0.5,<0.6'
```

### Pages needing JavaScript

The current profile excludes browser tools after navigation/daemon failures. Use native
extraction or owner-provided screenshots; report blocked pages. Dormant browser configuration
and its read-only guard remain for a separately tested recovery. Browser setup is not required
for this release. Never bypass a challenge or disguise Iris's user agent.

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

## 4. Enable the daily checks and weekly brief

Run this **once**, replacing the example number with the authorized owner's Telegram ID:

```sh
OWNER_CHAT_ID=123456789 bash scripts/setup_jobs.sh
hermes -p iris cron list --all
```

Expect three jobs in Cairo time: `iris-daily-check` at **08:00** for structured price and stock
changes, `iris-offer-check` at **08:30** for advertised offers on watched product pages, and
`iris-weekly-brief` on **Sunday at 10:00**. The setup enables native delivery mirroring so the
owner's reply can refer to a report. The offer check reads pages with Hermes; it does not prove
checkout eligibility or guarantee that every page-only promotion is visible.

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

## Migrating an existing profile

Back up runtime files and private configuration first. Remove `iris_store.py`, `iris_offers.py`
and stale compiled copies from the deployed plugin. Remove `SHOPIFY_*` and `IRIS_ENABLE_OFFERS`
settings and the old token cache from the active profile after keeping a private backup.
Preserve watch/history databases, owner memories, native MCP authorization and message history.
Update existing scheduled prompts to read the confirmed connected catalog; do not recreate jobs.
Refresh frozen instructions through Hermes and restart the native gateway. Verify Composio
again after restart and read a real catalog before claiming catalog migration is complete.

[Current deployment](STATUS.md) · [Testing](TESTING.md)
