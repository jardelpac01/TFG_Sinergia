from app.routers.authors import router as authors_router
from app.routers.institutions import router as institutions_router
from app.routers.insert_openalex_data import router as insert_openalex_data_router
from app.routers.sources import router as sources_router
from app.routers.topics import router as topics_router
from app.routers.works import router as works_router


__all__ = [
    "authors_router",
    "institutions_router",
    "insert_openalex_data_router",
    "sources_router",
    "topics_router",
    "works_router",
]
