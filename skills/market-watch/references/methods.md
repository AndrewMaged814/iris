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

Shopify's public feed has no currency. If a store sells in the owner's country, use the owner's
currency from `my_store` and say "prices in EGP" once. If you can't tell, say the currency is unknown
instead of guessing.
