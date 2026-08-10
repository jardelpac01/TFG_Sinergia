from sqlmodel import Session

from app.database import engine
from app.services.openalex_data import OpenAlexService


def main():
    db = Session(engine)
    try:
        service = OpenAlexService(db)
        orcid_de_prueba = "0000-0003-3160-7414"

        print("Iniciando descarga y guardado...")
        author_id = service.fetch_and_store_author(orcid_de_prueba)
        print(f"Proceso completado. Author ID: {author_id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
