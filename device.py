import usb.core
import usb.util

VID = 0x2541
PID = 0x0236

dev = usb.core.find(idVendor=VID, idProduct=PID)

if dev is None:
    print("Device not found")
else:
    print("Found!")
    print(dev)

    print("\nConfigurations:")

    for cfg in dev:
        print(f"\nConfiguration {cfg.bConfigurationValue}")

        for intf in cfg:
            print(
                f" Interface {intf.bInterfaceNumber}"
                f" Class={hex(intf.bInterfaceClass)}"
                f" SubClass={hex(intf.bInterfaceSubClass)}"
                f" Protocol={hex(intf.bInterfaceProtocol)}"
            )

            for ep in intf:
                direction = "IN" if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else "OUT"

                print(
                    f"    Endpoint {hex(ep.bEndpointAddress)} "
                    f"{direction} "
                    f"Type={usb.util.endpoint_type(ep.bmAttributes)}"
                )