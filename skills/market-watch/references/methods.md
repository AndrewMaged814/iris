# Reading the market

Adapted from FlatNine ecommerce-skills (pricing-intel, trend-alert; MIT).

## Price picture by product type

- Use `by_type` from the tools: count, lowest, median and highest price, how many are on sale or out of stock.
- Say where the owner sits: below the median, around it, or in the top part of the range.
- Small samples (fewer than 5 products) are hints, not a picture. Say so.
- Leave out obvious outliers (a price of 0, or 10 times the median, is usually a bundle or an error).

## Trend or noise?

- **Confirmed:** the same change at 2 or more watched stores, or repeated over 2 or more weeks.
- **Emerging:** one store, new this week, in the owner's product types.
- **Noise:** under 5% price moves, one-day changes that flipped back, products outside the owner's types.

Report confirmed and emerging. Leave noise out.

## Missing currency

Shopify's public feed omits currency. The reader can confirm it using first-party store metadata
and a product page with the same price and currency. Use that confirmed currency. If missing,
read the relevant product page before comparing prices; retain its own price and currency together.
If still unknown, give the raw number with that limitation and omit relative price judgments.
Shared location alone doesn't confirm currency.
