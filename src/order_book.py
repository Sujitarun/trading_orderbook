import json
import operator
from itertools import chain
from typing import Dict, List, Union, NewType

from orders import OrderInputSchema, LimitOrder


class OrderBook:

    #define two lists for buy order and sell orders.
    _order_ids = []
    _OrderTypes = NewType('orders_types', Union[LimitOrder])
    _OrdersList = NewType('orders_list', List[_OrderTypes])
    _buy_orders = _OrdersList([])
    _sell_orders = _OrdersList([])

    #Returns object in string format.
    def __repr__(self):
        return json.dumps({
            'buyOrders': [o.overview() for o in self._buy_orders],
            'sellOrders': [o.overview() for o in self._sell_orders]
        })

    #validate and create a new order 
    def new_order(self, raw_order: str) -> _OrderTypes:
        order_schema = OrderInputSchema()
        order = order_schema.loads(raw_order)
        if order.order_id in self._order_ids:
            raise Exception("duplicate order ID")
        self._order_ids.append(order.order_id)
        self._insert_order(order)
        return order
        
    #insert orders sorted as  buy_orders list with highest bid and sell_orders list with lowest ask on top 
    def _insert_order(self, new_order):
        if new_order.direction == 'buy':
            self._buy_orders.append(new_order)
            self._buy_orders.sort(key=lambda i: (
                i.price, i.timestamp), reverse=True)
        elif new_order.direction == 'sell':
            self._sell_orders.append(new_order)
            self._sell_orders.sort(key=lambda i: (
                i.price, i.timestamp), reverse=False)

    #start with the transactions to match orders  - bid order price is higher than ask price.
    def make_transactions(self, order: _OrderTypes) -> List[Dict]:
        executed_transaction = self._exhaust_order(order)
        transactions = list(chain(executed_transaction))
        return transactions
    
    #match orders  and execute them- bid order price is higher than ask price.
    def _exhaust_order(self, order, transactions=[]):
        opposite_orders = self._sell_orders if order.direction == 'buy' else self._buy_orders
        for opposite_order in opposite_orders:
            buy_order, sell_order = self._categorize_orders(
                order, opposite_order)
            if buy_order >= sell_order:
                transactions.append(
                    self._execute_transaction(buy_order, sell_order))

                if order.quantity > 0:
                    transactions = self._exhaust_order(
                        order, transactions)

        return transactions
    
    #determine the order direction for given 2 orders.
    def _categorize_orders(self, order1, order2):
        if order1.direction == 'buy':
            buy_order = order1
            sell_order = order2
        else:
            buy_order = order2
            sell_order = order1
        return buy_order, sell_order

    def _execute_transaction(self, buy_order, sell_order):
        if buy_order.quantity <= sell_order.quantity:
            quantity_exchanged = buy_order.quantity
        else:
            quantity_exchanged = buy_order.quantity - sell_order.quantity

        buy_order.quantity -= quantity_exchanged
        sell_order.quantity -= quantity_exchanged

        self._update_order_after_transaction(buy_order)
        self._update_order_after_transaction(sell_order)

        return {
            "buyOrderId": buy_order.order_id,
            "sellOrderId": sell_order.order_id,
            "price": buy_order.price,
            "quantity": quantity_exchanged
        }

    def _update_order_after_transaction(self, order: _OrderTypes):
        if order.quantity == 0:
            self._delete_order_with_zero_quantity(order)

    def _delete_order_with_zero_quantity(self, order):
        try:
            if order.direction == 'buy':
                idx = self._buy_orders.index(order)
                self._buy_orders.pop(idx)
            elif order.direction == 'sell':
                idx = self._sell_orders.index(order)
                self._sell_orders.pop(idx)
        except:
            pass
