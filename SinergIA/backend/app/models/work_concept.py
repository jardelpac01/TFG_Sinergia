from sqlmodel import SQLModel, Field


class WorkConcept(SQLModel, table=True):
    __tablename__ = "work_concepts"

    work_id: str = Field(foreign_key="works.id", primary_key=True)
    concept_id: str = Field(foreign_key="concepts.id", primary_key=True)
    score: float = Field(default=0.0)
