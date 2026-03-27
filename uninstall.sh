#!/bin/bash
# Mate Smart Lock - Uninstaller
# https://github.com/s7ntech82/Mate-Smart-Lock
set -e

APP_NAME="mate-smart-lock"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
info()    { echo "[INFO]  $*"; }
success() { echo "[OK]    $*"; }
warn()    { echo "[WARN]  $*"; }
error()   { echo "[ERROR] $*" >&2; exit 1; }

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        error "This uninstaller must be run as root. Try: sudo bash uninstall.sh"
    fi
}

# ---------------------------------------------------------------------------
# Remove snap installation
# ---------------------------------------------------------------------------
remove_snap() {
    if command -v snap >/dev/null 2>&1; then
        if snap list "$APP_NAME" >/dev/null 2>&1; then
            info "Removing Snap package..."
            snap remove "$APP_NAME"
            success "Snap package removed."
        else
            info "Snap package not installed. Skipping."
        fi
    else
        info "Snap not available. Skipping Snap removal."
    fi
}

# ---------------------------------------------------------------------------
# Remove deb installation
# ---------------------------------------------------------------------------
remove_deb() {
    if dpkg -s "$APP_NAME" >/dev/null 2>&1; then
        info "Removing .deb package..."
        apt-get remove -y "$APP_NAME"
        success ".deb package removed."
    else
        info ".deb package not installed. Skipping."
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
require_root

echo ""
echo "=========================================="
echo "   Mate Smart Lock - Uninstaller"
echo "=========================================="
echo ""

remove_snap
remove_deb

echo ""
echo "=========================================="
success "Uninstall complete."
echo "  User config at ~/.config/mate-smart-lock/ was NOT removed."
echo "  Delete it manually if you want a clean uninstall."
echo "=========================================="
