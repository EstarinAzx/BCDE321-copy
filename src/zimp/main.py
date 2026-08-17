import tkinter as tk

from zimp.support.game.items_fake import Items
from zimp.support.game.movement_fake import Movement
from zimp.support.game.actions_fake import ActionHandler

from zimp.integration.game_controller import GameController
from zimp.ui.tk_app import TkGameView


def build_app() -> tk.Tk:
    """Composition root: replace dependencies here, not inside widgets."""
    root = tk.Tk()
    movement = Movement()
    actions = ActionHandler()
    items = Items()
    TkGameView(root, GameController(movement, items, actions))
    return root


def main() -> None:
    build_app().mainloop()


if __name__ == "__main__":
    main()
