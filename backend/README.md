# CS9711 Capture Script — Documentation

## Overview
`cs9711_capture.py` communicates with a **CS9711 USB fingerprint sensor** via
`pyusb` + `libusb1`, triggers a scan, reads the raw image bytes, converts them
into a usable grayscale image, and saves the result to disk.

**Dependencies:** `pyusb`, `Pillow (PIL)`, `libusb-1.0.dll` (must sit next to
this script).

---

## Device Constants

| Constant | Value | Meaning |
|---|---|---|
| `VID` | `0x2541` | USB Vendor ID of the sensor |
| `PID` | `0x0236` | USB Product ID of the sensor |
| `EP_OUT` | `0x01` | Endpoint used to send commands to the device |
| `EP_IN` | `0x81` | Endpoint used to read data from the device |
| `CMD_INIT` | `0x01` | Command byte: initialize sensor |
| `CMD_RESET` | `0x02` | Command byte: reset sensor |
| `CMD_SCAN` | `0x04` | Command byte: trigger a fingerprint scan |
| `SENSOR_WIDTH` / `SENSOR_HEIGHT` | `34` / `236` | Default (fallback) raw sensor dimensions |

---

## Functions

### `find_device()`
**Purpose:** Locates the CS9711 device on the USB bus.

**Parameters:** None

**Returns:** `usb.core.Device` — the matched device object.

**Raises:** `RuntimeError` if no device matching `VID`/`PID` is found.

**Notes:** Uses the custom `libusb1` backend loaded from `libusb-1.0.dll` in
the script's directory.

---

### `send_command(dev, command)`
**Purpose:** Sends a single command packet to the device over `EP_OUT`.

**Parameters:**
- `dev` (`usb.core.Device`) — target device.
- `command` (`int`) — one of `CMD_INIT`, `CMD_RESET`, `CMD_SCAN`.

**Returns:** None

**Packet format** (8 bytes total):
```
[0xEA, command, 0x00, 0x00, 0x00, 0x00, command, 0xEA]
```
Starts and ends with the sync byte `0xEA`; the command byte is repeated at
position 1 and 6 as a simple integrity check.

**Timeout:** 3000 ms.

---

### `read_image(dev)`
**Purpose:** Reads the raw image frame back from the device over `EP_IN`.

**Parameters:**
- `dev` (`usb.core.Device`) — target device.

**Returns:** `bytes` — raw frame data.

**Behavior:**
1. **Primary path:** attempts a single read of up to 16384 bytes (10s timeout),
   large enough to capture the whole frame in one call.
2. **Fallback path:** if the single read fails (exception raised), tries two
   sequential reads — 8000 bytes then 3000 bytes — and concatenates them.
3. If both paths fail, re-raises the original exception.

**Why two paths exist:** Some USB stacks/drivers don't reliably return large
transfers in one call, so the fallback splits the read into the two chunk
sizes the older device firmware is known to send.

---

### `convert_image(raw)`
**Purpose:** Converts the raw byte stream from the sensor into a `PIL.Image`.

**Parameters:**
- `raw` (`bytes`) — raw frame data from `read_image()`.

**Returns:** `PIL.Image.Image` — grayscale (`"L"` mode) image, resized to the
final output dimensions.

**Format detection (based on `len(raw)`):**

| Raw length | Sensor W×H | Output W×H (pre-resize) | Final resize |
|---|---|---|---|
| `10976` | 49×224 | 98×112 | 196×224 |
| `9216` | 48×192 | 96×96 | 192×192 |
| *any other* (fallback, expected `8024`) | 34×236 | 68×118 | 136×236 |

**Pixel remapping logic:**
- Raw bytes are laid out row-major at `sensor_width × sensor_height`.
- Each raw pixel `(x, y)` is remapped to output coordinates:
  - `dy = y // 2` (two source rows collapse into one output row)
  - `dx = x * 2 + (y % 2)` (columns are interleaved based on odd/even row)
- This "de-interleaving" reconstructs a full-resolution image from a sensor
  that outputs data in an interlaced/zig-zag pattern.
- Out-of-bounds indices (`index >= raw_len` or `dx/dy` outside the output
  image) are silently skipped.
- The de-interleaved image is then upscaled via `Image.resize()` to the
  final `resize_dim`.

---

### `capture(output_file)`
**Purpose:** Main entry point — runs the full capture sequence end-to-end and
saves a fingerprint image.

**Parameters:**
- `output_file` (`str`) — path to save the resulting image (e.g. `"fingerprint.png"`).

**Returns:** `dict`
```python
{
    "success": True,
    "file": output_file,
    "size": <int, raw byte length received>
}
```

**Raises:** `RuntimeError` if the received frame size isn't one of the three
known valid sizes (`8024`, `9216`, `10976`).

**Sequence of operations:**
1. `find_device()` — locate the sensor.
2. Get active configuration and claim interface `0`.
3. Send `CMD_INIT`, wait `0.5s`, then attempt a throwaway 8-byte read
   (ignored if it fails — clears any stale ack packet).
4. Send `CMD_SCAN` to trigger the actual fingerprint capture.
5. `read_image()` — read the raw frame.
6. Validate frame length.
7. `convert_image()` — decode raw bytes into a `PIL.Image`.
8. Save image to `output_file`.
9. **Always** (via `finally`): send `CMD_RESET`, then release the USB
   interface and dispose of resources — even if an error occurred above.

**Cleanup guarantee:** The `finally` block ensures the device is reset and
released regardless of whether the capture succeeded, preventing the sensor
from being left in a locked/busy state for the next run.

---

## Script Entry Point (`__main__`)
When run directly, the script calls:
```python
capture("fingerprint.png")
```
and prints the resulting status dictionary. Useful for quick manual testing
of the sensor without integrating into a larger application.

---

## Quick Usage Example
```python
from cs9711_capture import capture

result = capture("scan_001.png")
if result["success"]:
    print(f"Saved {result['size']} bytes to {result['file']}")
```

## Known Frame Sizes Reference
| Bytes | Resolution (raw) | Likely device variant |
|---|---|---|
| 8024 | 34×236 | Default/fallback |
| 9216 | 48×192 | Variant A |
| 10976 | 49×224 | Variant B |

Any other size aborts the capture with a `RuntimeError`, since it likely
indicates a corrupted or partial USB transfer.