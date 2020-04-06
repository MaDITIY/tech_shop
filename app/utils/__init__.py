import os

from app import app, db
from app.models import User, Type, Manufacturer, Product
from flask import abort, flash
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


def add_product(model, type, manufacturer, price, count=None):
    type_id = Type.query.filter(
        Type.name == type
    ).first().id
    product = Product.query.filter(
        Product.model == model,
        Product.type_id == type_id
    ).first()
    if product is None:
        manufacturer_id = Manufacturer.query.filter(
            Manufacturer.name == manufacturer
        ).first().id
        product = Product(
            model=model,
            type_id=type_id,
            manufacturer_id=manufacturer_id,
            count=count or 0,
            price=price
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product \'{model}\' of type {type} was successfully created')
    else:
        flash('We already have such product. Please choose another model name')


def delete_types(type_ids):
    types = Type.query.filter(
        Type.id.in_(type_ids)
    ).all()
    for type in types:
        db.session.delete(type)
    db.session.commit()


def delete_manufacturers(manufacturer_ids):
    manufacturers = Manufacturer.query.filter(
        Manufacturer.id.in_(manufacturer_ids)
    ).all()
    for manufacturer in manufacturers:
        db.session.delete(manufacturer)
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