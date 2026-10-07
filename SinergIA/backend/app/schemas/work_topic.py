from sqlmodel import SQLModel


class WorkTopicBase(SQLModel):
    work_id: str
    topic_id: str
    score: float = 0.0
    is_primary: bool = False


class WorkTopicCreate(WorkTopicBase):
    pass


class WorkTopicRead(WorkTopicBase):
    pass
