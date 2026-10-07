from sqlmodel import SQLModel


class AuthorYearlyMetricBase(SQLModel):
    author_id: str
    year: int
    works_count: int = 0
    cited_by_count: int = 0
    oa_works_count: int = 0


class AuthorYearlyMetricCreate(AuthorYearlyMetricBase):
    pass


class AuthorYearlyMetricRead(AuthorYearlyMetricBase):
    pass
