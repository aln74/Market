from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    #purchase item logic
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        purchased_item_name = request.form.get('purchased_item')
        purchased_item = Item.query.filter_by(name=purchased_item_name).first()
        if purchased_item:
            if current_user.can_purchase(purchased_item):
                purchased_item.owner = current_user.id #should turn this into a method in models.py
                current_user.budget -= purchased_item.price
                db.session.commit()
                flash(f'Purchased {purchased_item.price} successful!', category='success')
            else:
                flash('Insufficient funds :(', category='danger')

        #sell item logic
        sold_item_name = request.form.get('sold_item')
        sold_item = Item.query.filter_by(name=sold_item_name).first()
        if sold_item:
            if current_user.can_sell(sold_item):
                sold_item.owner = None
                current_user.budget += sold_item.price
                db.session.commit()
                flash(f'Sold {sold_item} to market successfully!', category='success')
            else:
                flash('You do not own this item :/', category='danger')

        return redirect(url_for('market_page'))
    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit(): #first validates the information and then activates the condition on submit
        user_to_create = User(username=form.username.data,
        email_address=form.email_address.data,
        password = form.password1.data,)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account create successfully! You are now loggin in as {user_to_create.username}', category='success')

        return redirect(url_for('market_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username or Password is incorrect. Please try again', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('home_page'))