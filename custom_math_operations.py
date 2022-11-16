import re
import pandas as pd

recipe = """
For 3 people:
100g plain flour
2 large eggs
300ml milk
"""

def multiply_constructor(multiplier):
    def multiply(x):
        return str(int(x.group()) * multiplier)
    return multiply

desired_quantity = 9

m = re.search("(?<=For )(\d+)", recipe)
recipe_quantity = int(m.group())

recipe = re.sub("(?<=For )(\d+)", f"{desired_quantity}" ,recipe)

multiply = multiply_constructor(int(desired_quantity/recipe_quantity))
recipe = re.sub("(?<=\n)(\d+)(?=.+\n)", multiply, recipe)

df = pd.DataFrame({
    "desired_number_of_people":[9, 9, 9],
    "number_of_people":[3, 2, 4],
    "text": [
        "\n100g plain flour\n2 large eggs\n300ml milk\n",
        "\n500g strong white flour\n2 tsp salt\n300ml water\n",
        "\n2 tbsp olive oil\n2 onions\n1kg pumpkin\n150ml double cream\n"
    ]
})

df["text"] = (
    df.apply(lambda x: re.sub(
        "(?<=\n)(\d+)(?=.+\n)",
        multiply_constructor(x["desired_number_of_people"]/x["number_of_people"]),
        x["text"]
    ), axis=1)
)

for t in df["text"].values:
    print(t)

