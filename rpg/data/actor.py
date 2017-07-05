
"""Define various types of actors such as the Player, NPCs, and monsters.

This module defines the actors in the game. An actor is effectively a bundle of stats useful for combat. For NPC's this
is used for contested checks (e.g., a charisma check can be done against the NPC's wisdom), generalizing the mechanics
for various interactions which may be performed.

"""

from rpg.data import attributes

import typing
if typing.TYPE_CHECKING:
    from typing import Optional


class Actor(object):

    """The base class of all types of actor objects.
    
    """

    def __init__(self, name: str, race: None=None, stats: 'Optional[attributes.AttributeList]'=None) -> None:
        """Create a new instance of an Actor.

        :param name: The name of the actor
        :param race: The race of the actor (not used)
        :param stats: The attributes of the actor
        """
        self._name = name
        self._race = race
        self.stats = stats if stats is not None else attributes.AttributeList()

    def name(self, new_name: 'Optional[str]'=None) -> str:
        """Get or set the name of the actor.

        :param new_name: The new name of the actor if not None
        :return: The name of the actor
        """
        if new_name is not None:
            self._name = new_name
        return self._name

    def race(self) -> None:
        """Get the race of the actor.

        This is currently not used, and may end up not being used at all

        :return: The race of the actor
        """
        return self._race


class Player(Actor):

    """Definition of the Player character.

    The Player actor stores all information about the players character.

    """

    def __init__(self):
        """Create a new Player instance."""
        Actor.__init__(self, "", None, None)
        self.attribute_points = 0  # type: int
        self.inventory = None

    def calculate_secondaries(self):
        """Calculate the health, mana, and stamina of the player from the primary stats.

        The health of the character is calculated as (constitution * 3 + strength * 7)
        The stamina of the character is calculated as (constitution * 7 + agility * 3)
        The mana of the character is calculated as (intelligence * 7 + wisdom * 3)
        """
        current_health = self.stats.health.level()
        new_health = self.stats.constitution.level() * 3 + self.stats.strength.level() * 7
        self.stats.health.level_up(new_health - current_health)

        current_stamina = self.stats.stamina.level()
        new_stamina = self.stats.constitution.level() * 7 + self.stats.agility.level() * 3
        self.stats.stamina.level_up(new_stamina - current_stamina)

        current_mana = self.stats.mana.level()
        new_mana = self.stats.intelligence.level() * 7 + self.stats.wisdom.level() * 3
        self.stats.mana.level_up(new_mana - current_mana)


class NonPlayerCharacter(Actor):

    """An actor which is not the player.

    The NonPlayerCharacter class is used for pretty much every actor which is not the player. It defines one additional
    method over the Actor class, get_dialog()

    This method is intended to allow the player to interact with NPCs at a location.

    """

    def __init__(self, name: str, race: None=None, stats: 'Optional[attributes.AttributeList]'=None):
        """Create a new NonPlayerCharacter instance

        :param name: The name of the NPC
        :param race: The race of the NPC (not used)
        :param stats: The attributes of the NPC
        """
        Actor.__init__(self, name, race, stats)

    def get_dialog(self, game) -> 'Optional[str]':
        """Get a dialog resource_id used to interact with this NPC.

        If the return value of the dialog is None, then "This NPC does not want to talk to you" dialog is automatically
        substituted.

        :param game: The app.Game instance of the current game
        :return: A Dialog resource_id to display, or None if the NPC does not offer a dialog
        """
        raise NotImplementedError()


class Monster(NonPlayerCharacter):

    """A NonPlayerCharacter instance which can be fought.

    A Monster is a NPC which can be fought. Instances of these are generated from MonsterTemplates as defined in
    the rpg.data.resource module.

    """

    def __init__(self, name: str, race: None=None, stats: 'Optional[attributes.AttributeList]'=None):
        """Create a new Monster instance.

        This should not be done directly or even indirectly (do not subclass this)

        :param name: The name of the monster. This is generated dynamically from the MonsterTemplate class
        :param race: The race of the monster (not used)
        :param stats: The attributes of the monster
        """
        NonPlayerCharacter.__init__(self, name, race, stats)

    def get_dialog(self, game) -> 'Optional[str]':
        """Get a dialog for this monster.

        :param game: A handle to the current app.Game instance
        :return: A Dialog resource_id or None for no dialog
        """
        return None
