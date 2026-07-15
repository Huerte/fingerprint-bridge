from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from fastapi import FastAPI
import cs9711_capture
import base64
import os


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs(
    "fingerprints",
    exist_ok=True
)


app.mount(
    "/images",
    StaticFiles(directory="fingerprints"),
    name="images"
)


@app.get("/")
def home():
    return {
        "status": "CS9711 server running"
    }


@app.get("/scans")
def list_scans():
    files = os.listdir("fingerprints")
    scans = [larawan for larawan in files if larawan.endswith(".png")]
    scans.sort(reverse=True)
    
    return {
        "count": len(scans),
        "items": [
            {
                "filename": filename,
                "url": f"/images/{filename}"
            }
            for filename in scans
        ]
    }


@app.post("/capture")
def capture():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = f"scan_{timestamp}.png"
    filename = f"fingerprints/{image_name}"

    result = cs9711_capture.capture(filename)

    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    return {
        "success": True,
        "image": f"/images/{image_name}",
        "image_base64": encoded_string
    }