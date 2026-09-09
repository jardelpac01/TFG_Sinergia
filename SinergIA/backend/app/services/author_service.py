from typing import List, Optional

from sqlmodel import Session

from app.models import Author, Work
from app.repositories.author_repository import AuthorRepository
from app.schemas.author import AuthorReadLite, AuthorNetwork, CoAuthorConnection, CoAuthorLocation, CountryConnection


class AuthorService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuthorRepository(db)

    def list_authors(self, q: Optional[str] = None, limit: int = 50) -> List[Author]:
        return self.repository.list_authors(q=q, limit=limit)

    def get_author(self, author_id: str) -> Optional[Author]:
        return self.repository.get_author(author_id)

    def get_authors_by_name(self, name: str) -> List[Author]:
        return self.repository.get_author_by_name(name)

    def get_author_works(self, author_id: str) -> List[Work]:
        return self.repository.get_author_works(author_id)

    def get_author_network(self, author_id: str) -> Optional[AuthorNetwork]:
        author = self.get_author(author_id)
        if not author:
            return None

        coauthors = [
            CoAuthorConnection(
                id=coauthor.id,
                display_name=coauthor.display_name,
                shared_works_count=int(coauthor.shared_works_count),
            )
            for coauthor in self.repository.get_coauthors(author_id)
        ]

        countries = [
            CountryConnection(
                country_code=country.country_code,
                works_count=int(country.works_count),
            )
            for country in self.repository.get_country_collaborations(author_id)
        ]

        return AuthorNetwork(
            author=AuthorReadLite(
                id=author.id,
                display_name=author.display_name,
                orcid=author.orcid,
            ),
            coauthors=coauthors,
            country_collaborations=countries,
        )

    def get_collaborators_with_location(self, author_id: str) -> List[CoAuthorLocation]:
        collaborators = []
        for coauthor, shared_works_count in self.repository.get_coauthors_with_location(author_id):
            institution = coauthor.last_known_institution
            collaborators.append(
                CoAuthorLocation(
                    id=coauthor.id,
                    display_name=coauthor.display_name,
                    orcid=coauthor.orcid,
                    shared_works_count=int(shared_works_count),
                    institution_name=institution.name if institution else None,
                    country_code=institution.country_code if institution else None,
                    city=institution.city if institution else None,
                )
            )
        return collaborators
