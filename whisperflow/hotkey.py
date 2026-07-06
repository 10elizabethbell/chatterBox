"""Global hold-key push-to-talk listener.

Default key is right Option — pynput sees modifier keys system-wide and
they never conflict with typing. (The Fn key that Wispr Flow uses isn't
reliably observable from pynput; a Swift event tap is the upgrade path.)

Requires the hosting app (your terminal, while prototyping) to have
Accessibility + Input Monitoring permission in System Settings.
"""

from __future__ import annotations

from typing import Callable

from pynput import keyboard

DEFAULT_KEY = keyboard.Key.alt_r


class PushToTalk:
    def __init__(
        self,
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        key: keyboard.Key = DEFAULT_KEY,
    ) -> None:
        self._key = key
        self._on_start = on_start
        self._on_stop = on_stop
        self._held = False
        self._listener = keyboard.Listener(
            on_press=self._press, on_release=self._release
        )

    def _press(self, key) -> None:
        if key == self._key and not self._held:
            self._held = True
            self._on_start()

    def _release(self, key) -> None:
        if key == self._key and self._held:
            self._held = False
            self._on_stop()

    def run_forever(self) -> None:
        with self._listener:
            self._listener.join()
