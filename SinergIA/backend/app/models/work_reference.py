from sqlmodel import SQLModel, Field


class WorkReference(SQLModel, table=True):
    __tablename__ = "work_references"

    work_id: str = Field(foreign_key="works.id", primary_key=True)
    referenced_work_id: str = Field(foreign_key="works.id", primary_key=True)
