from pydantic import BaseModel, Field
from typing import List, Optional


class Column(BaseModel):
    name: str
    type: str  # string, integer, boolean, datetime, text, float
    nullable: bool = True
    unique: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None  # "table.column"


class Table(BaseModel):
    name: str
    columns: List[Column]


class DBSchema(BaseModel):
    tables: List[Table]
