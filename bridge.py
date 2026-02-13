from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime, timedelta
import traceback
import math

app = Flask(__name__)

# --- CONFIGURATION ---
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "CACO"
# The list of collections we want to aggregate
COLLECTIONS = ["EVB_min", "CACO_min", "UCTS_min", "TIB_min", "SIS_min", "CBOX_min", "STATE", "RUN_INFORMATION"]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route("/names", methods=["GET"])
def get_names():
    """Returns a unique list of all 'name' fields across all collections."""
    try:
        unique_names = set()
        for col_name in COLLECTIONS:
            # .distinct is much faster than loading all documents
            names = db[col_name].distinct("name")
            unique_names.update(names)
        
        # Remove None or empty strings if they exist
        result = [name for name in unique_names if name]
        return jsonify(sorted(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/data", methods=["GET"])
def get_data():
    try:
        from_time = request.args.get('from')
        to_time = request.args.get('to')
        selected_name = request.args.get('name')

        # Robust Time Parsing
        try:
            if from_time and to_time:
                # Handle both millisecond strings and floats
                start_dt = datetime.fromtimestamp(float(from_time)/1000)
                end_dt = datetime.fromtimestamp(float(to_time)/1000)
            else:
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(hours=1)
        except (ValueError, TypeError) as e:
            # If Grafana sends a format we didn't expect, don't crash, use fallback
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(hours=1)

        clean_results = []

        for col_name in COLLECTIONS:
            # IMPORTANT: Ensure your MongoDB 'date' field is actually a Date object
            # If 'date' is a string in Mongo, you'll need to adjust this query
            query = {"date": {"$gte": start_dt, "$lte": end_dt}}
            
            if selected_name and selected_name not in ["All", "$__all", ""]:
                names_list = selected_name.split(',')
                query["name"] = {"$in": names_list}

            # Only fetch what you need to save memory
            projection = {"_id": 0, "date": 1, "name": 1, "avg": 1}
            raw_docs = list(db[col_name].find(query, projection).limit(5000))

            for doc in raw_docs:
                dt = doc.get("date")
                # If Mongo date is already a datetime object:
                iso_date = dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
                
                # Sanitize avg value - convert NaN/Infinity to None
                avg_val = doc.get("avg", 0)
                if isinstance(avg_val, float) and (math.isnan(avg_val) or math.isinf(avg_val)):
                    avg_val = None
                
                clean_results.append({
                    "time": iso_date,
                    "name": doc.get("name", col_name),
                    "collection": col_name,
                    "avg": avg_val
                })

        return jsonify(clean_results)

    except Exception as e:
        # This ensures the error is SENT as JSON so Grafana doesn't see "N"
        return jsonify({"error": str(e), "details": traceback.format_exc()}), 500

if __name__ == "__main__":
    print(f"Bridge Active. Monitoring {len(COLLECTIONS)} collections in {DB_NAME}...")
    # host="0.0.0.0" is required for Docker-to-Host networking
    app.run(host="0.0.0.0", port=5000, debug=False)