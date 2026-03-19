#!/usr/bin/env bash
# Mindful Path — Linux installer
# Sets up the desktop launcher and icons

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DESKTOP="$HOME/.local/share/applications/mindful-path.desktop"

echo "☸  Installing Mindful Path..."

# Generate icons
echo "→ Generating icons..."
python3 "$SCRIPT_DIR/generate_icon.py"

# Write desktop entry with absolute path
echo "→ Installing desktop entry..."
cat > "$APP_DESKTOP" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Mindful Path
GenericName=Habit Tracker
Comment=A Buddhist-inspired daily practice tracker for students
Exec=$SCRIPT_DIR/mindful-path.sh
Icon=mindful-path
Terminal=false
Categories=Education;Utility;
Keywords=habits;mindfulness;meditation;study;buddhism;tracker;
StartupWMClass=mindful-path
StartupNotify=true
EOF

# Make launcher executable
chmod +x "$SCRIPT_DIR/mindful-path.sh"

# Refresh caches
update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor/" 2>/dev/null || true

echo ""
echo "✓ Done. Search 'Mindful Path' in your app launcher."
echo "  Or run directly:  $SCRIPT_DIR/mindful-path.sh"
