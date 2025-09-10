# nextrpg

![Python ≥3.14](https://img.shields.io/badge/python-%E2%89%A53.14-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Build your next RPG (Role Playing Game).

## Example

Turn your Python code (Yes, what comes after `:` are annotations!)

```python
npc: "Nice to meet you! What's your name?"
player: f"Hello {npc.display_name}! I am {player.display_name}."
```

into an RPG game scene!

![img.png](example/screenshot/scene.png)

It comes with rich debug-info with a simple config tweak:

```python
Config(debug=DebugConfig())
```

![img.png](example/screenshot/debug.png)