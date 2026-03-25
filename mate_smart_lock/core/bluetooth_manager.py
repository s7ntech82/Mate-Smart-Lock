import logging
from gi.repository import Gio, GLib

logger = logging.getLogger(__name__)

class BluetoothManager:
    _bus = None
    _path_cache = {}  # mac -> D-Bus object path

    @classmethod
    def _get_bus(cls):
        try:
            if cls._bus is None or cls._bus.is_closed():
                cls._bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        except Exception:
            cls._bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        return cls._bus

    @classmethod
    def _get_managed_objects(cls):
        result = cls._get_bus().call_sync(
            "org.bluez", "/",
            "org.freedesktop.DBus.ObjectManager", "GetManagedObjects",
            None, None, Gio.DBusCallFlags.NONE, -1, None
        )
        return result.unpack()[0]

    @classmethod
    def get_paired_devices(cls):
        devices = []
        try:
            for path, interfaces in cls._get_managed_objects().items():
                props = interfaces.get("org.bluez.Device1")
                if props and props.get("Paired"):
                    mac = props.get("Address", "")
                    name = props.get("Name") or props.get("Alias") or mac
                    devices.append({"mac": mac, "name": name})
                    cls._path_cache[mac.upper()] = path
        except Exception as e:
            logger.error(f"Failed to get paired devices via D-Bus: {e}")
        return devices

    @classmethod
    def _find_device_path(cls, mac_address):
        key = mac_address.upper()
        if key in cls._path_cache:
            return cls._path_cache[key]
        # Path not cached yet — search ObjectManager
        try:
            for path, interfaces in cls._get_managed_objects().items():
                props = interfaces.get("org.bluez.Device1")
                if props and props.get("Address", "").upper() == key:
                    cls._path_cache[key] = path
                    return path
        except Exception as e:
            logger.error(f"Failed to find device path for {mac_address}: {e}")
        return None

    @classmethod
    def is_device_connected(cls, mac_address):
        if not mac_address:
            return False

        path = cls._find_device_path(mac_address)
        if not path:
            return False

        try:
            result = cls._get_bus().call_sync(
                "org.bluez", path,
                "org.freedesktop.DBus.Properties", "Get",
                GLib.Variant("(ss)", ("org.bluez.Device1", "Connected")),
                GLib.VariantType.new("(v)"),
                Gio.DBusCallFlags.NONE, -1, None
            )
            return bool(result.unpack()[0])
        except Exception as e:
            logger.debug(f"is_device_connected({mac_address}): {e}")
            cls._path_cache.pop(mac_address.upper(), None)
            return False
