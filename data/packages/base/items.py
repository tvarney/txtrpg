
from rpg.data import item


copper_ore = item.MiscItem("misc.ore.copper", "Copper Ore", 2, 3.0)
tin_ore = item.MiscItem("misc.ore.tin", "Tin Ore", 2, 3.0)
iron_ore = item.MiscItem("misc.ore.iron", "Iron Ore", 4, 3.0)
coal_ore = item.MiscItem("misc.ore.coal", "Coal", 5, 3.0)
mithril_ore = item.MiscItem("misc.ore.mithril", "Mithril Ore", 10, 1.5)
adamantine_ore = item.MiscItem("misc.ore.adamantine", "Adamantine Ore", 20, 3.0)

bronze_bar = item.MiscItem("misc.bar.bronze", "Bronze Bar", 10, 5.0)
iron_bar = item.MiscItem("misc.bar.iron", "Iron Bar", 15, 5.0)
steel_bar = item.MiscItem("misc.bar.steel", "Steel Bar", 20, 5.0)
mithril_bar = item.MiscItem("misc.bar.mithril", "Mithril Bar", 50, 2.5)
adamantine_bar = item.MiscItem("misc.bar.adamantine", "Adamantine Bar", 100, 1.0)

weapon_bronze_short_sword = item.Weapon(
    "weapon.short_sword_bronze", item.WeaponType.ShortSword, "Bronze Short Sword", 10, 1, 0,
    [item.Attack("Slash", 10, 10), item.Attack("Stab", 5, 10)], 5
)
weapon_iron_short_sword = item.Weapon(
    "weapon.short_sword_iron", item.WeaponType.ShortSword, "Iron Short Sword", 10, 1, 0,
    [item.Attack("Slash", 10, 10), item.Attack("Stab", 5, 10)], 5
)
weapon_steel_short_sword = item.Weapon(
    "weapon.short_sword_steel", item.WeaponType.ShortSword, "Steel Short Sword", 10, 1, 0,
    [item.Attack("Slash", 10, 10), item.Attack("Stab", 5, 10)], 5
)
weapon_mithril_short_sword = item.Weapon(
    "weapon.short_sword_mithril", item.WeaponType.ShortSword, "Mithril Short Sword", 10, 1, 0,
    [item.Attack("Slash", 10, 10), item.Attack("Stab", 5, 10)], 5
)
weapon_adamantine_short_sword = item.Weapon(
    "weapon.short_sword_adamantine", item.WeaponType.ShortSword, "Adamantine Short Sword", 10, 1, 0,
    [item.Attack("Slash", 10, 10), item.Attack("Stab", 5, 10)], 5
)

weapon_bronze_long_sword = item.Weapon(
    "weapon.long_sword_bronze", item.WeaponType.LongSword, "Bronze Long Sword", 10, 1, 0,
    [item.Attack("Slash", 5, 10), item.Attack("Stab", 10, 10)], 5
)
weapon_bronze_dagger = item.Weapon(
    "weapon.dagger_bronze", item.WeaponType.Dagger, "Bronze Dagger", 10, 1, 0,
    [item.Attack("Slash", 5, 10), item.Attack("Stab", 5, 10)], 5
)
