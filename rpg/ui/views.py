
import tkinter

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data import resource
    from typing import Dict, List, Optional


class View(tkinter.Frame):
    def __init__(self, game: 'app.Game', name: str):
        tkinter.Frame.__init__(game.root())
        self._game_obj = game
        self._game_view = False
        self._name = name

    def name(self) -> str:
        return self._name

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
    def __init__(self, game_object: 'app.Game'):
        self._game_obj = game_object
        self._stack = list()  # type: List[View]
        self._views = dict()  # type: Dict[str, View]

    def add(self, name: str, view: View):
        """
        Add a new View instance to the dictionary of available views
        :param name: The name of the view, used when pushing the view onto the stack
        :param view: The actual instance of the view
        """
        if name in self._views:
            self._game_obj.log.warning("Overwriting {} with {} for name {}", self._views[name], view, name)
        self._views[name] = view

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
