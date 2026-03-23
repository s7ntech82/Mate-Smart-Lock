import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from .core.config import Config
from .core.lock_manager import LockManager
from .core.proximity_monitor import ProximityMonitor
from .ui.tray_icon import TrayIcon
from .ui.main_window import MainWindow

class MateSmartLockApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.mate_smart_lock.app", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.config = Config()
        self.lock_manager = LockManager(self.config)
        self.proximity_monitor = ProximityMonitor(self.config, self.lock_manager)
        
        self.tray_icon = None
        self.main_window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        
        # Initialize UI
        self.tray_icon = TrayIcon(self)
        self.main_window = MainWindow(self)
        self.add_window(self.main_window)
        
        # Connect monitor to UI
        self.proximity_monitor.on_state_changed = self._on_proximity_state_changed
        
        # Start background task
        self.proximity_monitor.start()

    def do_activate(self):
        # Don't show the main window automatically on launch. Let the tray icon handle it.
        pass

    def show_main_window(self):
        self.main_window.show_all()
        self.main_window.present()

    def _on_proximity_state_changed(self, is_connected):
        # Update tray icon state
        if self.tray_icon:
            self.tray_icon.update_state(is_connected)
            
    def quit(self):
        self.proximity_monitor.stop()
        super().quit()
