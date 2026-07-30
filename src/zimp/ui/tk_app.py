import tkinter as tk
from tkinter import ttk

from zimp.integration.game_controller import GameController


class TkGameView:
    """Minimal accessible shell. Visual sophistication is not assessed."""

    def __init__(self, root: tk.Tk, controller: GameController) -> None:
        self._root = root
        self._controller = controller
        root.title("Zombie in My Pocket")
        root.minsize(360, 280)

        frame = ttk.Frame(root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Movement controls").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        controls = (
            ("Move north", "north"),
            ("Move south", "south"),
            ("Move east", "east"),
            ("Move west", "west"),
        )
        self._movement_buttons: list[ttk.Button] = []
        for row, (label, direction) in enumerate(controls, start=1):
            button = ttk.Button(
                frame,
                text=label,
                command=lambda selected=direction: self._move(selected),
            )
            button.grid(row=row, column=0, sticky="ew", pady=2)
            self._movement_buttons.append(button)

        self.status = tk.StringVar(value="Choose a direction.")
        ttk.Label(frame, text="Status").grid(row=5, column=0, sticky="w", pady=(10, 0))
        ttk.Label(frame, textvariable=self.status, wraplength=320).grid(
            row=6, column=0, sticky="w", pady=(2, 8)
        )
        ttk.Button(frame, text="Exit", command=root.destroy).grid(
            row=7, column=0, sticky="w"
        )
        self._movement_buttons[0].focus_set()

    def _move(self, direction: str) -> None:
        self.status.set(self._controller.handle_move(direction))
