"""
Pygame Title Scene / New Game screen (single-file starter)
- Mouse + keyboard/gamepad navigation
- Scales to any window size
- Fade-in/out transitions
- Centered window & custom icon support
- "Continue" auto-enables if a save file exists
- Clean scene/state structure you can extend
- Built-in smoke tests (set RUN_TESTS=1 to run)

Runs without external assets. Python 3.11+ recommended.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# --- Center the window before initializing pygame ---
os.environ.setdefault("SDL_VIDEO_CENTERED", "1")

import pygame

# -------------- Config --------------
APP_NAME = "My Game"
WIN_W, WIN_H = 960, 540
FPS = 60
SAVE_PATH = Path.home() / ".my_game" / "save.json"

# -------------- Utility --------------


def ensure_save_dir():
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_has_save() -> bool:
    try:
        return SAVE_PATH.is_file() and SAVE_PATH.stat().st_size > 0
    except Exception:
        return False


@dataclass
class Colors:
    # Use default_factory for mutable defaults like pygame.Color
    bg: pygame.Color = field(default_factory=lambda: pygame.Color(18, 18, 20))
    panel: pygame.Color = field(
        default_factory=lambda: pygame.Color(30, 30, 36)
    )
    accent: pygame.Color = field(
        default_factory=lambda: pygame.Color(255, 215, 90)
    )
    text: pygame.Color = field(
        default_factory=lambda: pygame.Color(235, 235, 245)
    )
    text_muted: pygame.Color = field(
        default_factory=lambda: pygame.Color(160, 165, 175)
    )
    focus: pygame.Color = field(
        default_factory=lambda: pygame.Color(110, 190, 255)
    )


COLORS = Colors()


# -------------- Core scene system --------------
class Scene:
    def __init__(self, game: "Game"):
        self.game = game
        self.next: Optional[Scene] = None
        self.alpha = 255  # for fade
        self.fading_in = True
        self.fading_out = False

    def start(self):
        pass

    def handle_event(self, e: pygame.event.Event):
        pass

    def update(self, dt: float):
        # Fade logic
        fade_speed = 600  # alpha per second
        if self.fading_in:
            self.alpha -= fade_speed * dt
            if self.alpha <= 0:
                self.alpha = 0
                self.fading_in = False
        if self.fading_out:
            self.alpha += fade_speed * dt
            if self.alpha >= 255:
                self.alpha = 255
                # when fully faded out, switch scene
                if self.next:
                    self.game.set_scene(self.next)

    def drawing(self, screen: pygame.Surface):
        pass

    def request_switch(self, next_scene: "Scene"):
        self.next = next_scene
        self.fading_out = True


# -------------- UI Components --------------
class Button:
    def __init__(
        self, label: str, action: Callable[[], None], *, enabled: bool = True
    ):
        self.label = label
        self.action = action
        self.enabled = enabled
        self.rect = pygame.Rect(0, 0, 280, 56)
        self.focused = False

    def set_pos_center(self, cx: int, cy: int):
        self.rect.center = (cx, cy)

    def handle_event(self, e: pygame.event.Event):
        if not self.enabled:
            return
        if e.type == pygame.MOUSEMOTION:
            self.focused = self.rect.collidepoint(e.pos)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.focused and self.enabled:
                self.action()

    def drawing(self, screen: pygame.Surface, font: pygame.font.Font):
        bg = COLORS.panel
        border = COLORS.focus if self.focused and self.enabled else COLORS.panel
        label_color = COLORS.text if self.enabled else COLORS.text_muted

        pygame.draw.rect(screen, bg, self.rect, border_radius=12)
        pygame.draw.rect(screen, border, self.rect, width=2, border_radius=12)

        text_surf = font.render(self.label, True, label_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


# -------------- Scenes --------------
class TitleScene(Scene):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("arialblack", 64)
        self.btn_font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.buttons: list[Button] = []
        self.focus_index = 0
        self.has_save = load_has_save()

        # Build buttons
        self.btn_new = Button("New Game", self.on_new)
        self.btn_continue = Button(
            "Continue", self.on_continue, enabled=self.has_save
        )
        self.btn_options = Button("Options", self.on_options)
        self.btn_quit = Button("Quit", self.on_quit)
        self.buttons = [
            self.btn_new,
            self.btn_continue,
            self.btn_options,
            self.btn_quit,
        ]

    def start(self):
        self.layout()

    def layout(self):
        w, h = self.game.screen.get_size()
        center_x = w // 2
        start_y = h // 2 - 40
        gap = 72

        for i, b in enumerate(self.buttons):
            b.set_pos_center(center_x, start_y + i * gap)

    # ---- Button actions ----
    def on_new(self):
        # Overwrite save for demo
        ensure_save_dir()
        data = {"started_at": pygame.time.get_ticks()}
        SAVE_PATH.write_text(json.dumps(data))
        next_scene = GameScene(self.game, first_time=True)
        self.request_switch(next_scene)

    def on_continue(self):
        if not self.has_save:
            return
        next_scene = GameScene(self.game, first_time=False)
        self.request_switch(next_scene)

    def on_options(self):
        self.request_switch(OptionsScene(self.game))

    def on_quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    # ---- Event handling ----
    def handle_event(self, e: pygame.event.Event):
        # Mouse into buttons
        for b in self.buttons:
            b.handle_event(e)

        if e.type == pygame.VIDEORESIZE:
            self.layout()
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_DOWN, pygame.K_s):
                self.move_focus(1)
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.move_focus(-1)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate_focused()
        # Basic gamepad support
        if e.type == pygame.JOYBUTTONDOWN:
            if e.button in (0, 7):  # A / Start
                self.activate_focused()
        if e.type == pygame.JOYHATMOTION:
            if e.value[1] == 1:
                self.move_focus(-1)
            elif e.value[1] == -1:
                self.move_focus(1)

    def move_focus(self, delta: int):
        enabled_indices = [i for i, b in enumerate(self.buttons) if b.enabled]
        if not enabled_indices:
            return
        # Map current focus to nearest enabled index
        if self.focus_index not in enabled_indices:
            self.focus_index = enabled_indices[0]
        else:
            idx = enabled_indices.index(self.focus_index)
            idx = (idx + delta) % len(enabled_indices)
            self.focus_index = enabled_indices[idx]
        # Update visual focus state
        for i, b in enumerate(self.buttons):
            b.focused = i == self.focus_index

    def activate_focused(self):
        b = self.buttons[self.focus_index]
        if b.enabled:
            b.action()

    # ---- Draw ----
    def drawing(self, screen: pygame.Surface):
        screen.fill(COLORS.bg)
        w, h = screen.get_size()

        # Title
        title = self.title_font.render(APP_NAME, True, COLORS.accent)
        title_rect = title.get_rect(center=(w // 2, h // 2 - 140))
        screen.blit(title, title_rect)

        # Subtitle
        sub = self.small_font.render(
            "Press Enter / A to select", True, COLORS.text_muted
        )
        sub_rect = sub.get_rect(center=(w // 2, title_rect.bottom + 20))
        screen.blit(sub, sub_rect)

        # Buttons
        for i, b in enumerate(self.buttons):
            b.focused = i == self.focus_index
            b.drawing(screen, self.btn_font)

        # Footer
        foot = self.small_font.render(
            "© 2025 Your Studio", True, COLORS.text_muted
        )
        foot_rect = foot.get_rect(midbottom=(w // 2, h - 16))
        screen.blit(foot, foot_rect)

        # Fade overlay
        if self.alpha > 0:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.alpha)))
            screen.blit(overlay, (0, 0))


class OptionsScene(Scene):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 28)
        self.small = pygame.font.SysFont("arial", 18)

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.KEYDOWN and e.key in (
            pygame.K_ESCAPE,
            pygame.K_BACKSPACE,
        ):
            self.request_switch(TitleScene(self.game))
        if e.type == pygame.VIDEORESIZE:
            pass

    def drawing(self, screen: pygame.Surface):
        screen.fill(COLORS.bg)
        w, h = screen.get_size()
        txt = self.font.render(
            "Options (press Esc to go back)", True, COLORS.text
        )
        rect = txt.get_rect(center=(w // 2, h // 2 - 40))
        screen.blit(txt, rect)

        tip = self.small.render(
            "(Add volume, keybinds, graphics here)", True, COLORS.text_muted
        )
        tip_rect = tip.get_rect(center=(w // 2, rect.bottom + 40))
        screen.blit(tip, tip_rect)

        if self.alpha > 0:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.alpha)))
            screen.blit(overlay, (0, 0))


class GameScene(Scene):
    def __init__(self, game: "Game", *, first_time: bool):
        super().__init__(game)
        self.first_time = first_time
        self.font = pygame.font.SysFont("consolas", 24)

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.request_switch(TitleScene(self.game))

    def drawing(self, screen: pygame.Surface):
        screen.fill((20, 24, 28))
        w, h = screen.get_size()
        msg = "Game started (press Esc to return)"
        if self.first_time:
            msg = "New Game! " + msg
        else:
            msg = "Continue! " + msg
        surf = self.font.render(msg, True, (230, 230, 240))
        screen.blit(surf, surf.get_rect(center=(w // 2, h // 2)))

        if self.alpha > 0:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.alpha)))
            screen.blit(overlay, (0, 0))


# -------------- Game wrapper --------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        # Optional: set caption & custom icon (generated simple icon)
        pygame.display.set_caption(APP_NAME)
        icon = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(icon, COLORS.accent, (16, 16), 14)
        pygame.draw.circle(icon, COLORS.panel, (16, 16), 8)
        pygame.display.set_icon(icon)

        # Resizable window with high-DPI support
        flags = pygame.RESIZABLE | pygame.SCALED
        self.screen = pygame.display.set_mode((WIN_W, WIN_H), flags)
        self.clock = pygame.time.Clock()

        # Connect first gamepad if available
        if pygame.joystick.get_count() > 0:
            self.pad = pygame.joystick.Joystick(0)
            self.pad.init()
        else:
            self.pad = None

        self.current: Scene = TitleScene(self)
        self.current.start()

    def set_scene(self, scene: Scene):
        self.current = scene
        self.current.start()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                    break
                self.current.handle_event(e)

            self.current.update(dt)
            self.current.drawing(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


# -------------- Tests --------------


def run_smoke_tests():
    """Run non-interactive smoke tests. Set RUN_TESTS=1 to execute."""
    # Use dummy video driver to avoid opening a window
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()

    # --- Test 1: Colors default_factory creates independent objects ---
    c1, c2 = Colors(), Colors()
    c1.bg.r = 10
    assert (
        c2.bg.r != 10
    ), "Colors.bg should be a distinct pygame.Color instance (default_factory)."

    # --- Test 2: request_switch triggers game.set_scene after fade out ---
    class DummyGame:
        def __init__(self):
            self.screen = pygame.Surface((800, 600))
            self.last_set_scene = None

        def set_scene(self, s: Scene):
            self.last_set_scene = s

    g = DummyGame()
    a = TitleScene(g)
    b = OptionsScene(g)
    a.start()
    a.request_switch(b)
    # Simulate enough time for full fade (>= 255/600 s)
    a.update(1.0)
    assert (
        g.last_set_scene is b
    ), "After fade-out, Game.set_scene should be called with the next scene."

    # --- Test 3: Continue button enabled only when a save exists ---
    global SAVE_PATH
    with tempfile.TemporaryDirectory() as td:
        orig = SAVE_PATH
        try:
            SAVE_PATH = Path(td) / "save.json"
            # No save -> disabled
            s = TitleScene(g)
            assert (
                not s.btn_continue.enabled
            ), "Continue should be disabled when no save file exists."
            # Create save -> enabled
            SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
            SAVE_PATH.write_text("{}")
            s2 = TitleScene(g)
            assert (
                s2.btn_continue.enabled
            ), "Continue should be enabled when a save file exists."
        finally:
            SAVE_PATH = orig

    # --- Test 4: Button focus moves among enabled buttons ---
    s3 = TitleScene(g)
    s3.btn_continue.enabled = False  # ensure one disabled in the middle
    s3.buttons = [s3.btn_new, s3.btn_continue, s3.btn_options, s3.btn_quit]
    s3.focus_index = 0
    s3.move_focus(1)
    assert (
        s3.focus_index == 2
    ), "Focus should skip disabled buttons when moving."


# -------------- Entry point --------------
if __name__ == "__main__":
    if os.environ.get("RUN_TESTS") == "1":
        run_smoke_tests()
        sys.exit(0)

    ensure_save_dir()
    Game().run()
