from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.schemas.author import AuthorCollaboratorsResponse, AuthorListResponse, AuthorNetwork, AuthorReadLite
from app.schemas.research_group import ResearchGroupRead
from app.schemas.work import WorkReadWithRelationships
from app.services.author_service import AuthorService


router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=AuthorListResponse)
def list_authors(
    q: Optional[str] = Query(default=None, description="Search authors by name or ORCID"),
    research_group_id: Optional[int] = Query(
        default=None, description="Filter authors by research group"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=9, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = AuthorService(db)
    offset = (page - 1) * page_size
    items, total = service.list_authors(
        q=q,
        research_group_id=research_group_id,
        limit=page_size,
        offset=offset,
    )
    return AuthorListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/research-groups", response_model=List[ResearchGroupRead])
def list_research_groups(db: Session = Depends(get_db)):
    return AuthorService(db).list_research_groups()

@router.get("/collaborators/by-name", response_model=AuthorCollaboratorsResponse)
def get_collaborators_by_name(
    name: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    service = AuthorService(db)
    matches = service.get_authors_by_name(name)

    if not matches:
        raise HTTPException(status_code=404, detail=f"No author matching '{name}' was found in the database.")
    if len(matches) > 1:
        raise HTTPException(
            status_code=409,
            detail={
                "message": f"The name '{name}' matched {len(matches)} authors in the database. Refine the name.",
                "candidates": [
                    {"id": author.id, "display_name": author.display_name, "orcid": author.orcid}
                    for author in matches
                ],
            },
        )

    author = matches[0]
    collaborators = service.get_collaborators_with_location(author.id)

    return AuthorCollaboratorsResponse(
        author=AuthorReadLite(id=author.id, display_name=author.display_name, orcid=author.orcid),
        collaborators=collaborators or [],
    )


@router.get("/{author_id}", response_model=AuthorReadLite)
def get_author(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author(author_id)

    if not author:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")

    return author


@router.get("/{author_id}/works", response_model=List[WorkReadWithRelationships])
def get_author_works(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author(author_id)

    if not author:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")

    return service.get_author_works(author_id)



@router.get("/{author_id}/network", response_model=AuthorNetwork)
def get_author_network(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    network = service.get_author_network(author_id)
    if not network:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")
    return network
