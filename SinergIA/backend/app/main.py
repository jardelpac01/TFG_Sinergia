from fastapi import FastAPI

from app.routers import insert_openalex_data_router


app = FastAPI(title="Sinergia API")
app.include_router(insert_openalex_data_router)


@app.get("/")
def read_root():
    return {""}
