from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from fastapi import FastAPI, HTTPException
import cs9711_capture
import threading
import base64
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINGERPRINTS_DIR = os.path.join(BASE_DIR, "fingerprints")
capture_lock = threading.Lock()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs(
    FINGERPRINTS_DIR,
    exist_ok=True
)


app.mount(
    "/images",
    StaticFiles(directory=FINGERPRINTS_DIR),
    name="images"
)


@app.get("/")
def home():
    return {
        "status": "CS9711 server running"
    }


@app.get("/scans")
def list_scans():
    files = os.listdir(FINGERPRINTS_DIR)
    scans = [larawan for larawan in files if larawan.endswith(".png")]
    scans.sort(reverse=True)
    
    items = []
    for filename in scans:
        try:
            timestamp_str = filename.replace("scan_", "").replace(".png", "")
            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            iso_timestamp = dt.astimezone().isoformat()
        except ValueError:
            filepath = os.path.join(FINGERPRINTS_DIR, filename)
            mtime = os.path.getmtime(filepath)
            iso_timestamp = datetime.fromtimestamp(mtime).astimezone().isoformat()
            
        items.append({
            "filename": filename,
            "url": f"/images/{filename}",
            "timestamp": iso_timestamp
        })

    return {
        "count": len(scans),
        "items": items
    }


@app.post("/capture")
def capture():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    iso_timestamp = datetime.now().astimezone().isoformat()

    if not capture_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409, 
            detail={"message": "Scanner is busy", "timestamp": iso_timestamp}
        )

    try:
        image_name = f"scan_{timestamp}.png"
        filename = os.path.join(FINGERPRINTS_DIR, image_name)

        try:
            result = cs9711_capture.capture(filename)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail={"message": str(e), "timestamp": iso_timestamp}
            )

        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        return {
            "success": True,
            "image": f"/images/{image_name}",
            "image_base64": encoded_string,
            "timestamp": iso_timestamp 
        }
    finally:
        capture_lock.release()
