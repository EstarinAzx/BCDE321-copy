import tkinter as tk

from zimp.domain.basic_movement import BasicMovement
from zimp.domain.game_state import GameState
from zimp.integration.game_controller import GameController
from zimp.ui.tk_app import TkGameView


def build_app() -> tk.Tk:
    """Composition root: replace dependencies here, not inside widgets."""
    root = tk.Tk()
    movement = BasicMovement(GameState())
    TkGameView(root, GameController(movement))
    return root


def main() -> None:
    build_app().mainloop()


if __name__ == "__main__":
    main()
