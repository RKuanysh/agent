import unittest
import json
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import pytz

from agent_core.customer_tools import GetOrderStatusTool, GetProductRecommendationTool, GetEarlyRiserPromotionTool

# python -m tests.test_customer

# --- Test Data ---

mock_orders_data = json.dumps([
    {
        "CustomerName": "John Doe",
        "Email": "john.doe@example.com",
        "OrderNumber": "#W001",
        "ProductsOrdered": ["SOBP001", "SOWB004"],
        "Status": "delivered",
        "TrackingNumber": "TRK123456789"
    }
])

mock_products_data = json.dumps([
    {
        "ProductName": "Bhavish's Backcountry Blaze Backpack",
        "SKU": "SOBP001",
        "Tags": ["Backpack", "Hiking"]
    },
    {
        "ProductName": "Beth's Caffeinated Energy Drink",
        "SKU": "SOWB004",
        "Tags": ["Food & Beverage"]
    },
    {
        "ProductName": "Nat's Infinity Pro Hairbrush",
        "SKU": "SOBT003",
        "Tags": ["Hiking", "Comfort"]
    }
])


class TestGetOrderStatusTool(unittest.TestCase):

    def setUp(self):
        self.tool = GetOrderStatusTool()

    def test_get_missing_argument_prompt(self):
        self.assertEqual(self.tool.get_missing_argument_prompt({}), "What is your order number?")
        self.assertEqual(self.tool.get_missing_argument_prompt({"order_number": "#W001"}), "What is the email address associated with this order?")
        self.assertIsNone(self.tool.get_missing_argument_prompt({"order_number": "#W001", "email": "test@test.com"}))

    @patch("builtins.open", new_callable=mock_open, read_data=mock_orders_data)
    def test_execute_order_found(self, mock_file):
        result_str = self.tool.execute(order_number="#W001", email="john.doe@example.com")
        result = json.loads(result_str)
        self.assertEqual(result["OrderNumber"], "#W001")
        self.assertEqual(result["Status"], "delivered")
        self.assertIn("TrackingURL", result)
        self.assertEqual(result["TrackingURL"], "https://tools.usps.com/go/TrackConfirmAction?tLabels=TRK123456789")

    @patch("builtins.open", new_callable=mock_open, read_data=mock_orders_data)
    def test_execute_order_number_normalization(self, mock_file):
        # Test with lowercase and no '#'
        result_str = self.tool.execute(order_number="w001", email="john.doe@example.com")
        result = json.loads(result_str)
        self.assertEqual(result["OrderNumber"], "#W001")

    @patch("builtins.open", new_callable=mock_open, read_data=mock_orders_data)
    def test_execute_order_not_found(self, mock_file):
        result_str = self.tool.execute(order_number="#W999", email="jane.doe@example.com")
        result = json.loads(result_str)
        self.assertEqual(result, {"error": "Order not found or email does not match."})

    def test_get_response_instructions(self):
        # Simple test to ensure it returns a non-empty string
        self.assertIsInstance(self.tool.get_response_instructions(), str)
        self.assertIn("Tracking Number", self.tool.get_response_instructions())


class TestGetProductRecommendationTool(unittest.TestCase):

    def setUp(self):
        self.tool = GetProductRecommendationTool()

    def test_get_missing_argument_prompt(self):
        self.assertEqual(self.tool.get_missing_argument_prompt({}), "What products are you interested in? You can tell me a category or a specific product name!")
        self.assertIsNone(self.tool.get_missing_argument_prompt({"query": "backpack"}))

    @patch("builtins.open", new_callable=mock_open, read_data=mock_products_data)
    def test_execute_exact_product_match(self, mock_file):
        query = "Bhavish's Backcountry Blaze Backpack"
        result_str = self.tool.execute(query=query)
        result = json.loads(result_str)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["ProductName"], query)

    @patch("builtins.open", new_callable=mock_open, read_data=mock_products_data)
    def test_execute_category_match(self, mock_file):
        query = "hiking"
        result_str = self.tool.execute(query=query)
        result = json.loads(result_str)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        # Check that both products with "Hiking" tag are returned
        product_names = {p["ProductName"] for p in result}
        self.assertIn("Bhavish's Backcountry Blaze Backpack", product_names)
        self.assertIn("Nat's Infinity Pro Hairbrush", product_names)

    @patch("builtins.open", new_callable=mock_open, read_data=mock_products_data)
    def test_execute_no_match(self, mock_file):
        query = "nonexistent"
        result_str = self.tool.execute(query=query)
        result = json.loads(result_str)
        self.assertEqual(result, {"error": f"No products found matching '{query}'."})

    def test_get_response_instructions(self):
        self.assertIsInstance(self.tool.get_response_instructions(), str)
        self.assertIn("product name and description", self.tool.get_response_instructions())


class TestGetEarlyRiserPromotionTool(unittest.TestCase):

    def setUp(self):
        self.tool = GetEarlyRiserPromotionTool()
        self.pacific_tz = pytz.timezone('America/Los_Angeles')

    def test_get_missing_argument_prompt(self):
        self.assertIsNone(self.tool.get_missing_argument_prompt({}))

    @patch('agent_core.customer.datetime')
    def test_execute_during_promo_time(self, mock_datetime):
        # Mock the time to be 9:30 AM Pacific Time
        mock_now = self.pacific_tz.localize(datetime(2023, 1, 1, 9, 30))
        mock_datetime.now.return_value = mock_now

        result_str = self.tool.execute()
        result = json.loads(result_str)

        self.assertEqual(result, {
            "promotion": "Early Riser Discount",
            "discount_code": "EARLYBIRD10",
            "discount_value": "10%"
        })

    @patch('agent_core.customer.datetime')
    def test_execute_outside_promo_time_before(self, mock_datetime):
        # Mock the time to be 7:00 AM Pacific Time
        mock_now = self.pacific_tz.localize(datetime(2023, 1, 1, 7, 0))
        mock_datetime.now.return_value = mock_now

        result_str = self.tool.execute()
        result = json.loads(result_str)

        self.assertEqual(result, {
            "message": "Sorry, the Early Riser promotion is only active from 8 AM to 10 AM Pacific Time."
        })

    @patch('agent_core.customer.datetime')
    def test_execute_outside_promo_time_after(self, mock_datetime):
        # Mock the time to be 11:01 AM Pacific Time
        mock_now = self.pacific_tz.localize(datetime(2023, 1, 1, 10, 1))
        mock_datetime.now.return_value = mock_now

        result_str = self.tool.execute()
        result = json.loads(result_str)

        self.assertEqual(result, {
            "message": "Sorry, the Early Riser promotion is only active from 8 AM to 10 AM Pacific Time."
        })

    @patch('agent_core.customer.datetime')
    def test_execute_at_promo_start_boundary(self, mock_datetime):
        # Mock the time to be exactly 8:00 AM Pacific Time
        mock_now = self.pacific_tz.localize(datetime(2023, 1, 1, 8, 0))
        mock_datetime.now.return_value = mock_now

        result_str = self.tool.execute()
        result = json.loads(result_str)

        self.assertIn("promotion", result)

    @patch('agent_core.customer.datetime')
    def test_execute_at_promo_end_boundary(self, mock_datetime):
        # Mock the time to be exactly 11:00 AM Pacific Time (which is outside the < 11 condition)
        mock_now = self.pacific_tz.localize(datetime(2023, 1, 1, 11, 0))
        mock_datetime.now.return_value = mock_now

        result_str = self.tool.execute()
        result = json.loads(result_str)

        self.assertIn("message", result)


if __name__ == '__main__':
    unittest.main()