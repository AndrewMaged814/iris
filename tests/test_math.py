import unittest
import helpers  # noqa: F401
from iris_math import calculate


class MarketMath(unittest.TestCase):
    def test_lower_item_price_can_have_higher_unit_price_without_reversing_the_relation(self):
        result = calculate({"operation": "compare_products",
            "own": {"price": 320, "quantity": 50, "unit": "ml", "currency": "EGP"},
            "products": [{"name": "AVUVA", "price": 329, "quantity": 120, "unit": "ml", "currency": "EGP"},
                         {"name": "Bobai", "price": 329, "quantity": 60, "unit": "ml", "currency": "EGP"}]})
        for row in result["comparisons"]:
            scenario = row["comparison"]["scenarios"][0]
            self.assertEqual(scenario["own_upfront_price_relation_to_rival"], "less_than")
            self.assertEqual(scenario["own_unit_price_relation_to_rival"], "greater_than")
            self.assertFalse(row["comparison"]["product_equivalence_verified"])

    def test_direction_is_unknown_for_invalid_money_or_units_and_equal_after_unit_conversion(self):
        mismatch = self.basket(rival_currency="USD")["scenarios"][0]
        self.assertIsNone(mismatch["own_upfront_price_relation_to_rival"])
        self.assertIsNone(mismatch["own_unit_price_relation_to_rival"])
        mass = self.basket(rival_unit="g")["scenarios"][0]
        self.assertEqual(mass["own_upfront_price_relation_to_rival"], "less_than")
        self.assertIsNone(mass["own_unit_price_relation_to_rival"])
        equal = calculate({"operation": "compare_baskets",
            "own": {"price": 320, "quantity": 50, "unit": "ml", "currency": "EGP"},
            "rival": {"totals": [320], "quantity": .05, "unit": "l", "currency": "EGP"}})
        self.assertEqual(equal["scenarios"][0]["own_unit_price_relation_to_rival"], "equal")

    def test_different_products_keep_their_own_sizes_in_one_calculation(self):
        result = calculate({"operation": "compare_products",
            "own": {"price": 250, "quantity": 50, "unit": "ml", "currency": "EGP"},
            "products": [{"name": name, "price": price, "quantity": size, "unit": "ml", "currency": "EGP"}
                         for name, price, size in [("A", 153, 50), ("B", 120, 50), ("C", 225, 60)]]})
        self.assertEqual(result["computed_rival_price_per_unit_range"], [2.4, 3.75])
        c = result["comparisons"][2]
        self.assertEqual(c["name"], "C")
        self.assertEqual(c["comparison"]["quantity_ratio_rival_to_own"], 1.2)
        self.assertEqual(c["comparison"]["scenarios"][0]["upfront_difference_rival_minus_own"], -25)

    def test_unknown_or_incompatible_product_rows_do_not_join_normalized_range(self):
        result = calculate({"operation": "compare_products",
            "own": {"price": 320, "quantity": 50, "unit": "ml", "currency": "EGP"},
            "products": [{"name": "unknown size", "price": 216, "quantity": None, "unit": None, "currency": "EGP"},
                         {"name": "mass", "price": 200, "quantity": 50, "unit": "g", "currency": "EGP"}]})
        self.assertIsNone(result["computed_rival_price_per_unit_range"])
        self.assertEqual(result["normalized_price_comparison_count"], 0)
        self.assertEqual(result["comparisons"][0]["comparison"]["scenarios"][0]["upfront_difference_rival_minus_own"], -104)
        with self.assertRaises(ValueError):
            calculate({"operation": "compare_products", "own": {}, "products": [{"price": 120}]})
        with self.assertRaisesRegex(ValueError, "own reference basket is required separately"):
            calculate({"operation": "compare_products", "products": [{"name": "own included here by mistake", "price": 250}]})

    def basket(self, own_quantity=50, own_unit="ml", rival_quantity=120, rival_unit="ml", rival_currency="EGP"):
        return calculate({"operation": "compare_baskets",
                          "own": {"price": 320, "quantity": own_quantity, "unit": own_unit, "currency": "EGP"},
                          "rival": {"totals": [570, 285], "quantity": rival_quantity, "unit": rival_unit, "currency": rival_currency}})

    def test_actual_bundle_failure_and_both_payable_scenarios(self):
        result = self.basket()
        self.assertEqual(result["quantity_ratio_rival_to_own"], 2.4)
        self.assertEqual(result["quantity_difference_rival_minus_own"], 70)
        self.assertEqual(result["quantity_percent_more_than_own"], 140)
        self.assertEqual(result["own_price_per_normalized_unit"], 6.4)
        self.assertEqual([(r["upfront_difference_rival_minus_own"], r["rival_price_per_normalized_unit"])
                          for r in result["scenarios"]], [(250, 4.75), (-35, 2.375)])
        self.assertFalse(result["checkout_verified"])

    def test_unit_conversion_and_no_mass_to_volume_assumption(self):
        self.assertEqual(self.basket(.05, "l")["quantity_ratio_rival_to_own"], 2.4)
        self.assertIsNone(self.basket(rival_unit="g")["quantity_ratio_rival_to_own"])
        self.assertIsNone(self.basket(own_quantity=None)["quantity_ratio_rival_to_own"])

    def test_currency_mismatch_blocks_monetary_comparison_but_not_volume(self):
        result = self.basket(rival_currency="USD")
        self.assertIsNone(result["scenarios"][0]["upfront_difference_rival_minus_own"])
        self.assertEqual(result["quantity_ratio_rival_to_own"], 2.4)

    def economics(self, **changes):
        inputs = {"operation": "unit_economics", "currency": "EGP", "current_price": 320,
                  "proposed_price": 288, "unit_cost": 160, "variable_cost_per_item": 10,
                  "payment_fee_percent": 3, "minimum_to_keep": 100, "baseline_units": 4,
                  "baseline_period": "week", "offer_period": "weekend"}
        inputs.update(changes)
        return calculate(inputs)

    def test_cost_floor_and_weekend_baseline(self):
        result = self.economics()
        self.assertEqual(result["current"]["amount_after_supplied_costs"], 140.4)
        self.assertEqual(result["proposed"]["amount_after_supplied_costs"], 109.36)
        self.assertEqual(result["minimum_price_for_supplied_floor"], 278.36)
        self.assertEqual(result["additional_units_percent_to_equal_current"], 28.3833)
        self.assertEqual(result["whole_period_units_to_equal_baseline"], 6)
        self.assertIsNone(result["offer_period_target_units"])
        self.assertEqual(self.economics(offer_period="week")["offer_period_target_units"], 6)

    def test_current_only_economics_replays_missing_proposal_without_inventing_it(self):
        args = {"operation": "unit_economics", "currency": "EGP", "current_price": 320,
                "unit_cost": 160, "variable_cost_per_item": 10, "payment_fee_percent": 3,
                "minimum_to_keep": 100, "baseline_units": None, "baseline_period": "seven days"}
        result = calculate(args)
        self.assertEqual(result["current"]["amount_after_supplied_costs"], 140.4)
        self.assertEqual(result["minimum_price_for_supplied_floor"], 278.36)
        self.assertIsNone(result["proposed"])
        self.assertIsNone(result["amount_lost_per_item"])
        self.assertIsNone(result["offer_period_target_units"])
        self.assertIsNone(result["units_multiplier_to_equal_current"])
        partial = calculate({**args, "payment_fee_percent": None})
        self.assertIsNone(partial["current"]["amount_after_supplied_costs"])
        self.assertEqual(partial["current"]["price_minus_unit_cost"], 160)

    def test_missing_costs_do_not_become_zero(self):
        result = self.economics(payment_fee_percent=None)
        self.assertIsNone(result["proposed"]["amount_after_supplied_costs"])
        self.assertEqual(result["proposed"]["price_minus_unit_cost"], 128)
        self.assertIsNone(result["minimum_price_for_supplied_floor"])
        self.assertIsNone(result["additional_units_percent_to_equal_current"])

    def test_decimal_ceiling_and_nonpositive_contribution(self):
        self.assertEqual(self.economics(current_price=10, proposed_price=2.5, unit_cost=0,
                                       variable_cost_per_item=0, payment_fee_percent=0,
                                       baseline_units=3)["whole_period_units_to_equal_baseline"], 12)
        self.assertIsNone(self.economics(proposed_price=100)["whole_period_units_to_equal_baseline"])
        self.assertIsNone(self.economics(proposed_price=100)["units_multiplier_to_equal_current"])

    def test_invalid_values_are_rejected_without_execution(self):
        for value in (True, float("nan"), float("inf"), -1, "__import__('os')", []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.economics(current_price=value)
        with self.assertRaises(ValueError):
            self.economics(payment_fee_percent=100)
        with self.assertRaises(ValueError):
            self.economics(baseline_units=2.5)
