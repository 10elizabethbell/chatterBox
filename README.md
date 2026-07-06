# whisperFlow

Local Wispr Flow clone for macOS: hold a key, speak, release — text appears.
On-device transcription via NVIDIA Parakeet TDT v3 (MLX, runs on Apple Silicon),
with a Claude Haiku cleanup pass planned (milestone 3).

## Status: milestone 2

- [x] Hold-key push-to-talk → mic capture (with 500ms pre-roll) → Parakeet transcript printed to terminal
- [x] Milestone 2: insert text into the focused app (clipboard + Cmd-V, clipboard restored after)
- [ ] Milestone 3: Claude Haiku cleanup pass (filler removal, formatting, personal dictionary, per-app tone)
- [ ] Milestone 4: skip-short-utterance rule, secure-input detection, menu-bar UI

## Setup

```sh
uv venv --python 3.12
uv pip install -e .
```

First run downloads the ~1.2GB Parakeet model from HuggingFace.

## Usage

```sh
# push-to-talk: hold RIGHT OPTION, speak, release -> text pastes at the cursor
.venv/bin/whisperflow

# same, but terminal output only (no pasting)
.venv/bin/whisperflow --print-only

# paste test without the mic: focus any text field within 3s
.venv/bin/whisperflow type "hello from whisperflow"

# transcribe a wav without mic/hotkey (16kHz mono; convert with afconvert)
.venv/bin/whisperflow transcribe path/to/audio.wav
```

Quick self-test without speaking:

```sh
say -o /tmp/t.aiff "testing one two three" && afconvert -f WAVE -d LEI16@16000 -c 1 /tmp/t.aiff /tmp/t.wav
.venv/bin/whisperflow transcribe /tmp/t.wav
```

## Permissions

Push-to-talk mode needs your terminal app to have, under System Settings → Privacy & Security:

- **Microphone** (prompted automatically on first run)
- **Input Monitoring** and **Accessibility** (for the global hotkey listener; add your terminal manually)

## Performance (M-series, measured)

- Model load: ~0.7s (warm start; 43s first-ever download)
- Warm transcription: **~0.06s** for a 3.5s utterance
