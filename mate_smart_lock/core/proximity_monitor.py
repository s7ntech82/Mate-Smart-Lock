import logging
import threading
from gi.repository import GLib
from .bluetooth_manager import BluetoothManager

logger = logging.getLogger(__name__)

class ProximityMonitor:
    def __init__(self, config, lock_manager):
        self.config = config
        self.lock_manager = lock_manager
        self.is_running = False
        self._source_id = None
        self._current_interval = None
        
        # State
        self.is_currently_locked = False
        self._missed_pings = 0
        
        # Callbacks for UI updates
        self.on_state_changed = None

    def start(self):
        if self.is_running:
            return
        logger.info("Starting proximity monitor...")
        self.is_running = True
        self._missed_pings = 0
        self._current_interval = self.config.get("polling_interval", 5)
        self._source_id = GLib.timeout_add_seconds(self._current_interval, self._check_proximity)
        
        # Trigger an immediate check
        GLib.idle_add(self._check_proximity)

    def stop(self):
        if not self.is_running:
            return
        logger.info("Stopping proximity monitor...")
        self.is_running = False
        if self._source_id is not None:
            GLib.source_remove(self._source_id)
            self._source_id = None

    def restart(self):
        self.stop()
        self.start()

    def _check_proximity(self):
        if not self.is_running:
            return False # Don't run again

        # Check if interval changed
        configured_interval = self.config.get("polling_interval", 5)
        if configured_interval != self._current_interval:
            self._current_interval = configured_interval
            # Remove current and reschedule with new interval
            self._source_id = GLib.timeout_add_seconds(self._current_interval, self._check_proximity)
            return False

        mac = self.config.get("target_device_mac")
        if not mac:
            if self.on_state_changed:
                self.on_state_changed(False)
            return True

        is_connected = BluetoothManager.is_device_connected(mac)
        if self.on_state_changed:
            try:
                self.on_state_changed(is_connected)
            except Exception as e:
                logger.error(f"UI Callback error: {e}")

        debounce_limit = self.config.get("debounce_limit", 2)
        auto_lock = self.config.get("auto_lock_enabled", False)
        auto_unlock = self.config.get("auto_unlock_enabled", False)

        if is_connected:
            self._missed_pings = 0
            if self.is_currently_locked and auto_unlock:
                logger.info("Device connected. Unlocking...")
                self.is_currently_locked = False
                threading.Thread(target=self.lock_manager.unlock, daemon=True).start()
        else:
            self._missed_pings += 1
            if self._missed_pings >= debounce_limit and not self.is_currently_locked and auto_lock:
                logger.info(f"Device disconnected for {self._missed_pings} checks. Locking...")
                self.is_currently_locked = True
                threading.Thread(target=self.lock_manager.lock, daemon=True).start()
                
        return True # Keep GLib timeout running
