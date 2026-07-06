"""Entry point.

    whisperflow                  # push-to-talk mode: hold right Option, speak, release
    whisperflow transcribe FILE  # transcribe a wav/audio file (no mic/hotkey needed)
"""

from __future__ import annotations

import sys
import time


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "transcribe":
        run_file(args[1])
    else:
        run_ptt()


def run_file(path: str) -> None:
    from whisperflow.transcriber import Transcriber

    t = Transcriber()
    t0 = time.perf_counter()
    text = t.transcribe_file(path)
    print(f"[{time.perf_counter() - t0:.2f}s] {text}")


def run_ptt() -> None:
    from whisperflow.audio import Recorder
    from whisperflow.hotkey import PushToTalk
    from whisperflow.transcriber import Transcriber

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

    print("Hold RIGHT OPTION to talk, release to transcribe. Ctrl-C to quit.")
    ptt = PushToTalk(on_start=on_start, on_stop=on_stop)
    try:
        ptt.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        recorder.close()


if __name__ == "__main__":
    main()
