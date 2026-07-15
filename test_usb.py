import usb.core
import usb.backend.libusb1
import os

print("Loading libusb...")

dll_path = os.path.join(
    os.getcwd(),
    "libusb-1.0.dll"
)

backend = usb.backend.libusb1.get_backend(
    find_library=lambda x: dll_path
)

if backend is None:
    print("❌ Could not create libusb backend")
    exit()

print("✅ libusb backend loaded")

print("\nSearching for CS9711...")

VID = 0x2541
PID = 0x0236

dev = usb.core.find(
    idVendor=VID,
    idProduct=PID,
    backend=backend
)

if dev is None:
    print("❌ CS9711 not found")
    print("")
    print("Possible reasons:")
    print("1. Windows driver is currently owning the scanner")
    print("2. Wrong VID/PID")
    print("3. Device is disconnected")

else:
    print("✅ CS9711 FOUND!")
    print(dev)

    print("\nDevice details:")
    print("VID:", hex(dev.idVendor))
    print("PID:", hex(dev.idProduct))