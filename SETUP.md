# FingerprintBridge: Setup & Run Guide

> Complete walkthrough from zero to a working fingerprint scan in the browser.

---

## Architecture Overview

```
Vue 3 (Vite)   →  POST /capture  →  FastAPI (Python)  →  PyUSB  →  CS9711 Scanner
     ↑                                      │
     └──────── GET /images/latest.png ──────┘
```

**Port map:**
| Service | URL |
|---------|-----|
| FastAPI backend | `http://localhost:8000` |
| Vue frontend | `http://localhost:5173` |

---

## Prerequisites

Before touching any code, confirm you have the following installed.

| Tool | Min Version | Check Command |
|------|-------------|---------------|
| Python | 3.10+ | `python --version` |
| Node.js | 22.18+ or 24.12+ | `node --version` |
| npm | bundled with Node | `npm --version` |

> [!IMPORTANT]
> The `frontend/package.json` enforces `"node": "^22.18.0 || >=24.12.0"`. Install the correct Node version before running `npm install`.

---

## Step 1: Replace the USB Driver with libusbK

This is the most critical step. Windows assigns the ChipSailing proprietary driver to the scanner by default, which blocks PyUSB from claiming the device.

### 1.1 Plug in the CS9711 scanner

Connect it to a USB port and leave it plugged in.

### 1.2 Run Zadig

The installer is already in the repo:

```
FingerprintBridge/drivers/zadig-2.9.exe
```

Double-click it. Run it **as Administrator** if prompted.

### 1.3 Install the libusbK driver

1. In Zadig, go to **Options → List All Devices**.
2. Find **ChipSailing CS9711** (or a device with VID `2541`, PID `0236`) in the dropdown.
3. In the driver selector box on the right, pick **libusbK**.

   > [!WARNING]
   > Do not select WinUSB. PyUSB works with libusbK specifically for this device.

4. Click **Replace Driver** (or **Install Driver**).
5. Wait for Zadig to confirm success.

### 1.4 Verify the driver

Open a normal (non-admin) PowerShell and run:

```powershell
pnputil /enum-devices /class "USB"
```

Look for an entry whose **Provider** column shows `libusbK` instead of `ChipSailing`. That confirms the swap worked.

---

## Step 2: Set Up the Python Virtual Environment

> [!IMPORTANT]
> All backend commands must be run from an **Administrator PowerShell**. Non-elevated shells will produce `Access denied` when PyUSB tries to claim the USB interface.

### 2.1 Open Administrator PowerShell

Right-click the Start menu → **Windows PowerShell (Admin)** or **Terminal (Admin)**.

### 2.2 Navigate to the project root

```powershell
cd path\to\FingerprintBridge
```

### 2.3 Create the virtual environment

```powershell
python -m venv venv
```

### 2.4 Activate the virtual environment

```powershell
venv\Scripts\Activate.ps1
```

Your prompt should now show `(venv)` at the start.

> [!NOTE]
> If PowerShell blocks the script with an execution policy error, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> This only affects the current session.

### 2.5 Install Python dependencies

```powershell
pip install fastapi uvicorn pyusb pillow starlette
```

---

## Step 3: Confirm libusb-1.0.dll Is in Place

The capture module expects the DLL at this exact path:

```
FingerprintBridge/backend/libusb-1.0.dll
```

Check the backend folder:

```powershell
ls backend\
```

You should see `libusb-1.0.dll` listed. It is already there per the project structure.

`cs9711_capture.py` resolves the DLL relative to its own file location, so placing it inside `backend/` is required.

---

## Step 4: Start the FastAPI Backend

Still in the **Administrator PowerShell** with `(venv)` active:

