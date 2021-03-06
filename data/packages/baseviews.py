
from rpg import event
from rpg.ui import components, options, views, widgets
import tkinter

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data import actor
    from typing import Optional

Author = "Troy Varney"
Version = "0.1"


@views.view_impl
class MainMenuView(views.View):

    """The Main Menu.

    This View is the default initial view. It displays the title of the game and buttons for the options.

    Options provided by this View are:
        1. "New Game" -> Attempts to push the view named "NewGame"
        2. "Load Game" -> Attempts to push the view named "LoadGame"
        3. "Options" -> Attempts to push the view named "Options"
        4. "Packages" -> Attempts to push the view named "PackageManager"
        5. "Quit" -> Clears the stack and quits the application

    """

    def __init__(self, game: 'app.Game') -> None:
        """Initialize the MainMenuView instance.

        :param game: The app.Game instance
        """
        views.View.__init__(self, game, "MainMenu")
        self._initial_view = True
        self.lblTitle = tkinter.Label(self, text="Text RPG", font=("Helvetica", 28, 'bold'))
        self.frmSpace1 = tkinter.Frame(self)
        self.frmButtons = tkinter.Frame(self)

        self.btnNewGame = widgets.Button(self.frmButtons, "New Game", self._action_new_game)
        self.btnLoadGame = widgets.Button(self.frmButtons, "Load Game", self._action_load_game)
        self.btnOptions = widgets.Button(self.frmButtons, "Options", self._action_options)
        self.btnQuit = widgets.Button(self.frmButtons, "Quit", self._action_quit)

        self.lblTitle.pack()
        self.frmSpace1.pack(pady=10)
        self.btnNewGame.pack(fill='x', expand=True)
        self.btnLoadGame.pack(fill='x', expand=True)
        self.btnOptions.pack(fill='x', expand=True)
        self.btnQuit.pack(fill='x', expand=True)
        self.frmButtons.pack()

    def _action_new_game(self):
        self._game_obj.build_resources()
        self._game_obj.stack.push("NewGame")

    def _action_load_game(self):
        self._game_obj.build_resources()
        self._game_obj.stack.push("GameView")
        self._game_obj.state.player.name("Test Player")
        self._game_obj.state.player.inventory.add('misc.ore.coal', 100)
        self._game_obj.state.player.inventory.add('misc.ore.tin', 100)
        self._game_obj.state.player.inventory.add('misc.ore.copper', 100)
        self._game_obj.state.player.inventory.add('weapon.short_sword_bronze')
        self._game_obj.state.player.inventory.add('weapon.short_sword_bronze')
        self._game_obj.state.start()

    def _action_quit(self):
        self._game_obj.quit(0)

    def _action_options(self):
        self._game_obj.stack.push("OptionsMenu")


@views.view_impl
class NewGameView(views.View):

    """Implementation of the NewGameView.

    This view defines controls for creating a new character and starting a new game. Callback hooks for pre- and post-
    new game initialization are ran by this view.

    When the player setup is complete, this view swaps itself out for the view named "GameView".
    """

    def __init__(self, game: 'app.Game'):
        """Initialize this instance of the NewGameView class.

        :param game: The app.Game instance
        """
        views.View.__init__(self, game, "NewGame")

        self.frmContent = tkinter.Frame(self)
        self.entryName = widgets.LabeledEntry(self.frmContent, "Name")
        self.frmStats = components.AttributeEditorFrame(self.frmContent, 20)
        self.entryName.pack(side="top", anchor=tkinter.W)
        self.frmStats.pack(side='top', anchor=tkinter.W)
        self.frmContent.pack(side='top', fill='both', expand=True, anchor="n")

        self.frmNavigation = tkinter.Frame(self)
        self.btnBack = widgets.Button(self.frmNavigation, "Back", self._action_back)
        self.btnBack.pack(side=tkinter.LEFT)
        self.btnNext = widgets.Button(self.frmNavigation, "Next", self._action_next)
        self.btnNext.pack(side=tkinter.RIGHT)
        self.frmNavigation.pack(side="bottom", fill="x", expand=True, anchor='s')

    def start(self) -> None:
        """Start callback of the View API.

        This method should (but does not currently) iterate over active packages and call their pre new game callbacks.
        """
        self.entryName.entry.delete(0, tkinter.END)

    def _action_back(self) -> None:
        self._game_obj.stack.pop()

    def _action_next(self) -> None:
        name = self.entryName.entry.get()
        if name == "":
            return
        self._game_obj.stack.push("GameView")
        self._game_obj.state.player.name(self.entryName.entry.get())
        self.frmStats.write(self._game_obj.state.player)
        self._game_obj.state.start()


