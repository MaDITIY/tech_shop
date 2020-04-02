import os

from app import app, db
from app.models import User, Order, Product, Type
from app.forms import LoginForm, RegistrationForm, EditProfileForm, OrderForm
from app.utils import generate_reciept
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/catalog')
def catalog():
    types = Type.query.all()
    return render_template('catalog.html', title='Catalog', types=types)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('catalog')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('catalog'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template(
        'edit_profile.html', title='Edit Profile', form=form
    )

@app.route('/order', methods=['GET', 'POST'])
@login_required
def get_order():
    choises = [(type.name, type.name) for type in Type.query.all()]
    form = OrderForm(choises)
    if form.validate_on_submit():
        type = Type.query.filter(
            Type.name == form.product_type.data
        ).one()
        model = form.model.data
        product = Product.query.filter(
            Product.model == model,
            Product.type_id == type.id
        ).first()
        if product is None:
            flash('Sorry, we don\'t have such product. Please check input fields')
            return render_template(
                'order.html', title='Order Page', form=form
            )
        count = int(form.product_count.data)
        if product.count < count:
            flash(
                'Currently we don\'t have so much products. '
                'Please choose smaller number. '
                'We will buy more in some time'
            )
            return render_template(
                'order.html', title='Order Page', form=form
            )
        order = Order(
            customer=current_user,
            product=product,
            price=product.price * count
        )
        db.session.add(order)
        db.session.commit()
        generate_reciept(order)
        uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        return send_from_directory(directory=uploads, filename='reciept.txt', as_attachment=True)
        flash('You successfully bought {}'.format(order))
        return redirect(url_for('get_order'))
    elif request.method == 'GET':
        model = request.args.get('model')
        type = request.args.get('type')
        if model and type:
            form.model.data = model
            form.product_type.data = type
    return render_template(
        'order.html', title='Order Page', form=form
    )


@app.route('/product/<product_name>')
@login_required
def product(product_name):
    type = Type.query.filter(
        Type.name == product_name
    ).one()
    products = Product.query.filter(
        Product.type_id == type.id
    ).all()
    return render_template('product.html', title='{} page'.format(product_name), products=products)