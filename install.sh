#!/bin/bash
# Mate Smart Lock - Installer
# https://github.com/s7ntech82/Mate-Smart-Lock
set -e

APP_NAME="mate-smart-lock"
VERSION="0.1.0"
GITHUB_REPO="s7ntech82/Mate-Smart-Lock"
RELEASES_URL="https://github.com/${GITHUB_REPO}/releases/download/v${VERSION}"

DEB_PACKAGE="${APP_NAME}_${VERSION}_all.deb"
SNAP_AMD64="${APP_NAME}_${VERSION}_amd64.snap"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
info()    { echo "[INFO]  $*"; }
success() { echo "[OK]    $*"; }
warn()    { echo "[WARN]  $*"; }
error()   { echo "[ERROR] $*" >&2; exit 1; }

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        error "This installer must be run as root. Try: sudo bash install.sh"
    fi
}

# ---------------------------------------------------------------------------
# Detect architecture
# ---------------------------------------------------------------------------
detect_arch() {
    ARCH="$(uname -m)"
    case "$ARCH" in
        x86_64)  ARCH="amd64" ;;
        aarch64) ARCH="arm64" ;;
        *)        warn "Unsupported architecture: $ARCH"; ARCH="unknown" ;;
    esac
    info "Detected architecture: $ARCH"
}

# ---------------------------------------------------------------------------
# Snap install
# ---------------------------------------------------------------------------
install_via_snap() {
    info "Snap is available. Installing via Snap..."

    if [ "$ARCH" != "amd64" ]; then
        warn "Snap package is only available for amd64. Falling back to .deb."
        return 1
    fi

    SNAP_FILE="$(mktemp --suffix=.snap)"
    info "Downloading ${SNAP_AMD64}..."
    if ! curl -fsSL "${RELEASES_URL}/${SNAP_AMD64}" -o "$SNAP_FILE"; then
        warn "Failed to download snap package. Falling back to .deb."
        rm -f "$SNAP_FILE"
        return 1
    fi

    snap install --dangerous "$SNAP_FILE"
    rm -f "$SNAP_FILE"
    success "Mate Smart Lock installed via Snap."
    return 0
}

# ---------------------------------------------------------------------------
# Deb install
# ---------------------------------------------------------------------------
install_via_deb() {
    info "Installing via .deb package..."

    DEB_FILE="$(mktemp --suffix=.deb)"
    info "Downloading ${DEB_PACKAGE}..."
    if ! curl -fsSL "${RELEASES_URL}/${DEB_PACKAGE}" -o "$DEB_FILE"; then
        rm -f "$DEB_FILE"
        error "Failed to download .deb package from:\n  ${RELEASES_URL}/${DEB_PACKAGE}"
    fi

    info "Installing package..."
    dpkg -i "$DEB_FILE" || true   # allow dependency failures; fixed below
    apt-get install -f -y         # resolve any missing dependencies
    rm -f "$DEB_FILE"
    success "Mate Smart Lock installed via .deb."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
require_root
detect_arch

echo ""
echo "=========================================="
echo "   Mate Smart Lock v${VERSION} Installer"
echo "=========================================="
echo ""

# Prefer Snap when available
if command -v snap >/dev/null 2>&1; then
    install_via_snap || install_via_deb
else
    info "Snap not found. Using .deb installation."
    install_via_deb
fi

echo ""
echo "=========================================="
success "Installation complete!"
echo "  Launch: mate-smart-lock"
echo "  Or find it in your applications menu."
echo "=========================================="
