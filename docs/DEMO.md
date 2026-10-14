# Demo recording (reproducible, keeps README fresh)

GitHub renders GIF/SVG inline but strips `<video>`. Use this pipeline so the demo never goes stale:

## Option A — terminal GIF in one command (recommended)

```bash
# 1. record while you run the repo
asciinema rec demo.cast   # then run: docker compose run --rm reproduce
# 2. render to GIF
agg demo.cast docs/screenshots/demo.gif
# 3. embed in README:
# ![terminal demo](docs/screenshots/demo.gif)
```

Keep the GIF < 8 MB, ~800 px wide, 10–15 s (trim idle with `--idle-limit 2`).

## Option B — scripted (vhs `.tape`, regenerable)

```tape
Output docs/screenshots/demo.gif
Set Shell "bash" / Set Width 900 / Set Height 520
Type "docker compose run --rm reproduce" Enter
Sleep 8s
```

`vhs demo.tape` re-renders identically after every code change.

## Option C — web app (this repo's preview.html)

The Playwright captures in `docs/screenshots/` were taken with:

```js
await page.goto('file:///.../preview.html');
await page.screenshot({ path: 'preview-hero.png' });          // viewport
await page.screenshot({ path: 'preview-full.png', fullPage: true });
```

For a video: record the browser while clicking *Mine one block* + answering the quiz, convert with `ffmpeg -i demo.mp4 -vf fps=12,scale=800:-1 demo.gif`, then `gifsicle -O3` to shrink.

Link interactive players (asciinema.org / hosted `preview.html` via Pages) as click-throughs behind the inline GIF poster.
