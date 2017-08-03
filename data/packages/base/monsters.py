
from rpg.data import actor, attributes
import typing
if typing.TYPE_CHECKING:
    from rpg import app


class Goblin(actor.NonPlayerCharacter):
    def __init__(self) -> None:
        stats = attributes.AttributeList(str=8, dex=6, con=8, agl=7, int=5, wis=5, cha=3, lck=5)
        actor.NonPlayerCharacter.__init__(self, 'mob.goblin', "Goblin", stats=stats)

    def get_intro_text(self, game: 'app.Game') -> str:
        return "\n".join(("You are fighting a goblin",
                          game.random.choice(["The goblin sneers at you",
                                              "The goblin growls and waves its short sword in your direction",
                                              "The goblin makes a rude gesture at you then draws its sword"])))
