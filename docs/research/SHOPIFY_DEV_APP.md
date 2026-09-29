# Development app setup

Target supplied by Andrew and verified in the logged-in Dev Dashboard: Mira Nile,
`mira-nile.myshopify.com`, development store under Mira Nile Lab. This is not yet
an authorized Iris connection.

Andrew created the standalone app **Iris**; its active version and read-only settings
were verified in the developer dashboard. Credentials are configured privately on
the Hermes host. No live merchant connection exists yet. Use the running HTTPS origin as
App URL and `<origin>/oauth/callback` as the allowed redirect. Disable embedding;
request only `read_products`; API version `2026-07`. Prefer the dashboard's
managed installation default for the first live test. If standalone OAuth
requires an installation change, record the observed failure and resolve it
against official documentation before changing the setting.

The current temporary Cloudflare Quick Tunnel is a development callback bridge,
not production hosting. Its hostname must match the private service environment
and Shopify redirect registration. Tunnel restart can change that hostname;
check it before onboarding. Stable hosting, production distribution, uninstall
handling and public-app review remain outside this first experiment.

App registration creates a persistent app identity/client credential. Store the
credential privately on the Hermes host; never paste it in Telegram or commit
it. Installing the app and approving `read_products` is a separate merchant
consent step. Complete it through Iris onboarding once the trusted Telegram
adapter exists; do not treat an operator-invented user ID as onboarding.
