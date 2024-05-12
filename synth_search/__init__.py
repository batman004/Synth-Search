import chromadb

client = chromadb.PersistentClient(path=f"./chroma_data/")
col = client.get_or_create_collection("synth_search_db_context")
