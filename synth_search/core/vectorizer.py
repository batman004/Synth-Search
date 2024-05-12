from synth_search import col
from synth_search.config import settings

logger = settings.configure_logging(__name__)


def store_db_context_in_chroma(
    collection_description: str, collection_or_table_name: str
) -> None:
    """
    Stores the data from a MongoDB collection description in a Chroma vector database.

    Args:
        collection_description (dict): A dictionary containing the description of a MongoDB collection.
    """
    try:
        col.add(
            ids=[collection_or_table_name],
            documents=[collection_description],
        )
    except ValueError as v_err:
        logger.exception(f"Could not save DB embeddings due to value error : {v_err}")
        raise ValueError(v_err)
    except Exception as err:
        logger.exception(f"Could not save DB embeddings due to err : {err}")
        raise Exception(err)
