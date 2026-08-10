from sqlmodel import SQLModel, Field


class AuthorConcept(SQLModel, table=True):
    __tablename__ = "author_concepts"

    author_id: str = Field(foreign_key="authors.id", primary_key=True)
    concept_id: str = Field(foreign_key="concepts.id", primary_key=True)
    score: float = Field(default=0.0)