```powershell
cd backend
uvicorn main:app --reload
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

> [!CAUTION]
> You must `cd backend` first. If you run `uvicorn` from the project root, Python will fail to import `cs9711_capture` and `main` because it will not find the module.

### Verify the backend is alive

Open a browser or run:

```powershell
curl http://localhost:8000/
```

Expected response:

```json
{"status": "CS9711 server running"}
```

---

## Step 5: Set Up and Start the Vue Frontend

Open a **second terminal** (normal, non-admin is fine for Node).

### 5.1 Navigate to the frontend directory

```powershell
cd path\to\FingerprintBridge\frontend
```

### 5.2 Install Node dependencies

```powershell
npm install
```

> [!NOTE]
> `node_modules/` already exists in the directory, so this may be fast. If you see version mismatch warnings, re-run with the correct Node version.

### 5.3 Start the dev server

```powershell
npm run dev
```

Expected output:

```
  VITE v8.x.x  ready in Xms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Step 6: Run a Scan

1. Open `http://localhost:5173` in your browser.
2. Place your finger on the CS9711 scanner.
3. Click **Scan Fingerprint**.
4. The button will show **Scanning...** while the capture runs.
5. On success, the fingerprint image appears below the button.

The backend will process the USB command sequence and capture the image.

The saved image lands at:

```
backend/fingerprints/latest.png
```

---

## Quick Reference: Full Startup Sequence

```
Terminal 1 (Administrator PowerShell)
──────────────────────────────────────
cd path\to\FingerprintBridge
venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --reload


Terminal 2 (Normal PowerShell)
──────────────────────────────────────
cd path\to\FingerprintBridge\frontend
npm run dev


Browser
──────────────────────────────────────
http://localhost:5173
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `usb.core.NoBackendError: No backend available` | `libusb-1.0.dll` missing from `backend/` | Copy the DLL into `backend/` |
| `Access denied` on `claim_interface` | PowerShell not elevated, or ChipSailing driver still active | Run as Administrator; re-run Zadig to install libusbK |
| `No module named usb` | `pyusb` not installed in the active venv | `pip install pyusb` |
| `Could not import module main` | `uvicorn` started from the wrong directory | `cd backend` first, then run uvicorn |
| `libusb backend not found` (Python RuntimeError) | `libusb-1.0.dll` not in the same folder as `cs9711_capture.py` | Place the DLL in `backend/` |
| `CS9711 not found` | Scanner not plugged in, or driver not swapped to libusbK | Plug in scanner; re-run Zadig |
| `Invalid frame size: X` (not 8024) | Scan timed out or partial read | Remove and re-insert scanner; try again |
| `ERR_CONNECTION_REFUSED` in browser | Backend not running, or wrong port | Confirm uvicorn is running on port 8000 |
| Vue image not refreshing | Browser cache | Cache-busting timestamp already handled in `App.vue` via `?t=Date.now()` |
| `vite: command not found` | `node_modules` not installed | Run `npm install` inside `frontend/` |
| Execution policy error on `Activate.ps1` | PowerShell script execution blocked | Run `Set-ExecutionPolicy -Scope Process Bypass` first |

---

## Project File Map

```
FingerprintBridge/
├── backend/
│   ├── main.py               ← FastAPI app, /capture endpoint, static /images
│   ├── cs9711_capture.py     ← USB logic: INIT / SCAN / RESET + image reconstruction
│   ├── libusb-1.0.dll        ← Must be here for PyUSB to find it
│   └── fingerprints/
│       └── latest.png        ← Overwritten on every scan
│
├── ChipSailing_Backup/       ← Original Windows drivers backup
│
├── frontend/
│   ├── src/
│   │   ├── App.vue           ← Scan button, fetch logic, image display
│   │   └── main.js           ← Vue entry point
│   ├── package.json
│   └── vite.config.js
│
├── drivers/
│   └── zadig-2.9.exe         ← USB driver replacement tool
│
├── venv/                     ← Python virtual environment
├── SETUP.md                  ← Setup & Run Guide
└── CONTEXT.md                ← Full protocol and architecture notes
```
