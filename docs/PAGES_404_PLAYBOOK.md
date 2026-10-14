# GitHub Pages builds succeed but page 404s — generic playbook

For any agent, any repo. Copy-paste the probes; read the table; apply the fix.

## 1. What was wrong (this repo's instance)

Pages showed "Deployed / Success" twice, yet
`https://<user>.github.io/<repo>/preview.html` returned 404.

Cause: **publishing source mismatch.** Pages was serving source `/` (root),
but the file lived at `docs/preview.html`. Under root source, URL paths mirror
repo paths, so the page actually resolved at `/docs/preview.html` (which
returned 200 all along). A green deployment only proves *something* built —
it never proves *your path* exists under the configured source.

## 2. Diagnose in 10 seconds (three probes, no login)

```bash
BASE="https://<user>.github.io/<repo>"
for p in "" "preview.html" "docs/preview.html"; do
  printf "%s -> " "/$p"
  curl -s -o /dev/null -w "%{http_code}\n" "$BASE/$p"
done
```

Read the result like this:

| `/` | `/preview.html` | `/docs/preview.html` | Meaning |
|---|---|---|---|
| 200 | 200 | 404 | source = `/docs` ✅, all good |
| 200 | 404 | 200 | source = `/` (root); file only under `/docs` |
| 404 | 404 | 404 | Pages off / still building / wrong branch |
| 200 | 404 | 404 | source = `/`, but neither entry nor file exists |

## 3. Rules (official Pages behavior — verify, don't assume)

1. The entry file (`index.html`) must sit at the **top level of the chosen
   source** (`/` or `/docs`), on the source branch. Case-sensitive.
2. Every other URL mirrors the repo path **under the source**:
   source `/docs` → repo `docs/x.html` serves at `/x.html`;
   source `/` → repo `docs/x.html` serves at `/docs/x.html`.
3. Put an empty `.nojekyll` file **in the source folder** or Jekyll may
   ignore underscore paths and process files you wanted static.
4. Asset paths must be **relative** (`assets/…` from root files,
   `../assets/…` from `/docs` files). Absolute/local paths (`/home/…`,
   `/assets/…`) break on project Pages (served under `/<repo>/`).
5. After changing Settings → Pages, wait 1–2 min and check the Actions
   "pages build and deployment" run before re-probing.
6. Never append GitHub's scaffold (`echo "# …" >> README.md`) to a finished
   repo — it corrupts the README.

## 4. Robust fix (works under either source setting)

Keep one canonical page (e.g. `docs/preview.html` + `docs/index.html`),
then add mirrors so both settings resolve:

- `preview.html` at repo root = copy of `docs/preview.html` with
  `../assets` → `assets` (mechanical `sed`, diff must show only those lines).
- `index.html` at repo root = redirect to `preview.html` + fallback links.
- `.nojekyll` at repo root (in addition to `docs/.nojekyll`).

Then `/preview.html` works with source `/docs`, and both `/` and
`/docs/preview.html` work with source `/`. Recommend `/docs` in Settings;
the mirrors make the recommendation non-fatal if ignored.

In this repo the page is single-file with zero asset references, so the
root `preview.html` and `docs/preview.html` are byte-identical mirrors,
plus `index.html` redirects at both levels and `.nojekyll` in both folders.

## 5. Push checklist

```bash
git status --short          # know what's dirty before staging
git add -A && git commit -m "<message>"
git push origin main && git status --short   # expect clean
git ls-tree -r origin/main --name-only | grep -E "index.html|preview.html|nojekyll"
sleep 75   # let Pages rebuild
# re-run the three probes from section 2; expect 200/200/200 (or 200/404/200
# if you intentionally serve a single source — then document which one)
```
