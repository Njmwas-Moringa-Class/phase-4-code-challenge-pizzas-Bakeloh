from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    restaurant_pizzas = relationship(
        'RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')

    def to_dict(self, include_pizzas=False):
        if include_pizzas:
            return {
                "id": self.id,
                "name": self.name,
                "address": self.address,
                "restaurant_pizzas": [rp.to_dict() for rp in self.restaurant_pizzas]
            }
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
        }

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    restaurant_pizzas = relationship(
        'RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients,
        }

    def __repr__(self):
        return f'<Pizza {self.name}, {self.ingredients}>'


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'))

    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, price):
        if not (isinstance(price, int) and 1 <= price <= 999):
            raise ValueError("Price must be between 1 and 999.")
        return price

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "pizza": self.pizza.to_dict(),
            "pizza_id": self.pizza_id,
            "restaurant": self.restaurant.to_dict(),
            "restaurant_id": self.restaurant_id
        }

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'

