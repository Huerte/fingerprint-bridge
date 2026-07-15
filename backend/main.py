from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
import cs9711_capture
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


@app.post("/capture")
def capture():

    filename = (
        "fingerprints/latest.png"
    )


    result = cs9711_capture.capture(
        filename
    )


    return {
        "success": True,
        "image": "/images/latest.png"
    }