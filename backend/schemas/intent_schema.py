from pydantic import BaseModel, Field
from typing import List, Optional


class Entity(BaseModel):
    name: str
    attributes: List[str]
    relationships: List[str] = []


class UserRole(BaseModel):
    name: str
    permissions: List[str]


class Feature(BaseModel):
    name: str
    description: str
    requires_auth: bool = False


class IntentSchema(BaseModel):
    app_name: str
    app_type: str
    entities: List[Entity]
    roles: List[UserRole]
    features: List[Feature]
    assumptions: List[str] = []
    clarifications_needed: List[str] = []
