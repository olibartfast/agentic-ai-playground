# Update Node.js

> TL;DR: Remove the old Node.js, install the latest LTS via Snap, verify `npx`, then run `npx @sourcegraph/amp`.

---
## 1. Replace the existing Node.js / npm

```bash
# Remove current Node.js and npm packages
sudo apt-get purge nodejs npm
sudo apt-get autoremove
```

## 2. Install the latest Node.js via Snap

```bash
sudo snap install node --classic
# (Snap bundles npm, so no separate npm install is needed)
```

## 3. Ensure `npx` is on your PATH

```bash
# If you get “/usr/bin/npx: No such file or directory”, add the Snap bin dir
 export PATH="/usr/local/bin:$PATH"
# Verify everything works
npx --version
```

## 4. Install CLI mode for Sourcegraph AMP

```bash
npx @sourcegraph/amp
```

---

> Make the PATH change permanent by adding the `export` line to `~/.bashrc` or `~/.zshrc` if desired.
