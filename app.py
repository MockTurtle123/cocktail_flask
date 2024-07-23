from flask import Flask, render_template, request, g, session, flash
from flask_sqlalchemy import SQLAlchemy

from functions import *

app = Flask(__name__)

app.config['SECRET_KEY'] = "secretkey123"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
db = SQLAlchemy(app)


class Cocktail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    glass = db.Column(db.String(20))
    garnish = db.Column(db.String(100))
    preparation = db.Column(db.String(500))
    ingredients = db.relationship('Ingredient', backref='cocktail')

    def __str__(self):
        return self.name


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    ingredient = db.Column(db.String(50))
    label = db.Column(db.String(50))
    special = db.Column(db.String(200))
    cocktail_id = db.Column(db.Integer, db.ForeignKey('cocktail.id'))

    def __str__(self):
        return self.ingredient


@app.route('/', methods=['GET', "POST"])
def index():

    if request.method == "POST":
        try:
            #  get selected ingredient from the user
            session['ingredient_selected'] = request.form['ingredient']
        except KeyError:
            try:
                #  get selected name from the user and return the recipe
                g.name_selected = request.form['name']
                session['recipe'] = return_recipe(g.name_selected, db)
                session.pop('ingredient_selected', default=None)
            except KeyError:
                #  post error message
                flash("Please select a name or an ingredient")

    # load ingredients from the database
    query = db.select(db.distinct(Ingredient.ingredient)).filter(Ingredient.ingredient.is_not(None)).order_by(Ingredient.ingredient)
    ingredient_list = db.session.scalars(query).all()

    name_list = []

    try:  # add recipes (containing selected ingredient) to the name list
        query = db.select(Cocktail).join(Ingredient).filter(Ingredient.ingredient == session['ingredient_selected'])
        name_list = db.session.scalars(query)
    except KeyError:  # add every recipe to the name list
        name_list = db.session.scalars(db.select(Cocktail).order_by(Cocktail.name))

    return render_template("index.html", ingredient_list=ingredient_list, name_list=name_list)


@app.route('/update')
def update():
    update_cocktails(db)
    return render_template("update.html")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)
