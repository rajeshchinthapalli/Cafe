from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Configure CORS on the same app instance

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
#dbn
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, default=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "has_sockets": self.has_sockets,
            "has_toilet": self.has_toilet,
            "has_wifi": self.has_wifi,
            "can_take_calls": self.can_take_calls,
            "seats": self.seats,
            "coffee_price": self.coffee_price,
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    random_cafe = db.session.execute(db.select(Cafe).order_by(db.sql.func.random()).limit(1)).scalar()
    print(random_cafe)
    return jsonify(Cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "has_sockets": random_cafe.has_sockets,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "can_take_calls": random_cafe.can_take_calls,
        "seats": random_cafe.seats,
        "coffee_price": random_cafe.coffee_price,
    })


@app.route("/all")
def get_all_cafes():
    all_cafes = Cafe.query.all()
    cafes_list = [cafe.to_dict() for cafe in all_cafes]
    return jsonify({"cafes": cafes_list})


@app.route("/search")
def search_cafes():
    query_params = request.args
    base_query = Cafe.query

    if 'location' in query_params:
        base_query = base_query.filter(Cafe.location == query_params['location'])

    if 'has_sockets' in query_params:
        base_query = base_query.filter(Cafe.has_sockets == bool(query_params['has_sockets']))

    if 'has_toilet' in query_params:
        base_query = base_query.filter(Cafe.has_toilet == bool(query_params['has_toilet']))

    search_results = base_query.all()
    cafes_list = [cafe.to_dict() for cafe in search_results]

    return jsonify({"cafes": cafes_list})


@app.route('/add', methods=['POST'])
def add():
    name = request.args.get('name')
    location = request.args.get('location')
    map = request.args.get('map')
    img = request.args.get('img')
    seats = request.args.get('seats')
    coffee_price = request.args.get('coffee_price')
    new_cafe = Cafe(name=name, location=location, map_url=map, img_url=img, seats=seats, coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()
    return "NEW DATA ADDED SUCCESSFULLY"


@app.route("/update", methods=["PATCH"])
def update():
    if request.method == "PATCH":
        query_id = int(request.args.get("id"))
        parameter = request.args.get("parameter")
        parameter_value = request.args.get(parameter)
        update_data = {parameter: parameter_value}
        db.session.execute(db.update(Cafe).values(update_data).where(Cafe.id == query_id))
        db.session.commit()
        return jsonify({"message": "Cafe updated successfully."})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