@views.view_impl
class LoadGameView(views.View):
    def __init__(self, game: 'app.Game'):
        views.View.__init__(self, game, "LoadGame")


@views.view_impl
class OptionsMenuView(views.View):
    def __init__(self, game: 'app.Game'):
        views.View.__init__(self, game, "OptionsMenu")


@views.view_impl
class GameViewImpl(views.GameView):
    """Default implementation of the GameView abstract class.

    """

    def __init__(self, game: 'app.Game'):
        """

        :param game: The app.Game instance
        """
        views.GameView.__init__(self, game, "GameView")
        self.frmOptions_Internal = None  # type: Optional[tkinter.Frame]

        self._var_title = tkinter.StringVar(self)

        self._inventory = False

        self.txtContent = widgets.StaticTextArea(self)
        self.lblTitle = tkinter.Label(self, textvariable=self._var_title, font=('arial', 18, 'bold'))
        self.frmStatus = components.StatusBar.default(self, game)
        controls = self.frmStatus.add_section("controls", None, side='bottom')
        controls.add_item("inventory", widgets.Button(controls, "Inventory", self._action_inventory))

        self.frmInventory = components.InventoryFrame(self)

        self.frmOptions = tkinter.Frame(self)
        self.frmMonster = components.CombatStatusBar(self)

        self.frmStatus.grid(column=0, row=0, rowspan=2, sticky='ns')
        self.txtContent.grid(column=1, row=1, sticky='nsew')
        self.frmOptions.grid(column=0, row=2, columnspan=2, sticky='ew')
        self.lblTitle.grid(column=1, row=0, sticky="ew")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._fight_options = options.OptionList((options.Option("Run Away", event.FightEndEvent()), 0, 0))

    def _action_inventory(self):
        if self._inventory:
            self.frmInventory.clear()
            self.frmInventory.grid_forget()
            self.txtContent.grid(column=1, row=1, sticky='nsew')
        else:
            self.frmInventory.build(self._game_obj.state.player.inventory)
            self.txtContent.grid_forget()
            self.frmInventory.grid(column=1, row=1, sticky='nsew')
        self._inventory = not self._inventory

    def set_title(self, text: str, update_status_bar: bool=False) -> None:
        """Set the displayed title to the given text.

        :param text: The text to update the title to
        :param update_status_bar: If the status bar should be updated
        """
        self._var_title.set(text)
        if update_status_bar:
            self._update_status_bar()

    def set_text(self, text: str, update_status_bar: bool=True) -> None:
        """Set the text displayed by this GameView.

        :param text: The text to display
        :param update_status_bar: If the StatusBar instance should be updated
        """
        self.txtContent.replace(text)
        if update_status_bar:
            self._update_status_bar()

    def add_text(self, text: str, update_status_bar: bool=True) -> None:
        self.txtContent.insert(tkinter.END, text)

    def set_options(self, option_list: 'options.OptionList', update_status_bar: bool=True) -> None:
        """Set the options displayed by this GameView.

        :param option_list: The options.OptionList instance to set the options to
        :param update_status_bar: If the StatusBar instance should be updated
        """
        if self.frmOptions_Internal is not None:
            self.frmOptions_Internal.grid_remove()
        self.frmOptions_Internal = option_list.generate(self._game_obj, self.frmOptions)
        self.frmOptions_Internal.grid(sticky="NSEW")
        if update_status_bar:
            self._update_status_bar()

    def _update_status_bar(self) -> None:
        """Private function used to update the StatusBar instance."""
        self.frmStatus.update_widgets(self._game_obj.state.player, self._game_obj)

    def text_area(self) -> tkinter.Text:
        """Get the tkinter.Text widget used to display text.

        :return: The tkinter.Text widget used to display text
        """
        return self.txtContent

    def start(self):
        pass

    def resume(self):
        self.start()

    def fight_start(self, monster: 'actor.NonPlayerCharacter'):
        self.txtContent.clear()
        self.frmMonster.grid(column=1, row=0, sticky="ew")
        self.frmMonster.update_actor(monster)
        self.set_options(self._fight_options)
        self.update_idletasks()
        self.txtContent.replace(monster.get_intro_text(self._game_obj))

    def fight_update(self, actor_: 'actor.NonPlayerCharacter'):
        self.frmMonster.update_actor(actor_)

    def fight_end(self):
        self.frmMonster.grid_forget()
        self._game_obj.state.resume_display()
