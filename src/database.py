import pymongo
import streamlit as st
from src.config import MONGO_URI, DATABASE_NAME, ALLOWED_SUFFIXES

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
    """Executes the query and returns the sorted data."""
    query = {"name": {"$in": selected_vars}, "date": {"$gte": start_dt, "$lte": end_dt}}
    return list(collection.find(query).sort("date", 1))