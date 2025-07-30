# nextrpg

![Python ≥3.14](https://img.shields.io/badge/python-%E2%89%A53.14-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Build your next RPG (Role Playing Game).

## Example

Turn your Python code

```python
npc: "Nice to meet you! What's your name?"
player: f"Hello {npc.display_name}! I am {player.display_name}."
```

into an RPG game scene!
![interior](example/screenshot/interior.png)

For more advanced text-styling:

```python
scene["Interior Scene"]: Text("Greetings!", cfg.sized(40)) + Text(
"""This is...

a sample """, cfg) + Text("nextrpg event", cfg.colored(Rgb(128, 0, 255)))
```

![text](example/screenshot/text.png)

Take a look
at [interior_scene.py](https://github.com/yx-z/nextrpg/blob/main/example/interior_scene.py#L24)
for details :)