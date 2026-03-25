# Mate Smart Lock

A modern alternative to BlueProximity for Linux, targeting the Ubuntu MATE desktop.
This application automatically locks and unlocks your session based on the proximity of a connected Bluetooth device (e.g., your smartphone).

## Features
- **Auto-Lock:** Executes `loginctl lock-session` when your device disconnects.
- **Auto-Unlock:** Executes `loginctl unlock-session` when your device reconnects (requires correct polkit configurations).
- **Customizable Delay:** Set polling intervals and debounce limit (grace period) to avoid false positives.
- **Tray Icon:** GTK3 AppIndicator to check state, manage locks, and quickly access preferences.
- **No Heavy Dependencies:** Uses standard `bluetoothctl` and `python3-gi`.

## Usage
Launch `Mate Smart Lock` from your applications menu or by running `mate-smart-lock` in the terminal.
A tray icon will appear. Right-click the icon to select "Settings".

In the Settings:
1. Under the **Device** tab, click "Scan Paired Devices" and select your phone.
2. In the **Behavior** tab, turn on "Enable Auto-Lock".
3. Close the settings. If your phone disconnects, your screen will lock.

*(You can override the commands in the Advanced tab)*
