from typing import Any
from typing import Dict

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from synth_search.api.controllers import query_rag
from synth_search.config import settings
from synth_search.core.vectorizer import store_db_context_in_chroma
from synth_search.data_connectors.mongo_connector import describe_mongo_collection
from synth_search.data_connectors.mongo_connector import query_collection

router = APIRouter(responses={404: {"description": "not found"}})

logger = settings.configure_logging(__name__)


@router.post("/add-data-source")
def add_data_source(
    db_name: str, collection_or_table_name: str, db_type: str, request: Request
):
    try:
        collection_description = describe_mongo_collection(
            db_name, collection_or_table_name, db_type, request
        )
        logger.info(
            f"Persisting DB context embeddings in chromaDB for collection_name: {collection_or_table_name}"
        )
        store_db_context_in_chroma(collection_description, collection_or_table_name)

        return JSONResponse(
            content=collection_description, status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {str(e)}"
        )


@router.get("/prompt-to-query")
def get_data_source_query(collection_name: str, query_prompt: str, request: Request):
    return query_rag(collection_name, query_prompt, request)


@router.get("/prompt-to-data")
def query_data_source(
    db_name: str,
    collection_name: str,
    query_prompt: str,
    library_name: str,
    request: Request,
):
    llm_generated_query = query_rag(
        collection_name, query_prompt, library_name, request
    )
    logger.info(f"Generated query : {llm_generated_query}")
    return query_collection(db_name, collection_name, request, llm_generated_query)
