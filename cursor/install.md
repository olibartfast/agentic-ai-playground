Here is the **rewritten Markdown guide** for installing and running **Cursor IDE on Linux via AppImage**, now using a `VERSION` variable for flexibility:

---

````markdown
# Cursor IDE – Linux AppImage Installation Guide

A lightweight guide to install and run **Cursor IDE** using the **AppImage** format on Linux. No root access or package manager required.

## Table of Contents
- [Download and Run](#download-and-run)
- [Optional: Desktop Integration](#optional-desktop-integration)
- [Security – `--no-sandbox` Flag](#security---no-sandbox-flag)
- [Troubleshooting](#troubleshooting)
- [Updating Cursor](#updating-cursor)
- [Resources](#resources)

---

## Download and Run

1. **Set the Version and Download**

Replace the version string below with the latest available version if needed:

```bash
# Define version
VERSION=1.3.8

# Download the AppImage
wget https://cursor.com/downloads/Cursor-$VERSION-x86_64.AppImage

# Rename for convenience
mv Cursor-$VERSION-x86_64.AppImage cursor.AppImage

# Make it executable
chmod +x cursor.AppImage

# Run Cursor
./cursor.AppImage
````

---

## Optional: Desktop Integration

To launch Cursor from your system menu (GNOME, KDE, etc.):

```bash
# Move AppImage to a permanent directory
mkdir -p ~/Applications
mv cursor.AppImage ~/Applications/

# Create a .desktop launcher
cat <<EOF > ~/.local/share/applications/cursor.desktop
[Desktop Entry]
Name=Cursor
Exec=$HOME/Applications/cursor.AppImage
Icon=cursor
Type=Application
Categories=Development;
EOF
```

You may need to refresh the desktop database or re-login to see the icon in your app launcher.

---

## Security – `--no-sandbox` Flag

Cursor uses a Chromium-based sandbox for process isolation and security.

You should only disable it if Cursor fails to launch due to sandbox errors, which may happen when:

* Running inside a Docker container
* Running as `root` (insecure, not recommended)
* Using specific WSL or Wayland configurations

### Run with `--no-sandbox` (only if necessary):

```bash
./cursor.AppImage --no-sandbox
```

> ⚠️ **Disabling the sandbox exposes your system to potential security threats. Use with caution.**

---

## Troubleshooting

### `cursor: command not found`

If you want to launch Cursor with a simple `cursor` command:

```bash
echo "alias cursor='$HOME/Applications/cursor.AppImage'" >> ~/.bashrc
source ~/.bashrc
```

### Missing Runtime Dependencies

On some Linux distributions (especially minimal ones), you may need to install required libraries:

```bash
sudo apt update
sudo apt install libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils
```

### Extensions Failing to Install

* Check internet connectivity
* Try installing extensions manually via `.vsix`
* Clear extension cache:

  * Go to **Help → Toggle Developer Tools**
  * In the console, run:

    ```js
    localStorage.clear()
    ```

### GPU or Rendering Issues

Disable hardware acceleration in `settings.json`:

```json
{
  "disable-hardware-acceleration": true
}
```

### Wayland Compatibility Issues

If using Wayland and encountering visual glitches or input problems, run Cursor with the X11 backend:

```bash
./cursor.AppImage --ozone-platform=x11
```

---

## Updating Cursor

Cursor AppImage does **not auto-update**. To manually update:

```bash
# Set the new version
VERSION=1.3.9

# Download and replace
wget -O ~/Applications/cursor.AppImage https://cursor.com/downloads/Cursor-$VERSION-x86_64.AppImage
chmod +x ~/Applications/cursor.AppImage
```

---

## Resources

* 📘 [Official Documentation](https://docs.cursor.sh)
* 💬 [Community Forum](https://forum.cursor.sh)
* 🐞 [GitHub Issues](https://github.com/getcursor/cursor/issues)
* ⌨️ In-App: **Help → Keyboard Shortcuts Reference**

---

