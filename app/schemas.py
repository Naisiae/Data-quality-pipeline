"""Expected data structure for the dataset we validate.

Keeping the rules here (not buried in the logic) means you can validate a
different dataset by editing this file only.
"""

EXPECTED_SCHEMA = {
    "order_id": {"type": "int", "required": True, "unique": True},
    "customer_name": {"type": "str", "required": True},
    "email": {"type": "email", "required": True},
    "country": {"type": "str", "required": True,
                "allowed": ["Kenya", "Uganda", "Tanzania", "Rwanda"]},
    "quantity": {"type": "int", "required": True, "min": 1, "max": 1000},
    "unit_price": {"type": "float", "required": True, "min": 0.01},
    "order_date": {"type": "date", "required": True},
}
