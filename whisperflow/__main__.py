"""Entry point.

    whisperflow                  # push-to-talk: hold right Option, speak, release -> text pastes at cursor
    whisperflow --print-only     # push-to-talk without pasting (terminal output only)
    whisperflow transcribe FILE  # transcribe a wav/audio file (no mic/hotkey needed)
    whisperflow type "TEXT"      # wait 3s (focus a target app), then paste TEXT at the cursor
"""

from __future__ import annotations

import sys
import time


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "transcribe":
        run_file(args[1])
    elif args and args[0] == "type":
        run_type(" ".join(args[1:]))
    else:
        run_ptt(inject="--print-only" not in args)


def run_file(path: str) -> None:
    from whisperflow.transcriber import Transcriber

    t = Transcriber()
    t0 = time.perf_counter()
    text = t.transcribe_file(path)
    print(f"[{time.perf_counter() - t0:.2f}s] {text}")


def run_type(text: str) -> None:
    from whisperflow.inject import insert_text

    print("Focus the target app — pasting in 3s ...")
    time.sleep(3)
    insert_text(text)
    print("done")


def run_ptt(inject: bool = True) -> None:
    from whisperflow.audio import Recorder
    from whisperflow.hotkey import PushToTalk
    from whisperflow.transcriber import Transcriber

    if inject:
        from whisperflow.inject import insert_text

    transcriber = Transcriber()
    transcriber.warm_up()

    recorder = Recorder()
    recorder.open()

    def on_start() -> None:
        recorder.start()
        print("● recording ... (release to transcribe)", flush=True)

    def on_stop() -> None:
        samples = recorder.stop()
        seconds = len(samples) / 16_000
        t0 = time.perf_counter()
        text = transcriber.transcribe(samples)
        dt = time.perf_counter() - t0
        print(f"○ {seconds:.1f}s audio → transcribed in {dt:.2f}s")
        print(f"  {text!r}", flush=True)
        if inject and text:
            insert_text(text + " ")

    mode = "text pastes at the cursor" if inject else "print-only"
    print(f"Hold RIGHT OPTION to talk, release to transcribe ({mode}). Ctrl-C to quit.")
    ptt = PushToTalk(on_start=on_start, on_stop=on_stop)
    try:
        ptt.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        recorder.close()


if __name__ == "__main__":
    main()
