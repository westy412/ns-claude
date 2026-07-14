# Deploy: one standalone Vercel project per client

Each client's deck gets its own URL, separate from any existing site. The deck is
already self-contained (only local assets + Google Fonts), so deploying is a
static push.

## Make a self-contained bundle

If the deck folder references assets with `../` (because it lived inside a larger
site), flatten it so everything is root-relative:

```bash
DIST=/tmp/<client>-pitch
rm -rf "$DIST"; mkdir -p "$DIST/assets/img"
# rewrite ../assets/ -> assets/ in the html
sed 's#\.\./assets/#assets/#g' pitch/index.html > "$DIST/index.html"
cp pitch/deck.css pitch/deck.js pitch/visuals-core.js "$DIST/"
cp -R pitch/visuals "$DIST/"            # the diagram files
cp <logos> "$DIST/assets/img/"
# sanity: no leftover ../assets refs
grep -c '\.\./assets' "$DIST/index.html"   # expect 0
```

If the deck was authored standalone from the templates, the folder already is the
bundle, deploy it directly.

## Deploy

```bash
cd "$DIST"           # a fresh dir with no .vercel  => a NEW project
vercel deploy --prod --yes --scope <team>
```

- **Project name** = the directory name, so name the dir well
  (`<client>-pitch` → `<client>-pitch.vercel.app`).
- **`--scope <team>` is required** if the account is in multiple teams; the CLI
  errors and lists the scopes if you omit it. Use the team that owns the work
  (e.g. `novosapien`).
- A fresh dir with no `.vercel/` makes a NEW project rather than redeploying an
  existing one. `--yes` accepts the defaults (new project, name = dir, root = .).

## Verify

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://<client>-pitch.vercel.app
```

- The **clean alias** `https://<project>.vercel.app` is the public one to share
  (expect 200).
- The **per-deployment URLs** (the long `…-<hash>-<team>.vercel.app`) often
  return **401** because the team has deployment protection on. That's expected;
  share the clean alias.

## Redeploy after edits

The deployed deck is a static snapshot. After changing the deck, rebuild the
bundle and run `vercel deploy --prod --yes --scope <team>` again from the same
dir (now it updates the existing project).

## Caveats to surface to the user

- **Speaker notes ship in the page source.** Pressing `N` shows them and anyone
  can view-source. If the notes hold sensitive figures, offer to (a) strip the
  `.snote` blocks from the deployed build, or (b) turn on Vercel password
  protection for the project. Confirm before publishing a sensitive deck.
- **Confirm the URL/name** before the first deploy (it's outward-facing).
