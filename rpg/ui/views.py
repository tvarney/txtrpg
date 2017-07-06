
"""Classes representing Views.

A View is a tkinter.Frame which holds onto the entire window and can be swapped in and out by a ViewManager object.
This module defines both the base classes for Views and the basic view implementations. In addition, the @view_impl
class decorator is defined which allows packages to 'provide' additional views.

A View must be decorated with this decorator to be available for push/swap operations on a ViewManager instance.

"""

# TODO: Move view implementations to base package
# TODO: Add a way to allow packages to replace existing Views
# TODO: Add a package hook for post-load but pre-display; this lets the initial_view be defined by a package hook.

from abc import ABCMeta, abstractmethod
import tkinter
from rpg.ui import components, widgets

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data import resource
    from rpg.ui import options as _options
    from typing import Dict, List, Optional


class View(tkinter.Frame, metaclass=ABCMeta):

    """Base class of all View implementations.

    A View is defined by a series of callbacks which occur at various points in the views life cycle. In addition, a
    view tracks if it is the initial view or a game_view. Views which return true for View.is_game_view() should be
    subclasses of the GameView class instead (itself a subclass of View).

    View defines its metaclass as ABCMeta, though does not itself have any abstract methods. This is so the GameView
    subclass can mark its API as abstract.

    """

    def __init__(self, game: 'app.Game', name: str) -> None:
        """Initialize this View instance

        :param game: The app.Game instance
        :param name: The unique name of this View, used for push/swap operations
        """
        tkinter.Frame.__init__(self, game.root())
        self._game_obj = game
        self._game_view = False
        self._initial_view = False
        self._name = name

    def name(self) -> str:
        """Get the name of this View instance.

        :return: The lookup-name of this view
        """
        return self._name

    def is_initial_view(self) -> bool:
        """Check if this View instance claims to be the initial_view.

        :return: If this view is the initial view
        """
        return self._initial_view

    def is_game_view(self) -> bool:
        """Check if this View instance implements the GameView interface.

        :return: If this view implements the GameView interface
        """
        return self._game_view

    def start(self):
        """Handle anything that needs to happen each time the view is added to the stack.

        This method is called every time the view is pushed onto the ViewManager. This means that it is completely
        possible that the start() method is called multiple times in a row. For instance, in the case where push is
        called in the order:
            1. push("MainMenu")
            2. push("Options")
            3. push("MainMenu")

        The View defined by the name "MainMenu" would have its start() method called twice. If this would be
        problematic, the class should track the state of the View in some manner.

        The default implementation of this method does not do anything.

        """
        pass

    def resume(self):
        """Handle anything that needs to happen each time the view is revealed by a pop() operation.

        This method will only ever be called on paused views, due to the nature of when it is called. The default
        implementation of this method does not do anything.

        """
        pass

    def pause(self):
        """Handle anything that needs to happen each time the view is covered by another view.

        This method will only ever be called on views which are currently the active view (started). The default
        implementation of this method does not do anything.

        """
        pass

    def stop(self):
        """Handle anything that needs to happen each time the view is removed from the stack.

        This method may be called on a view which has an instance further down the stack still active. For instance,
        given the call order:
            1. push("MainMenu")
            2. push("Options")
            3. push("MainMenu")
            4. pop()

        The stop() method will be called on the MainMenu() instance despite there being an active 'instance' of it
        further down the stack. If this is an issue, then the class should track its state in some manner.

        The default implemenation of this method does not do anything.

        """
        pass


