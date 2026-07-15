import usb.core
import usb.util
import usb.backend.libusb1

import time
import os

from PIL import Image


# ==========================
# DEVICE SETTINGS
# ==========================

VID = 0x2541
PID = 0x0236

EP_OUT = 0x01
EP_IN = 0x81

CMD_INIT = 0x01
CMD_RESET = 0x02
CMD_SCAN = 0x04

IMAGE_PART_1 = 8000
IMAGE_PART_2 = 24

SENSOR_WIDTH = 34
SENSOR_HEIGHT = 236


# ==========================
# LIBUSB BACKEND
# ==========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LIBUSB_DLL = os.path.join(
    BASE_DIR,
    "libusb-1.0.dll"
)


backend = usb.backend.libusb1.get_backend(
    find_library=lambda x: LIBUSB_DLL
)


if backend is None:
    raise RuntimeError(
        "libusb backend not found"
    )


# ==========================
# FIND DEVICE
# ==========================

def find_device():

    dev = usb.core.find(
        idVendor=VID,
        idProduct=PID,
        backend=backend
    )

    if dev is None:
        raise RuntimeError(
            "CS9711 not found"
        )

    return dev



# ==========================
# SEND COMMAND
# ==========================

def send_command(dev, command):

    packet = [
        0xEA,
        command,
        0x00,
        0x00,
        0x00,
        0x00,
        command,
        0xEA
    ]


    dev.write(
        EP_OUT,
        packet,
        timeout=3000
    )



# ==========================
# READ IMAGE
# ==========================

def read_image(dev):
    try:
        # Request a larger buffer to capture the entire frame sent by the device
        return bytes(dev.read(EP_IN, 16384, timeout=10000))
    except Exception as e:
        # Fallback double-read method if single read fails
        try:
            block1 = dev.read(EP_IN, 8000, timeout=10000)
            block2 = dev.read(EP_IN, 3000, timeout=10000)
            return bytes(block1 + block2)
        except:
            raise e



# ==========================
# CONVERT RAW DATA
# ==========================

def convert_image(raw):
    raw_len = len(raw)
    
    if raw_len == 10976:
        sensor_width = 49
        sensor_height = 224
        width = 98
        height = 112
        resize_dim = (196, 224)
    elif raw_len == 9216:
        sensor_width = 48
        sensor_height = 192
        width = 96
        height = 96
        resize_dim = (192, 192)
    else:
        # Default to 8024 bytes fallback (68x118)
        sensor_width = 34
        sensor_height = 236
        width = 68
        height = 118
        resize_dim = (136, 236)

    img = Image.new("L", (width, height))
    pixels = img.load()

    for y in range(sensor_height):
        for x in range(sensor_width):
            index = y * sensor_width + x
            if index >= raw_len:
                continue

            dy = y // 2
            dx = x * 2 + (y % 2)

            if dx < width and dy < height:
                pixels[dx, dy] = raw[index]

    img = img.resize(resize_dim)
    return img



# ==========================
# MAIN CAPTURE FUNCTION
# ==========================

def capture(output_file):

    dev = find_device()


    try:

        # Device is already configured by libusbK

        cfg = dev.get_active_configuration()

        interface = cfg[(0,0)]


        usb.util.claim_interface(
            dev,
            interface.bInterfaceNumber
        )


        # INIT

        send_command(
            dev,
            CMD_INIT
        )


        time.sleep(
            0.5
        )


        try:

            dev.read(
                EP_IN,
                8,
                timeout=3000
            )

        except:

            pass



        # SCAN

        send_command(
            dev,
            CMD_SCAN
        )


        raw = read_image(
            dev
        )


        if len(raw) not in (8024, 10976, 9216):

            raise RuntimeError(
                f"Invalid frame size: {len(raw)}. Expected 8024, 9216, or 10976 bytes."
            )



        image = convert_image(
            raw
        )


        image.save(
            output_file
        )


        return {
            "success": True,
            "file": output_file,
            "size": len(raw)
        }



    finally:

        try:

            send_command(
                dev,
                CMD_RESET
            )

        except:

            pass


        try:

            usb.util.release_interface(
                dev,
                0
            )


            usb.util.dispose_resources(
                dev
            )

        except:

            pass



# ==========================
# TEST MODE
# ==========================

if __name__ == "__main__":


    result = capture(
        "fingerprint.png"
    )


    print(result)