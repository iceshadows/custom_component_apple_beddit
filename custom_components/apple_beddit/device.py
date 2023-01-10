import logging

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

_LOGGER = logging.getLogger(__name__)

CHAR_FORCE_UUID = "f6807d24-b90a-11e5-a837-0800200c9a66"
CHAR_BED_FLAG_UUID = "f6807d22-b90a-11e5-a837-0800200c9a66"
CHAR_TEMPERATURE_UUID = "00002a6e-0000-1000-8000-00805f9b34fb"
CHAR_HUMIDITY_UUID = "00002a6f-0000-1000-8000-00805f9b34fb"


def get_data(data: bytearray, T: type):
    if T == float:
        data = int.from_bytes(data, "little") / 100
    elif T == int:
        data = int.from_bytes(data, "little")
    return data


class AppleBedditMointor:
    def __init__(self, address: str, name: str, bleakclient: BleakClient) -> None:
        self.address = address
        self.inited = False
        self.name = name
        self.ble_client: BleakClient = bleakclient
        _LOGGER.error("device created")
        self.force = None
        self.inbed_flag = None
        self.available = False
        self.temperature = None
        self.humidity = None
        self.sensor_instances = []

    def get_name(self):
        return self.name

    def disconect(self, client: BleakClient):
        _LOGGER.error("device disconnected")
        self.force = None
        self.inbed_flag = None
        self.temperature = None
        self.humidity = None
        self.available = False

    async def read_data(self, character: BleakGATTCharacteristic, data: bytearray):
        flag = None
        UUID = character.uuid
        T = float
        if UUID == CHAR_BED_FLAG_UUID:
            T = int
        data = get_data(data=data, T=T)
        if UUID == CHAR_FORCE_UUID:
            flag = "force"
            self.force = data
        if UUID == CHAR_HUMIDITY_UUID:
            flag = "humidity"
            self.humidity = data
        if UUID == CHAR_TEMPERATURE_UUID:
            flag = "temperature"
            self.temperature = data
        if UUID == CHAR_BED_FLAG_UUID:
            flag = "in bed"
            self.inbed_flag = data
        self.inited = True
        self.available = True
        # _LOGGER.error("%s get Data: %s", flag, data)

    async def get_sensors(self):
        client = self.ble_client
        try:
            _LOGGER.error("Device connecting..")
            await client.connect()
            _LOGGER.error("device connected")
            force_data = get_data(await client.read_gatt_char(CHAR_FORCE_UUID), float)
            self.force = force_data
            temperature_data = get_data(
                await client.read_gatt_char(CHAR_TEMPERATURE_UUID), float
            )
            self.temperature = temperature_data
            inbed_flag_data = get_data(
                await client.read_gatt_char(CHAR_BED_FLAG_UUID), int
            )
            self.inbed_flag = inbed_flag_data
            humdity_data = get_data(
                await client.read_gatt_char(CHAR_HUMIDITY_UUID), float
            )
            self.humidity = humdity_data
            self.available = True
            _LOGGER.error("data received")
        except Exception as exception:
            _LOGGER.error(exception)
            self.available = False
        finally:
            client.disconnect()

    @property
    def sensors_data(self):
        return {
            "bed_temperature": {
                "name": "Bed Temperature",
                "id": "bed_temperature",
                "state": self.temperature,
            },
            "bed_humidity": {
                "name": "Bed Humidity",
                "id": "bed_humidity",
                "state": self.humidity,
            },
            "bed_inbedstate": {
                "name": "InBed State",
                "id": "bed_inbedstate",
                "state": self.inbed_flag,
            },
            "bed_force": {
                "name": "Bed Force",
                "id": "bed_force",
                "state": self.force,
            },
        }

    async def connect(self):
        _LOGGER.error("Connecting.. %s", self.name)
        client = self.ble_client
        client.set_disconnected_callback(self.disconect)
        self.inited = True
        connectable = await client.connect()
        if connectable:
            force_data = get_data(await client.read_gatt_char(CHAR_FORCE_UUID), float)
            self.force = force_data
            temperature_data = get_data(
                await client.read_gatt_char(CHAR_TEMPERATURE_UUID), float
            )
            self.temperature = temperature_data
            inbed_flag_data = get_data(
                await client.read_gatt_char(CHAR_BED_FLAG_UUID), int
            )
            self.inbed_flag = inbed_flag_data
            humdity_data = get_data(
                await client.read_gatt_char(CHAR_HUMIDITY_UUID), float
            )
            self.humidity = humdity_data

            await client.start_notify(CHAR_FORCE_UUID, self.read_data)
            await client.start_notify(CHAR_BED_FLAG_UUID, self.read_data)
            await client.start_notify(CHAR_HUMIDITY_UUID, self.read_data)
            await client.start_notify(CHAR_TEMPERATURE_UUID, self.read_data)

            self.available = True
            _LOGGER.error("Connected %s", self.name)
        else:
            raise RuntimeError("Can not connect device")
