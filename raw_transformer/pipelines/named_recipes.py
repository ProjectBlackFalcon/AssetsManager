import json
import os


def generate():
    """
    Outputs the list of all recipes as a list of:
    {
        "resultLevel": 7,
        "Ingredients": [[16512, 3], [303, 3]],
        "resultName": "Epée de Boisaille",
        "jobId": 11,
        "resultTypeId": 6,
        "resultId": 44
    }

    :return: None
    """
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/i18n_fr.json')), 'r', encoding="utf8") as f:
        names = json.load(f)['texts']

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/Recipes.json')), 'r') as f:
        recipes = json.load(f)

    new_recipes = []
    for recipe in recipes:
        if str(recipe['resultNameId']) in names.keys():
            recipe['resultName'] = names[str(recipe['resultNameId'])]
            recipe['Ingredients'] = list(zip(recipe['ingredientIds'], recipe['quantities']))
            del recipe['resultNameId']
            del recipe['ingredientIds']
            del recipe['quantities']
            del recipe['skillId']
            new_recipes.append(recipe)

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/named_recipes.json')), 'w', encoding='utf8') as f:
        json.dump(new_recipes, f, ensure_ascii=False)
