import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from ..core.bluetooth_manager import BluetoothManager
import threading

class MainWindow(Gtk.Window):
    def __init__(self, app):
        super().__init__(title="Mate Smart Lock Settings")
        self.app = app
        self.set_default_size(500, 400)
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Base icon
        self.set_icon_name("preferences-system-bluetooth")
        
        # Core UI
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        
        self.notebook.append_page(self._create_device_tab(), Gtk.Label(label="Device"))
        self.notebook.append_page(self._create_behavior_tab(), Gtk.Label(label="Behavior"))
        self.notebook.append_page(self._create_advanced_tab(), Gtk.Label(label="Advanced"))
        
        self.connect("delete-event", self._on_delete_event)

    def _on_delete_event(self, widget, event):
        self.hide()
        return True # Prevent destruction

    # ------ DEVICE TAB ------
    def _create_device_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)
        
        hbox_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        btn_scan = Gtk.Button(label="Scan Paired Devices")
        btn_scan.connect("clicked", self._on_scan_clicked)
        hbox_buttons.pack_start(btn_scan, False, False, 0)
        
        self.btn_test = Gtk.Button(label="Test Connection")
        self.btn_test.connect("clicked", self._on_test_clicked)
        hbox_buttons.pack_start(self.btn_test, False, False, 0)
        vbox.pack_start(hbox_buttons, False, False, 0)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-activated", self._on_device_selected)
        scrolled.add(self.listbox)
        vbox.pack_start(scrolled, True, True, 0)
        
        self.lbl_status = Gtk.Label(label="Selected: None")
        self.lbl_status.set_halign(Gtk.Align.START)
        vbox.pack_start(self.lbl_status, False, False, 0)
        
        self._refresh_device_list()
        
        saved_mac = self.app.config.get("target_device_mac")
        if saved_mac:
            name = self.app.config.get("target_device_name", saved_mac)
            self.lbl_status.set_text(f"Selected: {name} ({saved_mac})")
            
        return vbox

    def _refresh_device_list(self):
        # Clear existing
        for child in self.listbox.get_children():
            self.listbox.remove(child)
            
        devices = BluetoothManager.get_paired_devices()
        for dev in devices:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_border_width(5)
            lbl_name = Gtk.Label(label=dev["name"])
            lbl_mac = Gtk.Label(label=f"<small>{dev['mac']}</small>")
            lbl_mac.set_use_markup(True)
            hbox.pack_start(lbl_name, False, False, 0)
            hbox.pack_end(lbl_mac, False, False, 0)
            row.add(hbox)
            row.device_data = dev
            self.listbox.add(row)
        self.listbox.show_all()

    def _on_scan_clicked(self, widget):
        self._refresh_device_list()

    def _on_device_selected(self, listbox, row):
        dev = row.device_data
        self.app.config.set("target_device_mac", dev["mac"])
        self.app.config.set("target_device_name", dev["name"])
        self.lbl_status.set_text(f"Selected: {dev['name']} ({dev['mac']})")
        # Restart monitor to pick up new device
        if hasattr(self.app, 'proximity_monitor'):
            self.app.proximity_monitor.restart()

    def _on_test_clicked(self, widget):
        mac = self.app.config.get("target_device_mac")
        if not mac:
            self._show_dialog("Error", "No device selected.")
            return
            
        self.btn_test.set_sensitive(False)
        self.btn_test.set_label("Testing...")
        
        def run_test():
            is_connected = BluetoothManager.is_device_connected(mac)
            GLib.idle_add(self._test_finished, is_connected)
            
        threading.Thread(target=run_test, daemon=True).start()

    def _test_finished(self, is_connected):
        self.btn_test.set_sensitive(True)
        self.btn_test.set_label("Test Connection")
        status = "Connected" if is_connected else "Disconnected"
        self._show_dialog("Test Result", f"Device is currently: {status}")

    # ------ BEHAVIOR TAB ------
    def _create_behavior_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        vbox.set_border_width(15)
        
        # Auto-Lock
        hbox_lock = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        sw_lock = Gtk.Switch()
        sw_lock.set_active(self.app.config.get("auto_lock_enabled", False))
        sw_lock.connect("notify::active", self._on_switch_changed, "auto_lock_enabled")
        hbox_lock.pack_start(Gtk.Label(label="Enable Auto-Lock"), False, False, 0)
        hbox_lock.pack_end(sw_lock, False, False, 0)
        vbox.pack_start(hbox_lock, False, False, 0)
        
        # Auto-Unlock
        hbox_unlock = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        sw_unlock = Gtk.Switch()
        sw_unlock.set_active(self.app.config.get("auto_unlock_enabled", False))
        sw_unlock.connect("notify::active", self._on_switch_changed, "auto_unlock_enabled")
        hbox_unlock.pack_start(Gtk.Label(label="Enable Auto-Unlock"), False, False, 0)
        hbox_unlock.pack_end(sw_unlock, False, False, 0)
        vbox.pack_start(hbox_unlock, False, False, 0)
        
        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 10)
        
        # Polling Interval
        hbox_poll = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        adj_poll = Gtk.Adjustment(value=self.app.config.get("polling_interval", 5), lower=2, upper=60, step_increment=1)
        spin_poll = Gtk.SpinButton(adjustment=adj_poll)
        spin_poll.connect("value-changed", self._on_spin_changed, "polling_interval")
        hbox_poll.pack_start(Gtk.Label(label="Polling Interval (seconds)"), False, False, 0)
        hbox_poll.pack_end(spin_poll, False, False, 0)
        vbox.pack_start(hbox_poll, False, False, 0)
        
        # Debounce Limit
        hbox_debounce = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        adj_debounce = Gtk.Adjustment(value=self.app.config.get("debounce_limit", 2), lower=1, upper=10, step_increment=1)
        spin_debounce = Gtk.SpinButton(adjustment=adj_debounce)
        spin_debounce.connect("value-changed", self._on_spin_changed, "debounce_limit")
        hbox_debounce.pack_start(Gtk.Label(label="Debounce (missed checks before lock)"), False, False, 0)
        hbox_debounce.pack_end(spin_debounce, False, False, 0)
        vbox.pack_start(hbox_debounce, False, False, 0)
        
        return vbox

    def _on_switch_changed(self, switch, gparam, config_key):
        is_active = switch.get_active()
        self.app.config.set(config_key, is_active)
        # sync tray toggle
        if config_key == "auto_lock_enabled" and hasattr(self.app, 'tray_icon'):
            self.app.tray_icon.item_toggle.set_active(is_active)

    def _on_spin_changed(self, spin, config_key):
        val = int(spin.get_value())
        self.app.config.set(config_key, val)

    # ------ ADVANCED TAB ------
    def _create_advanced_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(15)
        
        lbl_info = Gtk.Label(label="Warning: Changing these commands might prevent locking/unlocking.")
        lbl_info.set_line_wrap(True)
        vbox.pack_start(lbl_info, False, False, 10)
        
        # Lock Command
        vbox.pack_start(Gtk.Label(label="Lock Command:", xalign=0), False, False, 0)
        entry_lock = Gtk.Entry()
        entry_lock.set_text(self.app.config.get("lock_command", "loginctl lock-session"))
        entry_lock.connect("changed", self._on_entry_changed, "lock_command")
        vbox.pack_start(entry_lock, False, False, 0)
        
        # Unlock Command
        vbox.pack_start(Gtk.Label(label="Unlock Command:", xalign=0), False, False, 0)
        entry_unlock = Gtk.Entry()
        entry_unlock.set_text(self.app.config.get("unlock_command", "loginctl unlock-session"))
        entry_unlock.connect("changed", self._on_entry_changed, "unlock_command")
        vbox.pack_start(entry_unlock, False, False, 0)
        
        return vbox

    def _on_entry_changed(self, entry, config_key):
        self.app.config.set(config_key, entry.get_text())

    # ------ HELPERS ------
    def _show_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
