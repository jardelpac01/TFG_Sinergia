from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class InstitutionBase(SQLModel):
    id: str
    name: str
    country_code: Optional[str] = None
    ror: Optional[str] = None
    type: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    city: Optional[str] = None

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionRead(InstitutionBase):
    updated_at: datetime