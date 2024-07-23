import pandas as pd
from sqlalchemy.exc import NoResultFound

from app import Cocktail, Ingredient


def update_cocktails(db):
    """Convert json file to database"""
    recipe_book_df = pd.read_json('static/recipes.json')
    for index, row in recipe_book_df.iterrows():
        cocktail = Cocktail(
            name=row['name'],
            glass=row['glass'],
            garnish=row['garnish'],
            preparation=row['preparation'],
        )
        db.session.add(cocktail)

        for item in row['ingredients']:
            ingredient = Ingredient()
            try:
                ingredient.amount = item['amount']
            except KeyError:
                pass

            try:
                ingredient.ingredient = item['ingredient']
            except KeyError:
                pass

            try:
                ingredient.label = item['label']
            except KeyError:
                pass

            try:
                ingredient.special = item['special']
            except KeyError:
                pass

            ingredient.cocktail = cocktail
            db.session.add(ingredient)
        db.session.commit()

    db.session.commit()


def convert(cl: int | float) -> int:
    """convert cl to ml"""
    ml = cl * 10
    return int(ml)


def format_glass(name: str, glass: str) -> str:
    """prepare glass string for output"""
    article: str = "an" if glass.startswith("o") else "a"
    glass_str: str = f"{name} is typically served in {article} {glass} glass.\n\n"

    return glass_str


def format_ingredients(ingredients: Cocktail.ingredients) -> list[str]:
    """prepare ingredients for output"""
    ingredients_output: list = ["<b>Ingredients:</b>"]
    for item in ingredients:
        if item.label:
            ingredients_output.append(f"{convert(item.amount)}ml of {item.ingredient} ({item.label})")
        elif item.ingredient:
            ingredients_output.append(f"{convert(item.amount)}ml of {item.ingredient}")
        elif item.special:
            ingredients_output.append(f"{item.special}")
        else:
            continue

    return ingredients_output


def format_garnish(garnish: str) -> str:
    """prepare garnish string for output"""
    garnish_str: str = f"Usually garnished with {garnish.lower()}\n"

    return garnish_str


def return_recipe(name: str, db) -> list[str]:
    """output the full recipe"""
    try:
        query = db.select(Cocktail).where(Cocktail.name == name)
        selection = db.session.scalars(query).first()
    except NoResultFound:
        return ["Recipe not found"]

    glass: str = selection.glass
    garnish: str = selection.garnish
    ingredients: list = selection.ingredients
    preparation: str = selection.preparation

    recipe: list = []

    recipe.append(format_glass(name, glass))
    recipe.extend(format_ingredients(ingredients))

    if garnish:
        recipe.append(format_garnish(garnish))

    recipe.extend(["<b>Preparation:</b>", preparation])

    return recipe
