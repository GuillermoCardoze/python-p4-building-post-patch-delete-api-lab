#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()

    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    if request.method == 'PATCH':
        # Get the 'name' from the form data, if provided
        new_name = request.form.get('name')

        # Check if the name is provided in the form
        if new_name:
            bakery.name = new_name  # Update the bakery name
            db.session.commit()     # Commit the changes to the database

        # Return the updated bakery data
        return make_response(bakery.to_dict(), 200)

    # If it's a GET request, return the bakery's data
    bakery_serialized = bakery.to_dict()
    return make_response(bakery_serialized, 200)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    if request.method == 'POST':
        # Get the form data from the request
        name = request.form.get('name')
        price = request.form.get('price')
        bakery_id = request.form.get('bakery_id')

        # Validate form data
        if not name or not price or not bakery_id:
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        # Create a new baked good instance
        new_baked_good = BakedGood(
            name=name,
            price=price,
            bakery_id=bakery_id
        )

        # Add to the database
        db.session.add(new_baked_good)
        db.session.commit()

        # Return the new baked good as JSON
        return make_response(new_baked_good.to_dict(), 201)

    # If it's a GET request, return all baked goods
    baked_goods = [bg.to_dict() for bg in BakedGood.query.all()]
    return make_response(baked_goods, 200)


@app.route('/baked_goods/<int:id>', methods=['GET', 'DELETE'])
def baked_good_by_id(id):
    baked_good = BakedGood.query.filter_by(id=id).first()

    if not baked_good:
        return make_response(jsonify({"error": "Baked good not found"}), 404)

    if request.method == 'DELETE':
        # Delete the baked good from the database
        db.session.delete(baked_good)
        db.session.commit()

        # Return a JSON confirmation message
        return make_response(jsonify({"message": "Baked good successfully deleted"}), 200)

    # If it's a GET request, return the baked good's data
    baked_good_serialized = baked_good.to_dict()
    return make_response(baked_good_serialized, 200)




if __name__ == '__main__':
    app.run(port=5555, debug=True)