class GameView(View):

    """Base class of views which define themselves as a 'GameView'.

    A GameView is any view which can display a resource which has rpg.resource.Displayable as a super class.
    This class is here to define the basic API that a GameView should implement.

    """

    def __init__(self, game: 'app.Game', name: str) -> None:
        """Initialize the GameView instance.

        This method sets the self._game_view boolean to True, but otherwise is identical to the View.__init__(...)
        method.

        :param game: The app.Game instance
        :param name: The look-up name for this View
        """
        View.__init__(self, game, name)
        self._game_view = True

    @abstractmethod
    def text_area(self) -> tkinter.Text:
        """Get the tkinter.Text area used for displaying text.

        :return: The tkinter.Text area used to display the text of the current Displayable resource
        """
        raise NotImplementedError()

    def display(self, displayable: 'resource.Displayable', update_status_bar: bool=True) -> None:
        """Display the given displayable resource.

        This method delegates to the GameView.set_text(...) and GameView.set_options(...) methods.

        :param displayable: The displayable resource to display
        :param update_status_bar: If the status bar should be updated.
        """
        self.set_text(displayable.text(self._game_obj), False)
        self.set_options(displayable.options(self._game_obj), update_status_bar)

    @abstractmethod
    def set_text(self, text: str, update_status_bar: bool=True) -> None:
        """Set the text area of this GameView to the given text

        :param text: The text to set the text area to
        :param update_status_bar: If the status bar should be updated
        """
        raise NotImplementedError()

    @abstractmethod
    def set_options(self, options: '_options.OptionList', update_status_bar: bool=True) -> None:
        """Set the options of this GameView to the given options.OptionList

        :param options: The options.OptionList instance to set the option frame to
        :param update_status_bar: If the status bar should be updated
        """
        raise NotImplementedError


class ViewManager(object):

    """Manager for views as well as a stack structure tracking the current view.

    The ViewManager class defines the API for pushing and popping views with late-binding using name lookup.

    Views must be provided by the @view_impl decorator for an instance of them to be available.

    """

    AllViews = []       # type: List[type(View)]

    def __init__(self, game_object: 'app.Game'):
        """Initialize this ViewManager instance

        :param game_object: The app.Game instance which this ViewManager works in
        """
        self._game_obj = game_object  # type: app.Game
        self._stack = list()  # type: List[View]
        self._views = dict()  # type: Dict[str, View]
        self._initial_view = None  # type: Optional[str]

    def load_views(self) -> None:
        """Load all views which were marked by the @view_impl decorator."""
        if self._game_obj.root() is None:
            raise Exception("Can not load views without valid tkinter.Tk() root")

        for cls_view in ViewManager.AllViews:
            view_obj = cls_view(self._game_obj)  # type: View
            view_name = view_obj.name()  # type: str
            if view_name in self._views:
                self._game_obj.log.warning("Duplicate name for view '{}': overwriting {} with {}", view_name,
                                           repr(self._views[view_name]), repr(view_obj))
            self._views[view_name] = view_obj

            if view_obj.is_initial_view():
                if self._initial_view is not None:
                    self._game_obj.log.warning("Overwriting initial view: {} -> {}", self._initial_view, view_name)
                self._initial_view = view_name

    def clear_views(self) -> None:
        """Remove all views instances from this ViewManager."""
        self._views = dict()

    def initial_view(self) -> 'Optional[str]':
        """Get the name of the initial view, or None if no initial view was defined.

        :return: The name of the initial view, or None if no initial view was defined
        """
        return self._initial_view

    def swap(self, view_name: str) -> None:
        """Swap the active view to the one given by view_name.

        The current view is first stopped, then removed from the stack. The new view is then started and added to the
        stack. The view which would have been exposed by the equivalent pop(), push(view_name) operation is not resumed
        by this operation.

        :param view_name: The name of the view to swap onto the top of the stack
        """
        view = self._views.get(view_name, None)
        if view is not None:
            if len(self._stack) > 0:
                self._stack[-1].stop()
                self._stack[-1].pack_forget()
                self._stack.pop()
            self._stack.append(view)
            view.pack(side="top", fill="both", expand=True)
            view.start()
        else:
            self._game_obj.log.error("ViewManager::swap(): Can not swap to invalid view {}", view_name)

    def push(self, view_name: str) -> None:
        """Push the given view onto the top of the stack.

        This operation will first pause the current view, then start the given view.

        :param view_name: The name of the view to push
        """
        view = self._views.get(view_name, None)
        if view is not None:
            if len(self._stack) > 0:
                self._stack[-1].pause()
                self._stack[-1].pack_forget()
            self._stack.append(view)
            view.pack(side="top", fill="both", expand=True)
            view.start()
        else:
            self._game_obj.log.error("ViewManager::push(): Can not push invalid view {}", view_name)

    def pop(self, num: int=1, quit_if_empty: bool=True) -> None:
        """Pop the topmost num views from the stack.

        :param num: The number of views to pop from the stack
        :param quit_if_empty: If the ViewManager should force the window to close if 0 views are left on the stack
        """
        n_views = len(self._stack)
        if n_views > 0 and num > 0:
            self._stack[-1].stop()
            self._stack[-1].pack_forget()
            self._stack.pop()

            remaining = max(min(num, n_views) - 1, 0)
            for _ in range(remaining):
                self._stack[-1].stop()
                self._stack.pop()
            if len(self._stack) == 0:
                if quit_if_empty:
                    self._game_obj.quit(0)
            else:
                self._stack[-1].pack(side="top", fill="both", expand=True)
                self._stack[-1].resume()

    def finalize(self) -> None:
        """Stop all views on the stack and clear the stack."""
        for view in self._stack:
            view.stop()
        self._stack.clear()

    def clear(self, quit_if_empty: bool=False) -> None:
        """Remove all views from the stack.

        :param quit_if_empty: If the ViewManager should force the window to close
        """
        n_views = len(self._stack)
        if n_views > 0:
            self.pop(n_views, quit_if_empty)

    def current(self) -> 'Optional[View]':
        """Get the topmost view on the stack, or None if the stack is empty.

        :return: The topmost view on the stack if not empty
        """
        return self._stack[-1] if len(self._stack) > 0 else None


