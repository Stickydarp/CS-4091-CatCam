from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from . import commands

app = FastAPI(title="CatCam Backend API (minimal)")


class InsertMetadataPayload(BaseModel):
    filename: str
    cameraId: Optional[int] = None
    file_type: Optional[str] = None
    classification: Optional[str] = None
    classified: Optional[bool] = False
    confidence: Optional[float] = None


class ClassifyImagePayload(BaseModel):
    image_id: int


@app.post("/init_db")
def init_db() -> Dict[str, Any]:
    res = commands.execute_command("init_db")
    return res


@app.post("/insert_metadata")
def insert_metadata(payload: InsertMetadataPayload) -> Dict[str, Any]:
    params = payload.dict()
    res = commands.execute_command("insert_metadata", params)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


@app.post("/classify_all")
def classify_all() -> Dict[str, Any]:
    return commands.execute_command("classify_all")


@app.post("/classify_image")
def classify_image(payload: ClassifyImagePayload) -> Dict[str, Any]:
    res = commands.execute_command("classify_image", {"image_id": payload.image_id})
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@app.get("/images")
def get_images(classified: Optional[bool] = None, cameraId: Optional[int] = None, limit: Optional[int] = None):
    params = {}
    if classified is not None:
        params["classified"] = classified
    if cameraId is not None:
        params["cameraId"] = cameraId
    if limit is not None:
        params["limit"] = limit
    res = commands.execute_command("get_images", params)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res


@app.get("/images/{image_id}")
def get_image(image_id: int):
    res = commands.execute_command("get_image", {"image_id": int(image_id)})
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@app.delete("/images/{image_id}")
def delete_image(image_id: int):
    res = commands.execute_command("delete_image", {"image_id": int(image_id)})
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res
