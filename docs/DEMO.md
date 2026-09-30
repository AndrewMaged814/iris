# See Iris work

Verified on 30 September 2026 with Luna through Azure Foundry. Mira Nile is a synthetic skincare
catalog. Public competitor facts were live reads, and simulated action results are labelled below.

## A price comparison that notices the offer

Ask: “Check this exact sunscreen's size, skin type, price and current offers.”

The original reader returned a whole catalog for an exact product link. Iris could not verify the
size from the official page and missed an advertised multi-buy offer. After the reader correction,
the exact official page supplied 50 ml, oily/combination skin, LE 360 and the advertised 2+2 offer.
Checkout conditions remained unverified. Source:
[Infinity's Arabic product page](https://infinityclinicpharma.com/ar/products/naturals-sun-screen-gel-spf-50-oily-skin).

## A factual product-page fix

Ask: “Review my sunscreen photo, size and price. Give me one useful factual fix.”

Before: Iris could see 50 ml and EGP 320, but needed a screenshot to inspect the image.

After: Iris read the image metadata, used native vision, and found that the existing photo had no
saved alt text. She suggested: “Synthetic demo: Mira Nile Sunscreen SPF 50 tube, 50 ml.” No conversion
claim or store edit was made. This is an observed listing gap, not proof of lost orders.

## From a chosen action to its result

Four separate native sessions exercised Hermes memory:

| Step | Actual result |
| --- | --- |
| Owner chooses the size-clarity edit | Saved as planned, unpublished and simulated, with drafting minutes as the measure |
| Weekly follow-up with scheduled toolsets | Recalled the correct move and asked whether it was used and how much drafting time it saved; no memory write |
| Owner reports the simulated result | Recorded the period, three orders, EGP 960 gross sales and five drafting minutes versus a stated twenty-minute baseline |
| Next review in another session | Recalled the reported fifteen minutes saved, retained simulation/source limits and did not ask again for the supplied result |

Iris explicitly rejected interpreting EGP 960 gross sales as profit or proof that the draft caused
orders. These are simulated reports, not a real merchant result or a measured time-saving claim.

## Scheduled Telegram delivery

The installed weekly job was run through Hermes on 30 September 2026 at 03:39 Cairo time. Its
durable execution record was `completed`, with delivery outcome `delivered` and no error.
The reply correctly said one check was a baseline, gave the Cairo date and linked Infinity.
The Sunday 10:00 schedule remains active. Platform delivery is not proof the owner read the message.

The existing daily job also completed at 03:48 Cairo time. No urgent change was found; its script
returned the no-wake gate and delivery outcome was `suppressed`. The 08:00 schedule remains active.
This added a genuine second observation; the two checks cover about ninety minutes, not a whole week.

This test used the real scheduled job and Telegram delivery. The action/memory simulations used
a private isolated profile copy and did not change the owner's live memory or send Telegram messages.
An updated full owner action conversation and a real SME pilot remain open checks.

## Reproduce the business cases

Use Hermes' Python environment. A new private output directory is required:

```sh
python tools/evaluate_iris.py --profile-home ~/.hermes/profiles/iris --output ~/iris-evaluations/demo --isolate
```

There are fifteen reusable cases. Each records expected criteria, the exact response, native tool
transcript, profile file hashes, timing, session ID and available usage data. Live prices and stock
are observations, not frozen fixtures. Review the evidence manually; the runner does not grade
answer quality. Action cases require isolation, and the isolated copy has no Telegram bot token.

Raw records contain owner data and private runtime configuration; keep the output outside Git.
Use [TESTING.md](TESTING.md) for offline and host checks and [PRODUCT.md](PRODUCT.md) for the real pilot.

## A price cut with its business cost

Hypothetical inputs: selling price EGP 320, cost EGP 190, packaging EGP 20 and payment fee 3%.
At EGP 299, Iris calculated contribution falling from EGP 100.40 to EGP 80.03 per bottle:
EGP 20.37 less, requiring about 25.5% more units to preserve total contribution. She kept the
assumptions explicit and did not infer extra demand or real sales.

The bulk-offer case also rejected an unqualified cheaper claim: the advertised EGP 360, buy-two-
get-two deal would be EGP 720 for four bottles if eligible, compared with EGP 1280 for four demo
Mira bottles. Single-bottle prices and conditional offers were kept separate. Checkout and a
complete product match remain unverified. [Read the case assessments](EVALUATION.md).
