import json

from fastapi import FastAPI

app = FastAPI()


@app.get("/ridepath.json")
def read_root():
    with open("artifacts/data.json", "r") as f:
        data = json.load(f)
    return data
