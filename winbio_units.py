import ctypes
from ctypes import wintypes

winbio = ctypes.WinDLL("winbio.dll")

WINBIO_TYPE_FINGERPRINT = 0x00000008

class WINBIO_UNIT_SCHEMA(ctypes.Structure):
    _fields_ = [
        ("UnitId", ctypes.c_ulong),
        ("PoolType", ctypes.c_ulong),
        ("BiometricFactor", ctypes.c_ulong),
        ("SensorSubType", ctypes.c_ulong),
        ("SensorCapabilities", ctypes.c_ulong),
        ("Description", ctypes.c_wchar * 256),
        ("Manufacturer", ctypes.c_wchar * 256),
        ("Model", ctypes.c_wchar * 256),
        ("SerialNumber", ctypes.c_wchar * 256),
        ("FirmwareVersion", ctypes.c_ulong)
    ]


count = ctypes.c_ulong()
schema = ctypes.POINTER(WINBIO_UNIT_SCHEMA)()

winbio.WinBioEnumBiometricUnits.restype = ctypes.c_long

result = winbio.WinBioEnumBiometricUnits(
    WINBIO_TYPE_FINGERPRINT,
    ctypes.byref(schema),
    ctypes.byref(count)
)

print("Result:", hex(result))
print("Count:", count.value)

if result == 0:
    for i in range(count.value):
        print("Sensor:", schema[i].Description)
        print("Manufacturer:", schema[i].Manufacturer)
        print("Model:", schema[i].Model)