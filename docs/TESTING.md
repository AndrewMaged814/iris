# Test Iris

Run offline checks with the declared reader dependencies and python-dotenv installed:

```sh
python3 tools/validate_repo.py
bash -n scripts/setup_jobs.sh
python3 -m unittest discover -s tests
```

The current suite has 96 tests and needs no network. It covers product-watch prices/stock,
blocked/private/robots access, ambiguous pages and homepage rejection, snapshot history,
delivery retries/receipts and fresh native owner approval for response codes.
Catalog feeds, sitemap samples and external monitor tests were removed with those features.

## Native research

Configure the same working Hermes web provider as your default profile (`hermes -p iris tools`).
On an upgraded profile remove the retired `web.search_backend: searxng` pin and Iris-only
`SEARXNG_URL`. Check native search and extraction with a real question, not just HTTP200.
Iris keeps browser reads and store writes restricted; copying default research settings does
not mean copying unrestricted tools or private owner memory.

Run native cases in a private copy with the installed Hermes Python:

```sh
python3 tools/evaluate_iris.py --profile-home "$CANDIDATE_HOME" \
  --hermes hermes --output "$PRIVATE_RESULTS" --isolate \
  --cases native-research exact-product honest-caption
```

Output must be a new directory. Review actual tool records, sources and replies. Raw results
can contain owner data; keep them private. Isolation removes Telegram delivery and protects
source memory/database. Read-only research does not publish a message or mutate Shopify.
Native research should use web_search/web_extract, not the structured watch reader.

## Onboarding without a merchant store

```sh
python3 tools/evaluate_iris.py --profile-home "$CANDIDATE_HOME" \
  --hermes hermes --output "$PRIVATE_RESULTS" --isolate \
  --catalog-fixture tests/fixtures/own_electronics_catalog.json
```

The fixture replaces GraphQL catalog reads only in the private profile, rejects other queries,
removes Shopify credentials, disables offers, starts empty owner memory and omits the watch
DB. Review setup confirmation, native Market profile readback, new-session and cron-toolset
recall. This is synthetic context proof, not Shopify access, Telegram transport or cron delivery.

## Owner Telegram and scheduled proof

1. Run `tools/iris_doctor.py --profile-home <candidate-home> --live` with Hermes's Python.
2. In the actual owner chat confirm the Market profile and ask one sourced competitor question.
   Check that native research works and browser actions remain blocked.
3. Approve one exact relevant product page to watch. A homepage should be rejected. If structured
   price/stock is missing, Iris explains the monitoring limit; native manual research may still work.
4. Read the baseline, then repeat with the same price/stock: no change alert. Change that product's
   supported structured price/stock on a controlled test page: one relevant alert, no duplicate
   after confirmed delivery. No full-store new-product alert is expected.
5. Check the actual scheduled offer job can use native web extraction, keeps advertised conditions
   explicit and stays silent when nothing relevant changed. Verify delivery and chat continuity.
6. For response codes, review exact proposal terms in the owner's native controls and verify
   create/readback/deactivate. A CLI, scheduled task or website cannot supply owner approval.

Do not replace legacy broad watches or delete their history silently. Ask the owner to choose
specific products. A fresh watch starts a baseline; old catalog snapshots do not prove that
new product-only monitoring covers the entire store. External monitor services/watches need
operator cleanup separately; code removal does not stop them.
