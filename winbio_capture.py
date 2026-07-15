import ctypes
from ctypes import wintypes

# ======================================================
# Windows Biometric Framework constants
# ======================================================

WINBIO_TYPE_FINGERPRINT = 0x00000008
WINBIO_POOL_SYSTEM = 0x00000001

# Session flags
WINBIO_FLAG_DEFAULT = 0x00000000
WINBIO_FLAG_RAW = 0x00000020

# Purpose
WINBIO_PURPOSE_VERIFY = 0x00000001

# Data Flags
WINBIO_DATA_FLAG_RAW = 0x00000001

HRESULT = ctypes.c_long

winbio = ctypes.WinDLL("winbio.dll")

# ======================================================
# Function prototypes
# ======================================================

winbio.WinBioOpenSession.argtypes = [
    ctypes.c_uint32,                     # Factor
    ctypes.c_uint32,                     # Pool
    ctypes.c_uint32,                     # Flags
    ctypes.POINTER(ctypes.c_uint32),     # Unit array
    ctypes.c_size_t,                     # Unit count
    ctypes.c_void_p,                     # Database ID
    ctypes.POINTER(wintypes.HANDLE)      # Session
]
winbio.WinBioOpenSession.restype = HRESULT


winbio.WinBioCaptureSample.argtypes = [
    wintypes.HANDLE,                     # Session
    ctypes.c_uint32,                     # Purpose
    ctypes.c_uint32,                     # Data Flags
    ctypes.POINTER(ctypes.c_uint32),     # UnitId
    ctypes.POINTER(ctypes.c_void_p),     # Sample
    ctypes.POINTER(ctypes.c_size_t),     # SampleSize
    ctypes.POINTER(ctypes.c_uint32),     # RejectDetail
]
winbio.WinBioCaptureSample.restype = HRESULT


winbio.WinBioFree.argtypes = [ctypes.c_void_p]
winbio.WinBioFree.restype = HRESULT


winbio.WinBioCloseSession.argtypes = [wintypes.HANDLE]
winbio.WinBioCloseSession.restype = HRESULT


# ======================================================
# Open Session
# ======================================================

session = wintypes.HANDLE()

hr = winbio.WinBioOpenSession(
    WINBIO_TYPE_FINGERPRINT,
    WINBIO_POOL_SYSTEM,
    WINBIO_FLAG_RAW,     # Must be RAW for CaptureSample
    None,
    0,
    None,
    ctypes.byref(session)
)

print(f"OpenSession: 0x{hr & 0xffffffff:08X}")

if hr != 0:
    quit()

print("Session Handle:", session.value)

# ======================================================
# Capture
# ======================================================

unit = ctypes.c_uint32()
sample = ctypes.c_void_p()
sample_size = ctypes.c_size_t()
reject = ctypes.c_uint32()

print("Touch the fingerprint sensor...")

hr = winbio.WinBioCaptureSample(
    session,
    WINBIO_PURPOSE_VERIFY,
    WINBIO_DATA_FLAG_RAW,
    ctypes.byref(unit),
    ctypes.byref(sample),
    ctypes.byref(sample_size),
    ctypes.byref(reject)
)

print(f"Capture Result : 0x{hr & 0xffffffff:08X}")
print("Unit ID        :", unit.value)
print("Sample Pointer :", sample.value)
print("Sample Size    :", sample_size.value)
print("Reject Detail  :", reject.value)

if hr == 0 and sample.value:
    print("Fingerprint captured successfully.")
    winbio.WinBioFree(sample)

winbio.WinBioCloseSession(session)