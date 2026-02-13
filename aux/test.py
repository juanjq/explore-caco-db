{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "d1507940",
   "metadata": {},
   "outputs": [],
   "source": [
    "from pymongo import MongoClient\n",
    "from datetime import datetime, timedelta\n",
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "dc6330e5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Processing collection: CACO_min\n",
      "Success! Imported 97085 documents into local Mongo.\n",
      "Processing collection: EVB_min\n",
      "Success! Imported 339893 documents into local Mongo.\n",
      "Processing collection: SIS_min\n",
      "Success! Imported 13500 documents into local Mongo.\n",
      "Processing collection: TIB_min\n",
      "Success! Imported 1877173 documents into local Mongo.\n",
      "Processing collection: UCTS_min\n",
      "Success! Imported 148884 documents into local Mongo.\n",
      "Processing collection: STATE\n",
      "Success! Imported 410804 documents into local Mongo.\n",
      "Processing collection: RUN_INFORMATION\n",
      "Success! Imported 32188 documents into local Mongo.\n"
     ]
    }
   ],
   "source": [
    "REMOTE_DB_NAME = \"CACO\"\n",
    "REMOTE_COL_NAME = \"CACO_min\"\n",
    "\n",
    "# for REMOTE_COL_NAME in [\n",
    "#     \"CACO_min\", \"CBOX_min\", \"CLUSCO_min\", \"ECC_min\", \"EVB_min\", \"SIS_min\", \"TIB_min\", \"UCTS_min\", \"STATE\", \"RUN_INFORMATION\"\n",
    "# ]:\n",
    "for REMOTE_COL_NAME in [\n",
    "    \"CACO_min\", \"EVB_min\", \"SIS_min\", \"TIB_min\", \"UCTS_min\", \"STATE\", \"RUN_INFORMATION\"\n",
    "]:\n",
    "\n",
    "    print(f\"Processing collection: {REMOTE_COL_NAME}\")\n",
    "\n",
    "    try:\n",
    "        client_remote = MongoClient('mongodb://localhost:27018') \n",
    "        client_local = MongoClient('mongodb://localhost:27017')\n",
    "\n",
    "        # one_week_ago = datetime.now() - timedelta(days=30)\n",
    "        query = {}\n",
    "        a = {\"date\": {\n",
    "            \"$gte\": datetime.fromisoformat(\"2025-09-20 21:00:00\"),\n",
    "            \"$lte\": datetime.fromisoformat(\"2025-09-21 01:00:00\")\n",
    "        }}\n",
    "        \n",
    "        source_col = client_remote[REMOTE_DB_NAME][REMOTE_COL_NAME]\n",
    "        local_col = client_local[\"CACO\"][REMOTE_COL_NAME]\n",
    "\n",
    "        local_col.drop()\n",
    "\n",
    "        sample_data = list(source_col.find(query))\n",
    "\n",
    "        if sample_data:\n",
    "            local_col.insert_many(sample_data)\n",
    "            print(f\"Success! Imported {len(sample_data)} documents into local Mongo.\")\n",
    "\n",
    "    except Exception as e:\n",
    "        print(f\"Error: {e}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "dbf11c90",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Total documents in local collection: 0\n"
     ]
    }
   ],
   "source": [
    "client_local = MongoClient('mongodb://localhost:27017')\n",
    "# Replace these with the names you used in your import script!\n",
    "db = client_local['test_db']\n",
    "col = db['test_collection']\n",
    "\n",
    "print(f\"Total documents in local collection: {col.count_documents({})}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "91b7bb34",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Databases found: ['CACO', 'admin', 'config', 'local', 'test_db']\n",
      " -> DB: CACO | Collection: EVB_min | Docs: 339893\n",
      " -> DB: CACO | Collection: CACO_min | Docs: 97085\n",
      " -> DB: CACO | Collection: UCTS_min | Docs: 148884\n",
      " -> DB: CACO | Collection: TIB_min | Docs: 1877173\n",
      " -> DB: CACO | Collection: SIS_min | Docs: 13500\n",
      " -> DB: CACO | Collection: CBOX_min | Docs: 769\n",
      " -> DB: CACO | Collection: STATE | Docs: 410804\n",
      " -> DB: CACO | Collection: RUN_INFORMATION | Docs: 32188\n",
      " -> DB: test_db | Collection: test_collection | Docs: 200\n"
     ]
    }
   ],
   "source": [
    "client = MongoClient('mongodb://localhost:27017')\n",
    "\n",
    "# 1. List all databases\n",
    "dbs = client.list_database_names()\n",
    "print(f\"Databases found: {dbs}\")\n",
    "\n",
    "# 2. List all collections in each database (ignoring system ones)\n",
    "for db_name in dbs:\n",
    "    if db_name not in ['admin', 'config', 'local']:\n",
    "        cols = client[db_name].list_collection_names()\n",
    "        for col_name in cols:\n",
    "            count = client[db_name][col_name].count_documents({})\n",
    "            print(f\" -> DB: {db_name} | Collection: {col_name} | Docs: {count}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "40ba168c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "All variable \"name\" in db: CACO, collection: CACO_min:\n",
      "\n",
      " - CACO_CameraControl_FSM_busy\n",
      " - CACO_CameraControl_FSM_previous_state\n",
      " - CACO_CameraControl_FSM_state\n",
      " - CACO_CameraControl_Information_ModulesStatus_CBOX\n",
      " - CACO_CameraControl_Information_ModulesStatus_CHILLER\n",
      " - CACO_CameraControl_Information_ModulesStatus_CLUS\n",
      " - CACO_CameraControl_Information_ModulesStatus_ECC\n",
      " - CACO_CameraControl_Information_ModulesStatus_EVB\n",
      " - CACO_CameraControl_Information_ModulesStatus_SHUTTER\n",
      " - CACO_CameraControl_Information_ModulesStatus_SIS\n",
      " - CACO_CameraControl_Information_ModulesStatus_SWITCHES\n",
      " - CACO_CameraControl_Information_ModulesStatus_TIB\n",
      " - CACO_CameraControl_Information_ModulesStatus_UCTS\n",
      " - CACO_CameraControl_Information_number_of_threads\n",
      " - CACO_CameraControl_Information_warm-up\n"
     ]
    }
   ],
   "source": [
    "DATABASE = \"CACO\"\n",
    "col = \"CACO_min\"\n",
    "\n",
    "var_names = np.sort(client[DATABASE][col].distinct(\"name\"))\n",
    "print(f\"All variable \\\"name\\\" in db: {DATABASE}, collection: {col}:\\n\")\n",
    "for n in var_names:\n",
    "    print(f\" - {n}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "2eda6101",
   "metadata": {},
   "outputs": [],
   "source": [
    "c = client[DATABASE][col]\n",
    "variable = \"CACO_CameraControl_FSM_busy\"\n",
    "\n",
    "query = {\"name\" : variable}\n",
    "\n",
    "ret = c.find(query)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "498ae479",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "{'_id': ObjectId('68f22f8f0eef7003d40ffd8c'), 'date': datetime.datetime(2025, 10, 17, 11, 59), 'hierarchical_name': 'exports.CameraControl.FSM.busy.busy', 'name': 'CACO_CameraControl_FSM_busy', 'avg': 0.5, 'max': 1.0, 'min': 0.0, 'values': {'11': 0.0, '48': 1.0}}\n"
     ]
    }
   ],
   "source": [
    "for r in ret:\n",
    "    print(r)\n",
    "    break"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "16496094",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "✅ Connection to Remote DB: SUCCESS\n",
      "Remote Databases: ['CACO', 'admin', 'config', 'local', 'tools']\n"
     ]
    }
   ],
   "source": [
    "client_remote = MongoClient('mongodb://localhost:27018/?directConnection=true')\n",
    "\n",
    "try:\n",
    "    # 1. Check if the server is actually there\n",
    "    client_remote.admin.command('ping')\n",
    "    print(\"✅ Connection to Remote DB: SUCCESS\")\n",
    "    \n",
    "    # 2. List remote databases to make sure you have the right name\n",
    "    print(f\"Remote Databases: {client_remote.list_database_names()}\")\n",
    "    \n",
    "except Exception as e:\n",
    "    print(f\"❌ Connection to Remote DB: FAILED. Error: {e}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "580a4c9d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Pulling data...\n",
      "🎉 Success! Moved 200 docs to your local micro-db.\n"
     ]
    }
   ],
   "source": [
    "# Setup connections\n",
    "client_remote = MongoClient('mongodb://localhost:27018/?directConnection=true')\n",
    "client_local = MongoClient('mongodb://localhost:27017')\n",
    "\n",
    "# Update these to match what you saw in Step 1\n",
    "REMOTE_DB = \"CACO\"\n",
    "REMOTE_COL = \"CACO_min\"\n",
    "\n",
    "source_col = client_remote[REMOTE_DB][REMOTE_COL]\n",
    "local_col = client_local['CACO']['CACO_min']\n",
    "\n",
    "# 1. Clear local\n",
    "local_col.drop()\n",
    "\n",
    "# 2. Grab 50 docs regardless of date\n",
    "print(\"Pulling data...\")\n",
    "sample_data = list(source_col.find().limit(200))\n",
    "\n",
    "# 3. Push to local\n",
    "if sample_data:\n",
    "    local_col.insert_many(sample_data)\n",
    "    print(f\"🎉 Success! Moved {len(sample_data)} docs to your local micro-db.\")\n",
    "else:\n",
    "    print(\"⚠️ The remote collection returned 0 docs. Double-check your DB/Collection names!\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7a48798f",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "base",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
