from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi import Request
from langchain_community.llms import Ollama

from synth_search.api.routers import router as synth_search_router
from synth_search.config import settings
from synth_search.data_connectors.mongo_connector import get_mongodb_client

logger = settings.configure_logging(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    try:
        app.llm = Ollama(
            model=settings.LLM_MODEL_NAME,
            verbose=True,
            temperature=settings.LLM_TEMPERATURE,
            keep_alive="1h",
        )
        # currently assuming client has already addded a data source
        app.db = get_mongodb_client(settings.DB_URL)
        yield
    except Exception as err:
        logger.exception(f"Could not set up API objects due to : {err}")


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=app_lifespan)


@app.get("/")
def read_root(request: Request):
    logger.info(f"Sending ping prompt to LLM")
    response_from_llm = request.app.llm.invoke(
        f"""
        Hi, are you awake? strictly answer with :
        'Hi my name is {settings.LLM_MODEL_NAME}! I'm up'
    """
    )
    return {"message": f"{response_from_llm}"}


app.include_router(synth_search_router, tags=["POC"], prefix="/synth-search/poc")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        reload=settings.DEBUG_MODE,
        port=settings.PORT,
    )
