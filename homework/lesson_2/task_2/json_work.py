import json


def write_order_to_json(item, quantity, price, buyer, date):
    data = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }

    with open('orders.json') as f:
        objects = json.load(f)

    with open('orders.json', 'w') as f:
        for k, v in objects.items():
            v.append(data)
        json.dump(objects, f, indent=4)


write_order_to_json(1, 1, 2, 3, 4)
write_order_to_json(1, 1, 2, 3, 4)