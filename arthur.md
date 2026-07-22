# chatterBot — spin-up

Local Wispr Flow clone: menu-bar dictation app (on-device Parakeet transcription
+ Claude Haiku cleanup, typed at the cursor). Say **"arthur, spin up my
chatterBot project"**. One Ghostty window per plain line (opened at this
directory); `@run` = headless; `@open` = macOS open.

```spinup
claude
# launch the menu-bar app itself (no window; icon appears in the menu bar)
@run open build/ChatterBot.app
```
