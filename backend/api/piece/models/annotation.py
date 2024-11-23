

from pydantic import BaseModel, Field

class AnnotationData(BaseModel):
    image_id: int = Field(..., description="ID of the image to annotate")
    type: str = Field(..., description="Type of the annotation (e.g., 'object', 'label')")
    x: float = Field(..., description="X coordinate of the annotation bounding box")
    y: float = Field(..., description="Y coordinate of the annotation bounding box")
    width: float = Field(..., description="Width of the annotation bounding box")
    height: float = Field(..., description="Height of the annotation bounding box")
