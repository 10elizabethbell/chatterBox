"""Microphone capture with a pre-roll ring buffer.

The input stream runs continuously so the ~500ms of audio *before* the
hotkey press is kept — otherwise the first word gets clipped while the
key event and stream spin-up race the speaker.
"""

from __future__ import annotations

import collections
import threading

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16_000  # what Parakeet expects
CHANNELS = 1
BLOCK_SIZE = 512  # ~32ms per callback
PRE_ROLL_SECONDS = 0.5


class Recorder:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._recording = False
        self._chunks: list[np.ndarray] = []
        pre_roll_blocks = int(PRE_ROLL_SECONDS * SAMPLE_RATE / BLOCK_SIZE) + 1
        self._pre_roll: collections.deque[np.ndarray] = collections.deque(
            maxlen=pre_roll_blocks
        )
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize=BLOCK_SIZE,
            dtype="float32",
            callback=self._callback,
        )

    def _callback(self, indata: np.ndarray, frames, time, status) -> None:
        if status:
            print(f"[audio] {status}", flush=True)
        mono = indata[:, 0].copy()
        with self._lock:
            if self._recording:
                self._chunks.append(mono)
            else:
                self._pre_roll.append(mono)

    def open(self) -> None:
        self._stream.start()

    def close(self) -> None:
        self._stream.stop()
        self._stream.close()

    def start(self) -> None:
        with self._lock:
            self._chunks = list(self._pre_roll)
            self._pre_roll.clear()
            self._recording = True

    def stop(self) -> np.ndarray:
        """Stop capturing and return the utterance as float32 samples."""
        with self._lock:
            self._recording = False
            chunks, self._chunks = self._chunks, []
        if not chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks)
