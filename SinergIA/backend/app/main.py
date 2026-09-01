from fastapi import FastAPI

from app.routers import (
    authors_router,
    institutions_router,
    insert_openalex_data_router,
    sources_router,
    topics_router,
    works_router,
)


app = FastAPI(title="Sinergia API")
app.include_router(insert_openalex_data_router)
app.include_router(authors_router)
app.include_router(works_router)
app.include_router(institutions_router)
app.include_router(topics_router)
app.include_router(sources_router)


@app.get("/")
def read_root():
    return {"status": "ok"}
