from flask import Flask, request, jsonify, abort
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurants.db'
db.init_app(app)
migrate = Migrate(app, db)

def error_response(message, status_code):
    response = jsonify({"error": message})
    response.status_code = status_code
    return response

def validate_restaurant_pizza_data(data):
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')
    
    if not all([price, pizza_id, restaurant_id]):
        return False, "Missing values in the request."
    if not (price.isdigit() and 1 <= int(price) <= 999):
        return False, "'Price' must be a number between 1 and 999."
    
    return True, ""

@app.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict(include_pizzas=True)), 200
    else:
        return error_response("Restaurant does not exist.", 404)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return error_response("The restaurant does not exist", 404)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200

@app.route('/restaurant_pizzas', methods=['POST'])
def add_new_pizza_to_restaurant():
    data = request.json
    is_valid, error_message = validate_restaurant_pizza_data(data)
    if not is_valid:
        return error_response(error_message, 400)
    
    pizza = Pizza.query.get(data['pizza_id'])
    restaurant = Restaurant.query.get(data['restaurant_id'])
    
    if not (pizza and restaurant):
        return error_response('Pizza or Restaurant does not exist', 400)
   
    try:
        new_pizza_in_restaurant = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_pizza_in_restaurant)
        db.session.commit()
        return jsonify(new_pizza_in_restaurant.to_dict()), 201
    except ValueError as e:
        return error_response(str(e), 500)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
