from datetime import datetime

from marshmallow import fields, Schema, validates, ValidationError, post_load

#Schema to define a order.Field with required=True are mandatory. 
class OrderDetailsSchema(Schema):
    id = fields.Integer(required=True)
    quantity = fields.Integer(required=True)
    price = fields.Integer(required=True)
    direction = fields.Str(required=True)


    @validates('direction')
    def check_order_type(self, value):
        if value.lower() not in ['buy', 'sell']:
            ValidationError("unsupported order direction")

#scheme which can be extended to validate other attributes or sub types of orders e.g limit order, market order, etc.
class OrderInputSchema(Schema):
    type = fields.Str(required=True)
    order = fields.Nested(OrderDetailsSchema, required=True)

    @post_load
    def make_order(self, data, **kwargs):
        if (t := data['type'].lower()) == 'limit':
            return LimitOrder(**data['order'])

# Order class and methods to compare price of two order objects.
class Order:
    def __lt__(self, other):
        return self.price < other.price

    def __le__(self, other):
        return self.price <= other.price

    def __eq__(self, other):
        return self.price == other.price

    def __ne__(self, other):
        return self.price != other.price

    def __ge__(self, other):
        return self.price >= other.price

    def __gt__(self, other):
        return self.price > other.price

    def overview(self):
        return dict(
            id=self.order_id, quantity=self.quantity, price=self.price
        )

    def debug(self):
        return str(self.__dict__)


class LimitOrder(Order):
    order_id = None
    quantity = None
    price = None
    direction = None
    timestamp = None

    def __init__(self, id, quantity, price, direction):
        self.order_id = id
        self.quantity = quantity
        self.price = price
        self.direction = direction.lower()
        self.timestamp = datetime.now()

