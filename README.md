# nextrpg

![Python ≥3.14](https://img.shields.io/badge/python-%E2%89%A53.14-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Build your next RPG (Role Playing Game).

```
pip install nextrpg
```

## Example

Bring up Tiled map editor...

![Tiled](example/screenshot/tiled.png)

And turn your Python code (Yes, what comes after `:` are "type
hints"!)

```python
npc: "Nice to meet you! What's your name?"
player[AvatarPosition.RIGHT]: f"Hello {npc.name}! I am {player.name}."
```

into an RPG game scene! See the full
example: [example/scene/interior_scene.py](example/scene/interior_scene.py)

![interior](example/screenshot/interior.png)

Plus, the debug information is just one-click away (by default, F3).

![Debug](example/screenshot/debug.png)

## Screenshots

![title](example/screenshot/title.png)

![exterior](example/screenshot/exterior.png)

![menu](example/screenshot/menu.png)