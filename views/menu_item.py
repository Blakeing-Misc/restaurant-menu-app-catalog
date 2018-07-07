
# -*- encoding: utf-8 -*-
from flask import Blueprint, request, render_template, redirect
from flask import url_for, flash
from flask import session as login_session
from sqlalchemy import asc, exc
from models.restaurant import Restaurant
from models.menu_item import MenuItem
from views.user import get_user_info, create_user, get_user_id
from database import session
from functools import wraps


menu_item = Blueprint('menu_item', __name__)


def login_required(f):
    """
    If a user is logged in, perform the normal action.
    Otherwise, send them to the login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(request.url)
        if 'username' not in login_session:
            flash(
                "The url %s is not available "
                "unless you are logged in!" % request.url
            )
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated_function


# Create a new restaurant


@menu_item.route('/restaurant/new/', methods=['GET', 'POST'])
@login_required
def new_restaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newRestaurant)
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        session.commit()
        return redirect(url_for('restaurant.show_restaurants'))
    else:
        return render_template('newRestaurant.html')

# Edit a restaurant


@menu_item.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_restaurant(restaurant_id):
    try:
        edited_restaurant = session.query(
            Restaurant).filter_by(
            id=restaurant_id
        ).one()
    except:
        return "No such restaurant exists."
    if edited_restaurant.user_id != login_session['user_id']:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to edit this restaurant. " \
               "Please create your own restaurant in order to edit.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name'] != edited_restaurant.name:
            edited_restaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % edited_restaurant.name)
        return redirect(url_for('restaurant.show_restaurants'))
    else:
        return render_template(
            'editRestaurant.html',
            restaurant=edited_restaurant
        )


# Delete a restaurant
@menu_item.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_restaurant(restaurant_id):
    try:
        restaurant_to_delete = session.query(
            Restaurant).filter_by(id=restaurant_id).one()
    except:
        return "No such restaurant to delete"
    if restaurant_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to delete this restaurant. " \
               "Please create your own restaurant in order to delete.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(restaurant_to_delete)
        menu_items_to_delete = session.query(MenuItem).filter_by(
            restaurant_id=restaurant_id
        ).all()
        for del_menu in menu_items_to_delete:
            session.delete(del_menu)
        flash('%s Successfully Deleted' % restaurant_to_delete.name)
        session.commit()
        return redirect(
            url_for(
                'restaurant.show_restaurants',
                restaurant_id=restaurant_id
            )
        )
    else:
        return render_template(
            'deleteRestaurant.html',
            restaurant=restaurant_to_delete
        )

# Show a restaurant menu


@menu_item.route('/restaurant/<int:restaurant_id>/')
@menu_item.route('/restaurant/<int:restaurant_id>/menu/')
def show_menu(restaurant_id):
    try:
        restaurant = session.query(Restaurant).filter_by(
            id=restaurant_id
        ).one()
    except:
        return "No such restaurant"
    creator = get_user_info(restaurant.user_id)
    if creator is None:
        return "The owner has shut down the restaurant"
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return render_template(
        'menu.html',
        items=items,
        restaurant=restaurant,
        creator=creator,
        login_session=login_session
    )


# Create a new menu item


@menu_item.route(
    '/restaurant/<int:restaurant_id>/menu/new/',
    methods=['GET', 'POST']
)
@login_required
def new_menu_item(restaurant_id):
    try:
        restaurant = session.query(Restaurant).filter_by(
            id=restaurant_id
        ).one()
    except:
        return "No such restaurant"
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {" \
               "alert(" \
               "'You are not authorized to add menu items " \
               "to this restaurant. " \
               "Please create your own restaurant in order to add items.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        new_item = MenuItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            course=request.form['course'],
            restaurant_id=restaurant_id,
            user_id=restaurant.user_id
        )
        session.add(new_item)
        session.commit()
        flash('New Menu %s Item Successfully Created' % new_item.name)
        return redirect(url_for('menu_item.show_menu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


# Edit a menu item


@menu_item.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
    methods=['GET', 'POST']
)
@login_required
def edit_menu_item(restaurant_id, menu_id):
    try:
        edited_item = session.query(MenuItem).filter_by(
            id=menu_id
        ).one()
    except:
        return "No such item"
    try:
        restaurant = session.query(Restaurant).filter_by(
            id=restaurant_id
        ).one()
    except:
        return "No such restaurant"
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to edit menu items" \
               " to this restaurant. " \
               "Please create your own restaurant in order " \
               "to edit items.');}" \
               "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        for (key, value) in request.form.items():
            setattr(edited_item, key, value)
        session.add(edited_item)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('menu_item.show_menu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'editmenuitem.html',
            restaurant_id=restaurant_id,
            menu_id=menu_id,
            item=edited_item
        )


# Delete a menu item
@menu_item.route(
    '/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
    methods=['GET', 'POST']
)
@login_required
def delete_menu_item(restaurant_id, menu_id):
    try:
        restaurant = session.query(Restaurant).filter_by(
            id=restaurant_id
        ).one()
    except:
        return "No such restaurant"
    try:
        item_to_delete = session.query(MenuItem).filter_by(
            id=menu_id
        ).one()
    except:
        return "No such item"
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to delete menu items " \
               "to this restaurant. " \
               "Please create your own restaurant in order to delete " \
               "items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('menu_item.show_menu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=item_to_delete)
