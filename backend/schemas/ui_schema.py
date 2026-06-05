from pydantic import BaseModel, Field
from typing import List, Optional


class UIComponent(BaseModel):
    type: str        # form, table, card, button, input, chart, navbar
    name: str
    props: List[str] = []
    api_endpoint: Optional[str] = None  # maps to API path


class UIPage(BaseModel):
    name: str
    route: str
    auth_required: bool = False
    roles_allowed: List[str] = []
    components: List[UIComponent]


class UISchema(BaseModel):
    app_name: str
    theme: str = "light"
    pages: List[UIPage]
