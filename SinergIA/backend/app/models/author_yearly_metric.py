from sqlmodel import SQLModel, Field


class AuthorYearlyMetric(SQLModel, table=True):
    __tablename__ = "author_yearly_metrics"

    author_id: str = Field(foreign_key="authors.id", primary_key=True)
    year: int = Field(primary_key=True)
    works_count: int = Field(default=0)
    cited_by_count: int = Field(default=0)
    oa_works_count: int = Field(default=0)
