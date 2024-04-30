from pydantic import BaseModel


class BaseDocument(BaseModel):
    content_url : str 
    content : str