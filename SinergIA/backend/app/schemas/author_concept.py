from sqlmodel import SQLModel


class AuthorConceptBase(SQLModel):
    author_id: str
    concept_id: str
    score: float = 0.0


class AuthorConceptCreate(AuthorConceptBase):
    pass


class AuthorConceptRead(AuthorConceptBase):
    pass
