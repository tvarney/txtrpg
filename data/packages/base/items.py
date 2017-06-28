
from rpg.data import item


weapon_bronze_short_sword = item.Weapon(
    "weapon.short_sword_bronze", item.WeaponType.ShortSword, "Bronze Short Sword", 10, 1,
    [item.Attack("Slash", 10, 10), item.Attack("Stab", 5, 10)], 5
)
weapon_bronze_long_sword = item.Weapon(
    "weapon.long_sword_bronze", item.WeaponType.LongSword, "Bronze Long Sword", 10, 1,
    [item.Attack("Slash", 5, 10), item.Attack("Stab", 10, 10)], 5
)
weapon_bronze_dagger = item.Weapon(
    "weapon.dagger_bronze", item.WeaponType.Dagger, "Bronze Dagger", 10, 1,
    [item.Attack("Slash", 5, 10), item.Attack("Stab", 5, 10)], 5
)
