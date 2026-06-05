from pydantic import BaseModel
from typing import List, Optional
from .intent_schema import IntentSchema
from .db_schema import DBSchema
from .api_schema import APISchema
from .ui_schema import UISchema
from .auth_schema import AuthSchema


class AppSchema(BaseModel):
    intent: IntentSchema
    database: DBSchema
    api: APISchema
    ui: UISchema
    auth: AuthSchema
    generated_code_skeleton: Optional[str] = None


class PipelineResult(BaseModel):
    job_id: str
    status: str                        # success, partial, failed
    app_schema: Optional[AppSchema] = None
    stage_outputs: dict = {}           # raw output per stage
    validation_errors: List[str] = []
    repair_log: List[str] = []
    assumptions: List[str] = []
    metrics: dict = {}
