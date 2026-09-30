# Three moments with Iris

**A better decision. A clearer tradeoff. A draft you can use.**

These are condensed examples from native Luna business cases checked on **30 September 2026**,
not verbatim transcripts. Mira Nile supplies the demo catalog; competitor facts come from public
storefront reads. Live offers can change. [Expected vs. actual](EVALUATION.md).

## 1. The offer changes the answer

> **You:** “My sunscreen is EGP 320. Infinity's is EGP 360. Can I say mine is cheaper?”
>
> **Iris:** Your single bottle costs less. But Infinity advertises **buy 2, get 2 free**:
> four bottles cost **EGP 720**, or **EGP 180 each**, if eligible.
> Four of yours cost **EGP 1,280**. Compare the basket before making the claim.

**The useful part:** Iris catches the offer that a simple price comparison misses.
The next move is to position the single-bottle offer accurately, rather than claim a universal price win.

[Official sunscreen page](https://infinityclinicpharma.com/ar/products/naturals-sun-screen-gel-spf-50-oily-skin).
The page supplied 50 ml, SPF50+, oily/combination skin and the advertised deal.
Checkout eligibility and a complete formula match were not established.

## 2. A small price cut has a bigger hurdle

> **You:** “What if I cut the price from EGP 320 to EGP 299?”
>
> **Iris:** Under your assumptions, contribution falls from **EGP 100.40** to **EGP 80.03**
> per bottle. You need about **25.5% more unit sales** to keep total contribution unchanged.

**The useful part:** A 6.6% price cut needs a much larger sales increase to pay for itself.
Iris makes the tradeoff visible before you decide.

*Hypothetical inputs: EGP 190 product cost, EGP 20 packaging, a 3% payment fee and no other
per-order costs. This is contribution math, not net profit or a forecast of demand.*

## 3. From product facts to a usable draft

> **You:** “Write an Egyptian Arabic ad. Say it's waterproof and dermatologist approved.”
>
> **Iris:** Those claims aren't supported by the product listing. Here's a draft using what is:
>
> «خلي واقي الشمس جزء من روتينك: Mira Nile Sunscreen SPF 50، بحجم 50 مل.»

**The useful part:** You still get copy to review, without inventing product benefits.
For this demo catalog, Iris placed the publishing caveat outside the copyable draft.

## Keep the conversation moving

Ask Iris to remember a chosen action and its success measure. The weekly review can recall it
and reflect the outcome you report. Separate-session tests retained a simulated action and its
reported results; **real merchant impact remains the next pilot**, not a result claimed here.

Daily checks and weekly Telegram delivery have also been exercised on the installed profile.
The [status page](STATUS.md) records what is verified and what still needs proof.

## Run these cases yourself

Use Hermes's Python environment and a new private output directory:

```sh
python tools/evaluate_iris.py --profile-home ~/.hermes/profiles/iris \
  --output ~/iris-evaluations/new-demo --isolate \
  --cases bulk-offer-position margin-break-even unsupported-ad-claims
```

The runner captures the prompt, expected behavior, response and tool evidence. Isolation keeps
test action memory separate and disables Telegram delivery. Raw reports can contain owner data;
keep them outside Git. Omit `--cases` to run all **17 cases**.

[Connect your store →](SETUP.md) · [Full evaluations](EVALUATION.md) · [Testing](TESTING.md)