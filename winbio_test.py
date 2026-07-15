import ctypes
from ctypes import wintypes

winbio = ctypes.WinDLL("winbio.dll")

# Constants
WINBIO_TYPE_FINGERPRINT = 0x00000008
WINBIO_POOL_SYSTEM = 0x00000001
WINBIO_FLAG_DEFAULT = 0x00000000

# Open session
session = wintypes.HANDLE()

winbio.WinBioOpenSession.argtypes = [
    ctypes.c_ulong,
    ctypes.c_ulong,
    ctypes.c_ulong,
    ctypes.c_void_p,
    ctypes.c_ulong,
    ctypes.c_void_p,
    ctypes.POINTER(wintypes.HANDLE)
]

winbio.WinBioOpenSession.restype = ctypes.c_long


result = winbio.WinBioOpenSession(
    WINBIO_TYPE_FINGERPRINT,
    WINBIO_POOL_SYSTEM,
    WINBIO_FLAG_DEFAULT,
    None,
    0,
    None,
    ctypes.byref(session)
)

print("Open session:", result)

if result != 0:
    exit()


class WINBIO_IDENTITY(ctypes.Structure):
    _fields_ = [
        ("Type", ctypes.c_ulong),
        ("Value", ctypes.c_byte * 72)
    ]


identity = WINBIO_IDENTITY()
unit_id = ctypes.c_ulong()
subfactor = ctypes.c_ubyte()


winbio.WinBioIdentify.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(ctypes.c_ulong),
    ctypes.POINTER(WINBIO_IDENTITY),
    ctypes.POINTER(ctypes.c_ubyte)
]

winbio.WinBioIdentify.restype = ctypes.c_long


print("Place your finger on the scanner...")


result = winbio.WinBioIdentify(
    session,
    ctypes.byref(unit_id),
    ctypes.byref(identity),
    ctypes.byref(subfactor)
)


print("Result:", hex(result))

if result == 0:
    print("Fingerprint matched!")
    print("Unit:", unit_id.value)
else:
    print("Failed")