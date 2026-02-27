import pymongo
import streamlit as st
from pymongo.errors import ExecutionTimeout
from src.config import MONGO_URI, DATABASE_NAME, ALLOWED_SUFFIXES, SAFE_QUERY_LIMIT, MAX_QUERY_TIME_MS

@st.cache_resource
def get_db():
    client = pymongo.MongoClient(MONGO_URI)
    return client[DATABASE_NAME]

def get_mongo_connection_info():
    """Extracts host and port for display purposes."""
    mongo_host = MONGO_URI.replace("mongodb://", "").replace("/", "")
    if ":" in mongo_host:
        return mongo_host.split(":")
    return mongo_host, "27017"

def get_filtered_collections(db):
    """Returns collections that match the allowed resolution suffixes."""
    all_collections = list(db.list_collection_names())
    return [col for col in all_collections if any(col.endswith(suffix) for suffix in ALLOWED_SUFFIXES)]

def fetch_data(collection, selected_vars, start_dt, end_dt):
    """Executes the query and returns the sorted data.

    Safety check: first do a fast `count_documents` and, if the result
    exceeds `SAFE_QUERY_LIMIT`, warn the user and require explicit
    confirmation via a Streamlit button before running the full query.
    """
    query = {"name": {"$in": selected_vars}, "date": {"$gte": start_dt, "$lte": end_dt}}

    # Fast count check with timeout
    try:
        count = collection.count_documents(query, maxTimeMS=MAX_QUERY_TIME_MS)
    except ExecutionTimeout:
        st.error("Query timed out while counting results. Please narrow your filters.")
        st.stop()
    except Exception:
        # If count fails for any other reason, fall back to running the query
        count = 0

    if count > SAFE_QUERY_LIMIT:
        st.warning(f"(!) This query will return {count:,} documents.")
        st.info("Large queries can slow down the cluster. Are you sure you need all this data?")

        # Require user confirmation to proceed. On first run this will render
        # the button and then call `st.stop()` to avoid executing the heavy query.
        if not st.button("Download anyway"):
            st.stop()

    # If safe or confirmed, execute the query with a maximum execution time
    try:
        return list(collection.find(query, max_time_ms=MAX_QUERY_TIME_MS).sort("date", 1))
    except ExecutionTimeout:
        st.error("Query exceeded maximum execution time (60 s). Please narrow your filters.")
        return []