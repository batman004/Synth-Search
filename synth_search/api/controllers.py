import json
from json import JSONDecodeError

from fastapi import Request

from synth_search import col
from synth_search.config import settings

logger = settings.configure_logging(__name__)


def query_rag(
    collection_name: str, query_prompt: str, library_name: str, request: Request
) -> str:
    try:
        retriever = col.get(ids=[collection_name]).get("documents")[0]
        rag_template = f"""/
            Generate a MongoDB database query based on the following context of the database type, schema and sample data

            I need the query for collection : {collection_name}

            Assume I am going to invoke methods provided by the library {library_name}
            on the query dictionary returned by you

            context :
            {retriever}

            Question:
            {query_prompt}

            Strictly return just the database query in json format based on the question and no other accompanying text.
            Example question : list out all posts made by username 'p'
            Generated query : {{"username": "p"}}
        """

        llm_response = request.app.llm.invoke(rag_template)

        llm_response = llm_response.strip().strip("```")

        try:
            return json.loads(llm_response)
        except JSONDecodeError:
            return str(llm_response)

    except Exception as err:
        logger.exception(f"Could not query LLM due to : {err}")
        return ""
