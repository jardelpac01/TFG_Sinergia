from sqlmodel import SQLModel


class WorkReferenceBase(SQLModel):
    work_id: str
    referenced_work_id: str


class WorkReferenceCreate(WorkReferenceBase):
    pass


class WorkReferenceRead(WorkReferenceBase):
    pass
