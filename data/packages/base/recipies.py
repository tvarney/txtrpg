
from rpg.data import resource


recipe_bronze_bar = resource.Recipe(
    "recipe.bronze_bar", "Bronze Bar", [("misc.ore.copper", 2), ("misc.ore.tin", 1)], [("misc.bar.bronze", 1)],
    [("smelting", 1)]
)
recipe_iron_bar = resource.Recipe(
    "recipe.iron_bar", "Iron Bar", [("misc.ore.iron", 1)], [("misc.bar.iron", 1)], [("smelting", 10)]
)
recipe_steel_bar = resource.Recipe(
    "recipe.steel_bar", "Steel Bar", [("misc.ore.iron", 1), ("misc.ore.coal", 1)], [("misc.bar.steel", 1)],
    [("smelting", 20)]
)
recipe_mithril_bar = resource.Recipe(
    "recipe.mithril_bar", "Mithril Bar", [("misc.ore.mithril", 1), ("misc.ore.coal", 2)], [("misc.bar.mithril", 1)],
    [("smelting", 30)]
)

