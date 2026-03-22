import os
import subprocess
import logging
from gi.repository import Gio, GLib

logger = logging.getLogger(__name__)

class LockManager:
    def __init__(self, config):
        self.config = config

    def lock(self):
        command = self.config.get("lock_command", "")
        if command and command != "loginctl lock-session":
            logger.info(f"Executing custom lock command: {command}")
            self._execute(command)
        else:
            self._dbus_lock()

    def unlock(self):
        command = self.config.get("unlock_command", "")
        if command and command != "loginctl unlock-session":
            logger.info(f"Executing custom unlock command: {command}")
            self._execute(command)
        else:
            self._dbus_unlock()

    def _dbus_lock(self):
        screensaver_services = [
            ("org.gnome.ScreenSaver",        "/org/gnome/ScreenSaver",        "org.gnome.ScreenSaver"),
            ("org.mate.ScreenSaver",         "/org/mate/ScreenSaver",         "org.mate.ScreenSaver"),
            ("org.freedesktop.ScreenSaver",  "/org/freedesktop/ScreenSaver",  "org.freedesktop.ScreenSaver"),
        ]
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        for name, path, iface in screensaver_services:
            try:
                bus.call_sync(name, path, iface, "Lock", None, None,
                              Gio.DBusCallFlags.NONE, 1500, None)
                logger.info(f"Screen locked via D-Bus {name}")
                return
            except Exception:
                continue

        # Last resort: lock via login1 on system bus
        try:
            session_id = os.environ.get("XDG_SESSION_ID", "auto")
            sbus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            result = sbus.call_sync(
                "org.freedesktop.login1", "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager", "GetSession",
                GLib.Variant("(s)", (session_id,)),
                GLib.VariantType.new("(o)"),
                Gio.DBusCallFlags.NONE, -1, None
            )
            sbus.call_sync(
                "org.freedesktop.login1", result[0],
                "org.freedesktop.login1.Session", "Lock",
                None, None, Gio.DBusCallFlags.NONE, -1, None
            )
            logger.info("Screen locked via D-Bus login1")
        except Exception as e:
            logger.error(f"All D-Bus lock attempts failed: {e}")

    def _dbus_unlock(self):
        try:
            session_id = os.environ.get("XDG_SESSION_ID", "auto")
            bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            result = bus.call_sync(
                "org.freedesktop.login1",
                "/org/freedesktop/login1",
                "org.freedesktop.login1.Manager",
                "GetSession",
                GLib.Variant("(s)", (session_id,)),
                GLib.VariantType.new("(o)"),
                Gio.DBusCallFlags.NONE,
                -1, None
            )
            session_path = result[0]
            bus.call_sync(
                "org.freedesktop.login1",
                session_path,
                "org.freedesktop.login1.Session",
                "Unlock",
                None, None,
                Gio.DBusCallFlags.NONE,
                -1, None
            )
            logger.info("Screen unlocked via D-Bus login1")
        except Exception as e:
            logger.warning(f"D-Bus unlock failed ({e}), falling back to loginctl")
            self._execute("loginctl unlock-session")

    def _execute(self, command_str):
        if not command_str:
            return
        try:
            subprocess.run(command_str, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Command execution failed: {e}")
