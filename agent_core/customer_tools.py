import json
from datetime import datetime
from typing import Dict, Optional
import pytz
from .base_tool import BaseTool

class GetOrderStatusTool(BaseTool):
    def get_missing_argument_prompt(self, arguments: Dict) -> Optional[str]:
        if not arguments.get("order_number") and not arguments.get("email"):
            return "What is your order number and email address?"
        if not arguments.get("order_number"):
            return "What is your order number?"
        if not arguments.get("email"):
            return "What is the email address associated with this order?"
        if not arguments.get("name"):
            return "What is the customer name associated with this order?"
        return None

    def get_response_instructions(self) -> str:
        return """
        When you are given information that includes a tracking number or a tracking link, you MUST format it to be easy to copy.
        Place the tracking number and/or the tracking link on its own line, prefixed with a label.

        Example:
        Your order has been delivered.
        Tracking Number: TRK123456789
        Tracking Link: https://tools.usps.com/go/TrackConfirmAction?tLabels=TRK123456789

        Do not give out any more information. Only give order status, tracking number and trackling link.
        """

    def execute(self, order_number: str, email: str, name: str, **kwargs) -> str:
        order_number = order_number.strip().upper()
        if not order_number.startswith('#'):
            order_number = f"#{order_number}"

        email = email.strip().lower()

        with open('data/orders.json', 'r') as f:
            orders = json.load(f)
        
        for order in orders:
            if order.get("OrderNumber") == order_number and order.get("Email").strip().lower() == email and order.get("CustomerName").strip().lower() == name:
                tracking_number = order.get("TrackingNumber")
                if tracking_number:
                    order["TrackingURL"] = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
                return json.dumps(order)
                
        return json.dumps({"error": "Order not found or email does not match."})

class GetProductRecommendationTool(BaseTool):
    def get_missing_argument_prompt(self, arguments: Dict) -> Optional[str]:
        if not arguments.get("query"):
            return "What products are you interested in? You can tell me a category or a specific product name!"
        return None

    def get_response_instructions(self) -> str:
        return """
        Answer customer questions based off of product catalogue. Search for products in ProductName, Description or Tags fields.
        If a specific product was found, provide its details clearly.
        If multiple recommendations are found, list them clearly.

        Example:
        1. Product: Backcountry Backpack
        Description: Rugged and durable backpack.

        Do not give out any more information. Only give product name and description.
        """
   
    def execute(self, query: str, **kwargs) -> str:
        with open('data/products.json', 'r') as f:
            products = json.load(f)
        
        search_query = query.strip().lower()
        
        # First, try to find an exact match for a product name
        for p in products:
            if p.get("ProductName", "").strip().lower() == search_query:
                return json.dumps(p) # Return the single product found
        
        # If no exact match, proceed with general recommendations
        recommendations = []
        for p in products:
            in_name = search_query in p.get("ProductName", "").lower()
            in_description = search_query in p.get("Description", "").lower()
            # Tags is a list, so we check if the query is in any of the tags.
            in_tags = any(search_query in tag.lower() for tag in p.get("Tags", []))
            
            if in_name or in_description or in_tags:
                recommendations.append(p)
        
        if recommendations:
            return json.dumps(recommendations)
            
        return json.dumps({"error": f"No products found matching '{search_query}'."})

class GetEarlyRiserPromotionTool(BaseTool):
    def get_missing_argument_prompt(self, arguments: Dict) -> Optional[str]:
        return None # This tool requires no arguments

    def execute(self, **kwargs) -> str:
        pacific_tz = pytz.timezone('America/Los_Angeles')
        # gmt_tz = pytz.timezone('Europe/London')
        valid_promo_start = datetime.now(pacific_tz)
        
        if 8 <= valid_promo_start.hour < 10:
            return json.dumps({
                "promotion": "Early Riser Discount",
                "discount_code": "EARLYBIRD10",
                "discount_value": "10%"
            })
        return json.dumps({"message": "Sorry, the Early Riser promotion is only active from 8 AM to 10 AM Pacific Time."})