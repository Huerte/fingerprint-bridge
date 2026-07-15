import ctypes
import os

dll = os.path.join(os.getcwd(), "libusb-1.0.dll")

print("Loading:")
print(dll)

try:
    lib = ctypes.CDLL(dll)
    print("✅ libusb-1.0.dll loaded successfully")
except Exception as e:
    print("❌ Failed to load DLL")
    print(e)