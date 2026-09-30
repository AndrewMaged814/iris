# Operator setup versus merchant onboarding

Historical prototype investigation: the connection service and OAuth bridge described below are
not included in the current Iris distribution. Use [the current operator guide](../SETUP.md)
for the working one-store credential setup and [STATUS.md](../STATUS.md) for verified capabilities.

The profile uses the native Hermes Telegram gateway. `hermes -p iris-production setup model` configures inference; `hermes -p iris-production setup gateway` configures the separate bot and owner authorization. Create the bot in Telegram through BotFather `/newbot`; enter its token privately in the host's native wizard. A new profile should not clone existing bot tokens or merchant credentials. Native messaging settings and required features must be checked against the installed Hermes revision, not inferred from current docs.

After operator setup, preserve the live profile's model/provider settings and secrets during distribution updates. The repository's blank `model` is an installation template. Do not force-reinstall that template over a configured profile: the inspected installer replaces distribution-owned `config.yaml` when forced. Apply reviewed plugin/skill changes without replacing live model or gateway settings, and verify the resolved tool inventory afterward. A model name alone is insufficient; verify a real native model turn and the profile-specific connected platform status.

For Shopify onboarding, the Iris operator must create an app in Shopify's Dev Dashboard, configure read-only product scopes, set the application/callback HTTPS URLs, and store client credentials in the server secret environment. V1 serves Andrew's test store; app distribution type is not selected automatically because Shopify documents that choice as irreversible. Choose custom distribution only when its one-store/organization limits match the intended deployment.

The merchant then enters their store domain in Telegram, opens the returned link, approves permissions in Shopify, and confirms the verified store in the original Telegram chat. They do not edit environment files, create per-merchant API tokens or upload product facts by hand.

The `codex/shopify-onboarding` slice supplies the [connection service](../services/shopify_auth/README.md) and native plugin. The service's private environment contains Shopify credentials and encryption key. Create `local/shopify-auth/bridge.json` under the deployed profile with only `internal_secret` matching the service bearer; mode 600. The plugin reads this privately and fixes its URL to loopback port 8788. Its tool schemas exclude owner IDs, tokens and activation operations.

After configuration, verify plugin discovery, the exact resolved Telegram tool inventory, owner authorization and handler registration before issuing a link. The first live run must prove consent, original-chat button confirmation, product read and `/new` persistence. Browser consent remains a merchant action. Stable HTTPS and production review are later requirements.

The temporary development client grant is enabled only for Andrew's installed Mira Nile app/store in the same Shopify organization and his authenticated Telegram account. Its two private environment settings are documented in the service README. App installation grants product read access; it is not the original-chat binding. The live `store_connection begin` and confirmation button must establish that binding. Ordinary merchant onboarding remains OAuth. The [live gateway tool-loading issue](issues/2026-09-28-live-gateway-tools.md) records why an isolated plugin test does not prove live availability.
