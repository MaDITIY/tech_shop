import os

from app import app
from app.models import Order


def generate_order_text(order):
    reciept = f"Receipt from TechShop company:\r\n"+ \
            "----------------------------------\r\n"+\
            f"Product type: {order.product.type.name}\r\n"+\
            f"Product Model: {order.product.model}\r\n"+\
            f"Time of deal: {order.date}\r\n"+\
            f"Product count: {order.count}\r\n"+\
            f"Product cost: {order.product.price}\r\n"+\
            f"Total cost: {order.price} $\r\n"+\
            "----------------------------------\r\n"+\
            "Thank you!"
    return reciept



def generate_reciept(order):
    with open(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'reciept.txt'), 'w') as file:
        file.write(generate_order_text(order))
