# FingerprintBridge

## Prerequisites
- Python 3.10+
- Node.js (22.18+ or >=24.12.0)
- Administrator privileges

## 1. Driver Setup (First Time Only)
Windows blocks PyUSB by default. You must swap the driver to libusbK.
1. Plug in the CS9711 scanner.
2. Run `drivers/zadig-2.9.exe` as Administrator.
3. Click **Options → List All Devices**.
4. Select **ChipSailing CS9711** (VID `2541`, PID `0236`).
5. Choose **libusbK** (NOT WinUSB).
6. Click **Replace Driver**.

## 2. Installation & Run
Open an **Administrator PowerShell** in the project root:

```powershell
npm install
npm run setup
npm start
```
*(This starts both the FastAPI backend on port 8000 and Vue frontend on port 5173)*

## 3. Usage
1. Open `http://localhost:5173`
2. Place finger on scanner.
3. Click **Scan Fingerprint**.

## Troubleshooting
- **`Access denied`**: You didn't run PowerShell as Administrator.
- **`usb.core.NoBackendError`**: `libusb-1.0.dll` is missing from the `backend/` folder.
- **`CS9711 not found`**: Scanner isn't plugged in, or you didn't swap the driver to libusbK.

## STILL NOT WORKING ASK CHATGPT LOL!!!