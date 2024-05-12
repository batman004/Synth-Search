import json
from typing import Any
from typing import Dict

import pymongo
from fastapi import Request
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from synth_search.config import settings

logger = settings.configure_logging(__name__)


def get_mongodb_client(db_url: str) -> MongoClient:
    """
    Connects to a MongoDB server and retuns a callable client

    Args:
        db_url (str): The connection url of the MongoDB.
    Returns:
        pymongo.MongoClient: The MongoDB client object.
    Raises:
        pymongo.errors.PyMongoError: If there's an error connecting to MongoDB.
    """
    try:
        client = pymongo.MongoClient(db_url)
        return client
    except pymongo.errors.PyMongoError as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise e


def describe_mongo_collection(
    db_name: str, collection_or_table_name: str, db_type: str, request: Request
) -> str:
    """
    Generates a paragraph description of a MongoDB collection.

    Args:
        collection (pymongo.collection.Collection): The MongoDB collection object.
        db_type (str): The type of database.

    Returns:
        str: A paragraph describing the collection.
    """
    collection: Collection = request.app.db[db_name][collection_or_table_name]
    collection_name = collection.name
    database_name = collection.database.name

    schema_description = "The schema of this collection includes:\n"
    schema = collection.find_one()
    if schema:
        schema = dict(schema)
        for key, value in schema.items():
            schema_description += f"- {key}: {type(value).__name__}\n"
    else:
        schema_description += "No schema information available.\n"

    total_documents = collection.count_documents({})
    total_documents_description = (
        f"The total number of documents in this collection is {total_documents}.\n"
    )

    sample_documents_description = (
        "Here are some sample documents from this collection:\n"
    )
    random_data = list(collection.aggregate([{"$sample": {"size": 5}}]))
    if random_data:
        for idx, doc in enumerate(random_data):
            sample_documents_description += f"Document {idx + 1}:\n"
            for key, value in doc.items():
                sample_documents_description += f"  - {key}: {value}\n"
            sample_documents_description += "\n"
    else:
        sample_documents_description += "No sample documents available.\n"

    database_description = (
        f"This paragraph describes the MongoDB collection '{collection_name}' "
        f"in the database '{database_name}'. "
        f"{schema_description} "
        f"{total_documents_description} "
        f"{sample_documents_description}"
        f"The database type is {db_type}."
    )

    return database_description


def query_collection(
    db_name: str,
    collection_or_table_name: str,
    request: Request,
    query: Dict[str, Any] | str,
) -> list:
    """
    Query a MongoDB collection and return documents based on the given query.

    Args:
        collection (pymongo.collection.Collection): The MongoDB collection object.
        query (dict): The query to filter documents.

    Returns:
        list: A list of documents matching the query.
    """
    try:
        collection: Collection = request.app.db[db_name][collection_or_table_name]

        if isinstance(query, str):
            query = json.loads(query)

        documents = list(collection.find(query))
        return documents
    except PyMongoError as e:
        logger.error(f"Error querying collection: {e}")
        return []
