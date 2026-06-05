from pydantic import BaseModel, Field
from typing import List, Dict


class RolePermissions(BaseModel):
    role: str
    permissions: List[str]  # e.g. ["read:contacts", "write:contacts"]


class AuthSchema(BaseModel):
    auth_type: str = "jwt"
    roles: List[str]
    role_permissions: List[RolePermissions]
    protected_routes: List[str] = []
