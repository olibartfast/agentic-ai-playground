# Installation Guide for Windsurf
## For deb-based Linux distributions (Ubuntu 20.04+, Debian 10+)

### 1. Add the repository to sources.list.d

```bash
sudo apt-get install wget gpg
wget -qO- "https://windsurf-stable.codeiumdata.com/wVxQEIWkwPUEAGf3/windsurf.gpg" | gpg --dearmor > windsurf-stable.gpg
sudo install -D -o root -g root -m 644 windsurf-stable.gpg /etc/apt/keyrings/windsurf-stable.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/windsurf-stable.gpg] https://windsurf-stable.codeiumdata.com/wVxQEIWkwPUEAGf3/apt stable main" | sudo tee /etc/apt/sources.list.d/windsurf.list > /dev/null
rm -f windsurf-stable.gpg
```

### 2. Update packages

```bash
sudo apt install apt-transport-https
sudo apt update
```

### 3. Install Windsurf

```bash
sudo apt install windsurf
```