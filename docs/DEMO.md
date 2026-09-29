# Demo (2–3 minutes)

Everything runs on the test site (`iris-test-world`), a simulated market. Say so in the video.

1. **Setup.** Tap Start. Iris reads Mira Nile's catalog, suggests Glow Lab, Nile Beauty and Cairo Skin,
   and you approve all three.
2. **A question.** "What are serums selling for right now?" Iris gives the price range by product type
   and where Mira Nile sits.
3. **The overnight alert.** Edit `glow-lab/products.json`: give the Hydra Toner a sale price
   (`compare_at_price` above `price`). Wait for the daily check (demo schedule). Iris messages first:
   the promotion, what it means for your toner, and an offer to draft a post. Say yes; she writes it in Arabic.
4. **A screenshot.** Send a picture of a competitor's Instagram offer. Iris reads it, relates it to your
   products and saves it for the weekly message.
5. **The surprise.** Cairo Skin lists *your* Rose Serum with the wrong size. Iris notices it in the watched
   store and tells you, with a short reply you can give customers.
6. **The week.** Trigger the weekly job (`hermes -p iris cron run <weekly job id>`; the ID is in `hermes -p iris cron list`): "This week in your market".

Before recording: run the doctor with `--live`, measure how long GitHub Pages takes to show an edit,
and tap Start once to confirm the gateway is up.
