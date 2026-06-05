from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class RequestBody(BaseModel):
    fields: List[str]
    required: List[str]


class ResponseSchema(BaseModel):
    status_code: int
    fields: List[str]


class Endpoint(BaseModel):
    method: str        # GET, POST, PUT, DELETE
    path: str
    description: str
    auth_required: bool = False
    roles_allowed: List[str] = []
    request_body: Optional[RequestBody] = None
    response: ResponseSchema


class APISchema(BaseModel):
    base_path: str = "/api/v1"
    endpoints: List[Endpoint]
