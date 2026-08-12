from sqlmodel import SQLModel


class WorkConceptBase(SQLModel):
    work_id: str
    concept_id: str
    score: float = 0.0


class WorkConceptCreate(WorkConceptBase):
    pass


class WorkConceptRead(WorkConceptBase):
    pass
