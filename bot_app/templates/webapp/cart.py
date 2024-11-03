# cart.py

class Cart:
    def __init__(self):
        self.items = {}

    def add_item(self, product_id, quantity):
        if product_id in self.items:
            self.items[product_id] += quantity
        else:
            self.items[product_id] = quantity

    def decrease_item(self, product_id):
        if product_id in self.items and self.items[product_id] > 1:
            self.items[product_id] -= 1

    def increase_item(self, product_id):
        if product_id in self.items:
            self.items[product_id] += 1

    def get_cart_items(self):
        return self.items
