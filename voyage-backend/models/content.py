from pydantic import BaseModel


class Content(BaseModel):
    content_name: str
    content_type: str
    content_description: str
    content_latitude: str
    content_longitude: str
