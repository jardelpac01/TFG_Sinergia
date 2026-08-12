from sqlmodel import SQLModel


class AuthorTopicBase(SQLModel):
    author_id: str
    topic_id: str
    score: float = 0.0


class AuthorTopicCreate(AuthorTopicBase):
    pass


class AuthorTopicRead(AuthorTopicBase):
    pass
