import os

from app import app, db
from app.models import User, Order, Product, Type, Roles, Manufacturer
from app.forms import LoginForm, RegistrationForm, EditProfileForm, OrderForm
from app.utils import admin_required, generate_reciept, \
    set_role, delete_users, delete_types, delete_manufacturers, add_product
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
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter(
        Order.user_id == user.id
    ).order_by(Order.date.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('user', username=current_user.username, page=orders.next_num) \
        if orders.has_next else None
    prev_url = url_for('user', username=current_user.username, page=orders.prev_num) \
        if orders.has_prev else None
    return render_template(
        'user.html', user=user, orders=orders.items,
        next_url=next_url, prev_url=prev_url
    )


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
            user_id=current_user.id,
            product=product,
            count=count,
            price=product.price * count
        )
        product.count -= count
        db.session.add(order)
        db.session.commit()
        generate_reciept(order)
        uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        flash('You successfully bought {}'.format(product.model))
        if form.get_reciept.data:
            return send_from_directory(directory=uploads, filename='reciept.txt', as_attachment=True)
        return render_template(
            'order.html', title='Order Page', form=form
        )
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
    page = request.args.get('page', 1, type=int)

    type = Type.query.filter(
        Type.name == product_name
    ).one()
    products = Product.query.filter(
        Product.type_id == type.id
    ).order_by(Product.model).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('product', product_name=product_name, page=products.next_num) \
        if products.has_next else None
    prev_url = url_for('product', product_name=product_name, page=products.prev_num) \
        if products.has_prev else None
    return render_template(
        'product.html', title='{} page'.format(product_name),
        products=products.items, next_url=next_url, prev_url=prev_url)


@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('admin.html', title='Admin Page')


@app.route('/admin/manufacturers', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_manufacturers():
    if request.method == 'POST':
        ids = request.form.getlist('manufacturers')
        delete_manufacturers(ids)
    manufacturers = Manufacturer.query.all()
    return render_template('manage_manufacturers.html', title='Admin Page', manufacturers=manufacturers)


@app.route('/admin/create_manufacturer', methods=['GET', 'POST'])
@login_required
@admin_required
def create_manufacturer():
    if request.method == 'POST':
        name = request.form['name'].lower()
        ambassador = request.form['ambassador']
        manufacturer = Manufacturer.query.filter(
            Manufacturer.name == name
        ).first()
        if manufacturer is None:
            manufacturer = Manufacturer(
                name=name,
                ambassador=ambassador
            )
            db.session.add(manufacturer)
            db.session.commit()
            flash(f'Manufacturer \'{name}\' was successfully added')
        else:
            flash('We already have such manufacturer. No need to add')
    return render_template('create_manufacturer.html', title='Create Product Type')


@app.route('/admin/types', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_types():
    if request.method == 'POST':
        ids = request.form.getlist('types')
        delete_types(ids)
    types = Type.query.all()
    return render_template('manage_types.html', title='Admin Page', types=types)


@app.route('/admin/create_product_type', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product_type():
    if request.method == 'POST':
        name = request.form['name'].lower()
        type = Type.query.filter(
            Type.name == name
        ).first()
        if type is None:
            type = Type(name=name)
            db.session.add(type)
            db.session.commit()
            flash(f'Product type \'{name}\' was successfully created')
        else:
            flash('We already have such product type. Please choose another name')
    return render_template('create_product_type.html', title='Create Product Type')


@app.route('/admin/create_product', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    types = Type.query.all()
    manufacturers = Manufacturer.query.all()
    if request.method == 'POST':
        model = request.form['model'].lower()
        type = request.form['type']
        manufacturer = request.form['manufacturer']
        count = request.form.get('count')
        price = request.form['price']
        add_product(
            model=model,
            type=type,
            manufacturer=manufacturer,
            price=price,
            count=count
        )
    return render_template(
        'create_product.html', title='Create Product Type',
        types=types, manufacturers=manufacturers
    )


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    if request.method == 'POST':
        ids = request.form.getlist('users')
        if 'admin' in request.form:
            set_role(ids, Roles.Admin)
        if 'reader' in request.form:
            set_role(ids, Roles.Reader)
        if 'delete' in request.form:
            delete_users(ids)
    users = User.query.all()
    return render_template('manage_users.html', title='Admin Page', users=users)


