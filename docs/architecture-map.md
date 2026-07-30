# Architecture Map

## Runtime flow

`Tkinter button event -> TkGameView -> GameController -> MovementGateway -> BasicMovement -> GameState`

The returned status follows the same path back to the view. Expected failures are converted into visible messages by the controller.

## Dependency rules

1. `domain` must not import Tkinter.
2. `ui` may call the integration layer, not domain internals.
3. The integration layer depends on contracts rather than a particular team implementation.
4. Fakes and stubs may replace incomplete dependencies during development and testing.
5. Application dependencies are assembled in `zimp.main.build_app()`.

## Tutor example versus assessed work

The supplied movement flow is a small worked seam. It demonstrates the structure but does not complete the game or define every acceptable student feature.

## Clearly marked replacement points

- Add or replace component implementations behind explicit contracts.
- Add a controller method for each framework-to-domain interaction.
- Wire dependencies in `build_app()`.
- Add normal and failure-path pytest tests for each owned boundary.
- Extend the Tkinter shell only where an assessed feature requires it.
