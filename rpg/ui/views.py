
import tkinter
from rpg.ui import widgets

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data import resource
    from rpg.ui import options
    from typing import Dict, List, Optional


class View(tkinter.Frame):
    def __init__(self, game: 'app.Game', name: str):
        tkinter.Frame.__init__(self, game.root())
        self._game_obj = game
        self._game_view = False
        self._initial_view = False
        self._name = name

    def name(self) -> str:
        """
        :return: The lookup-name of this view
        """
        return self._name

    def is_initial_view(self) -> bool:
        """
        :return: If this view is the initial view
        """
        return self._initial_view

    def is_game_view(self) -> bool:
        """
        :return: If this view implements the GameView interface
        """
        return self._game_view

    def start(self):
        """
        Handle anything that needs to happen each time the view is added to the stack
        """
        pass

    def resume(self):
        """
        Handle anything that needs to happen each time the view is revealed by a pop() operation
        """
        pass

    def pause(self):
        """
        Handle anything that needs to happen each time the view is covered by another view
        """
        pass

    def stop(self):
        """
        Handle anything that needs to happen each time the view is removed from the stack
        """
        pass


class GameView(View):
    def __init__(self, game: 'app.Game', name: str):
        View.__init__(self, game, name)
        self._game_view = True
        self._actor = None  # type: Optional[rpg.data.Actor]

    def text_area(self) -> tkinter.Text:
        raise NotImplementedError()

    def display(self, displayable: 'resource.Displayable'):
        self.set_text(displayable.text(self._game_obj))
        self.set_options(displayable.options(self._game_obj))

    def set_text(self, text: str):
        raise NotImplementedError()

    def set_options(self, options: 'options.OptionList'):
        raise NotImplementedError


class ViewManager(object):
    AllViews = []       # type: List[type(View)]

    def __init__(self, game_object: 'app.Game'):
        self._game_obj = game_object
        self._stack = list()  # type: List[View]
        self._views = dict()  # type: Dict[str, View]
        self._initial_view = None  # type: Optional[str]

    def load_views(self):
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

    def clear_views(self):
        self._views = dict()

    def initial_view(self) -> 'Optional[str]':
        return self._initial_view

    def swap(self, view_name: str):
        """
        Swap the active view to the one given by view_name

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

    def push(self, view_name: str):
        """
        Push the given view onto the top of the stack

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

    def pop(self, num: int=1, quit_if_empty: bool=True):
        """
        Pop the topmost num views from the stack
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

    def finalize(self):
        for view in self._stack:
            view.stop()
        self._stack.clear()

    def clear(self, quit_if_empty: bool=False):
        """
        Remove all views from the stack
        :param quit_if_empty: If the ViewManager should force the window to close
        """
        n_views = len(self._stack)
        if n_views > 0:
            self.pop(n_views, quit_if_empty)

    def current(self) -> 'Optional[View]':
        return self._stack[-1] if len(self._stack) > 0 else None


def view_impl(cls: type(View)):
    ViewManager.AllViews.append(cls)
    return cls


@view_impl
class MainMenuView(View):
    def __init__(self, game: 'app.Game'):
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
        pass

    def _action_load_game(self):
        pass

    def _action_quit(self):
        self._game_obj.quit(0)

    def _action_options(self):
        pass


@view_impl
class NewGameView(View):
    def __init__(self, game: 'app.Game'):
        View.__init__(self, game, "NewGame")


@view_impl
class LoadGameView(View):
    def __init__(self, game: 'app.Game'):
        View.__init__(self, game, "LoadGame")


@view_impl
class OptionsMenuView(View):
    def __init__(self, game: 'app.Game'):
        View.__init__(self, game, "OptionsMenu")
