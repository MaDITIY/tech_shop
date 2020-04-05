import os

from app import app, db
from app.models import User, Roles
from flask import abort
from flask_login import current_user
from functools import wraps


def set_role(user_ids, role):
    users = User.query.filter(
        User.id.in_(user_ids)
    )
    for user in users:
        user.role = role
    db.session.commit()


def delete_users(user_ids):
    users = User.query.filter(
        User.id.in_(user_ids)
    ).all()
    for user in users:
        db.session.delete(user)
    db.session.commit()


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


def admin_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return func(*args, **kwargs)
    return wrap