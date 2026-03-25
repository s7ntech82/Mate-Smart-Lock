import gi
import logging
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

logger = logging.getLogger(__name__)

try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
    HAS_APPINDICATOR = True
except (ValueError, ImportError):
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3 as AppIndicator
        HAS_APPINDICATOR = True
    except (ValueError, ImportError):
        HAS_APPINDICATOR = False
        logger.warning("AppIndicator3/AyatanaAppIndicator3 not found, falling back to Gtk.StatusIcon")

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self._create_menu()
        
        # Choose icon names based on context
        self.icon_active = "bluetooth-active-symbolic" # Or just "bluetooth"
        self.icon_inactive = "bluetooth-disabled"
        
        if HAS_APPINDICATOR:
            self.indicator = AppIndicator.Indicator.new(
                "mate-smart-lock",
                self.icon_inactive, # Start assumed disconnected or unknown
                AppIndicator.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            self.indicator.set_menu(self.menu)
            self.status_icon = None
        else:
            self.indicator = None
            self.status_icon = Gtk.StatusIcon()
            self.status_icon.set_from_icon_name(self.icon_inactive)
            self.status_icon.connect("popup-menu", self._on_popup_menu)
            self.status_icon.set_tooltip_text("Mate Smart Lock")

    def _create_menu(self):
        self.menu = Gtk.Menu()
        
        self.item_toggle = Gtk.CheckMenuItem(label="Enable Auto-Lock")
        self.item_toggle.set_active(self.app.config.get("auto_lock_enabled", False))
        self.item_toggle.connect("toggled", self._on_toggle_auto_lock)
        self.menu.append(self.item_toggle)
        
        item_lock_now = Gtk.MenuItem(label="Lock Now")
        item_lock_now.connect("activate", lambda _: self.app.lock_manager.lock())
        self.menu.append(item_lock_now)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        item_settings = Gtk.MenuItem(label="Settings")
        item_settings.connect("activate", lambda _: self.app.show_main_window())
        self.menu.append(item_settings)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda _: self.app.quit())
        self.menu.append(item_quit)
        
        self.menu.show_all()

    def _on_toggle_auto_lock(self, widget):
        is_active = widget.get_active()
        self.app.config.set("auto_lock_enabled", is_active)

    def _on_popup_menu(self, icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    def update_state(self, is_connected):
        # Update icon based on state
        icon_name = self.icon_active if is_connected else self.icon_inactive
        tooltip = "Smart Lock: Connected" if is_connected else "Smart Lock: Disconnected"
        if HAS_APPINDICATOR:
            self.indicator.set_icon_full(icon_name, "Proximity State")
        else:
            self.status_icon.set_from_icon_name(icon_name)
            self.status_icon.set_tooltip_text(tooltip)
