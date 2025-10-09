from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class ImageMetadata(BaseModel):
    id: int
    filename: str
    timestamp: datetime
    cameraId: Optional[int]= None
    file_type: Optional[str]=None
    classification: Optional[str]= None
    classified: bool = False
    confidence: Optional[float]= None

class Command(BaseModel):
    action: str
    params: Optional[Dict] = None
