# -*- encoding: utf-8 -*-
from flask import Blueprint, render_template, session as login_session
from sqlalchemy import asc, desc
from models.restaurant import Restaurant
from models.menu_item import MenuItem
from database import session

restaurant = Blueprint('restaurant', __name__)


@restaurant.route('/')
@restaurant.route('/restaurant/')
def show_restaurants():
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template(
        'restaurants.html',
        restaurants=restaurants,
        login_session=login_session
    )