def view_impl(cls: type(View)):
    """Decorator method which registers a View implementation for the ViewManager class.

    :param cls: The subclass of View to register
    :return: The class after it has been registered
    """
    ViewManager.AllViews.append(cls)
    return cls


@view_impl
class MainMenuView(View):

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
        View.__init__(self, game, "MainMenu")
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
        self._game_obj.stack.push("LoadGame")

    def _action_quit(self):
        self._game_obj.quit(0)

    def _action_options(self):
        self._game_obj.stack.push("OptionsMenu")


@view_impl
class NewGameView(View):

    """Implementation of the NewGameView.

    This view defines controls for creating a new character and starting a new game. Callback hooks for pre- and post-
    new game initialization are ran by this view.

    When the player setup is complete, this view swaps itself out for the view named "GameView".
    """

    def __init__(self, game: 'app.Game'):
        """Initialize this instance of the NewGameView class.

        :param game: The app.Game instance
        """
        View.__init__(self, game, "NewGame")

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


@view_impl
class LoadGameView(View):
    def __init__(self, game: 'app.Game'):
        View.__init__(self, game, "LoadGame")


@view_impl
class OptionsMenuView(View):
    def __init__(self, game: 'app.Game'):
        View.__init__(self, game, "OptionsMenu")


@view_impl
class GameViewImpl(GameView):
    """Default implementation of the GameView abstract class.

    """

    def __init__(self, game: 'app.Game'):
        """

        :param game: The app.Game instance
        """
        GameView.__init__(self, game, "GameView")
        self.frmOptions_Internal = None  # type: Optional[tkinter.Frame]

        self.txtContent = widgets.StaticTextArea(self)
        self.frmStatus = components.StatusBar(self)
        self.frmOptions = tkinter.Frame(self)

        self.frmStatus.grid(column=0, row=0, sticky='ns')
        self.txtContent.grid(column=1, row=0, sticky='nswe')
        self.frmOptions.grid(column=0, row=1, columnspan=2, sticky='ew')

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def set_text(self, text: str, update_status_bar: bool=True) -> None:
        """Set the text displayed by this GameView.

        :param text: The text to display
        :param update_status_bar: If the StatusBar instance should be updated
        """
        self.txtContent.replace(text)
        if update_status_bar:
            self._update_status_bar()

    def set_options(self, option_list: '_options.OptionList', update_status_bar: bool=True) -> None:
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
        self.frmStatus.update_actor(self._game_obj.state.player)

    def text_area(self) -> tkinter.Text:
        """Get the tkinter.Text widget used to display text.

        :return: The tkinter.Text widget used to display text
        """
        return self.txtContent

    def start(self):
        pass

    def resume(self):
        self.start()


@view_impl
class FightView(View):
    def __init__(self, game: 'app.Game'):
        View.__init__(self, game, "FightView")


@view_impl
class InventoryView(View):
    def __init__(self, game: 'app.Game'):
        View.__init__(self, game, "InventoryView")
