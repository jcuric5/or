from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient
from http import HTTPStatus
from bson.objectid import ObjectId
import json

app = Flask(__name__)
CORS(app)
db_client = MongoClient("mongodb+srv://josipcuric:1234@or.g7eeo.mongodb.net/")

def filter_documents(documents, text, field):
    filter_documents = []

    text = text.lower()

    if field == "*":
        for document in documents:
            for key, value in document.items():
                if key == "_id":
                    continue

                if key == "purpose":
                    for val in value:
                        if text in val.lower():
                            filter_documents.append(document)

                            break
                elif key == "entrances":
                    for val in value:
                        if text in val.lower():
                            filter_documents.append(document)

                            break
                elif key == "area":
                    if text.isnumeric() and int(text) == value:
                        filter_documents.append(document)

                        break
                else:
                    if text in value.lower():
                        filter_documents.append(document)   

                        break  
    elif field == "purpose":
        for document in documents:
            for purpose in document["purpose"]:
                if text in purpose.lower():
                    filter_documents.append(document)

                    break
    elif field == "entrances":
        for document in documents:
            for purpose in document["entrances"]:
                if text in purpose.lower():
                    filter_documents.append(document)

                    break
    elif field == "area":
        if text.isnumeric():
            for document in documents:
                if int(text) == document["area"]:
                    filter_documents.append(document)

                    break
    else:
        for document in documents:
            if text in document[field].lower():
                filter_documents.append(document)

                break

    return filter_documents

def get_document_with_id(id):
    global db_client

    requested_doc = None

    for doc in db_client["ORLAB"]["ZagrebPristupacnostParkova"].find():
        if str(doc["_id"]) == str(id):
            doc["id"] = doc.pop("_id")
            requested_doc = doc

            break

    return requested_doc

def wrap_response(status_code, user_message, response_json):
    upper_level_response = {
        "status" : HTTPStatus(status_code).phrase,
        "message" : user_message,
        "response" : response_json
    }

    return json.dumps(upper_level_response, default=str), status_code, {'Content-Type': 'application/json'}

@app.route("/search", methods=["GET"])
def search():
    text = request.args.get("text")
    field = request.args.get("field")

    documents = db_client["ORLAB"]["ZagrebPristupacnostParkova"].find()
    filtered_docs = [doc for doc in filter_documents(documents, text, field)]
    
    for doc in filtered_docs:
        del doc["_id"]

    filtered_docs_json_string = json.dumps(filtered_docs, default=str)

    return filtered_docs_json_string, 200, {'Content-Type': 'application/json'}

@app.route("/api/v2/parks", methods=["POST"])
def v2_create():
    global db_client
    
    new_doc = request.get_json()
    insert_result = db_client["ORLAB"]["ZagrebPristupacnostParkova"].insert_one(new_doc)
    inserted_doc = get_document_with_id(insert_result.inserted_id)

    if inserted_doc:
        return wrap_response(200, "Park inserted with a unique ID", inserted_doc)
    else:
        return wrap_response(500, "Internal error", None)

@app.route("/api/v2/parks/<id>", methods=["GET"])
def v2_read(id):
    requested_doc = get_document_with_id(id)

    if requested_doc:
        return wrap_response(200, "Park with the given ID fetched", requested_doc)
    else:
        return wrap_response(404, "Park with the given ID does not exist", None)
    
@app.route("/api/v2/parks", methods=["GET"])
def v2_read_all():
    all_docs = [doc for doc in db_client["ORLAB"]["ZagrebPristupacnostParkova"].find()]

    if all_docs:
        return wrap_response(200, "All parks fetched", all_docs)
    else:
        return wrap_response(500, "Internal error", None)

@app.route("/api/v2/parks/<id>", methods=["PUT"])
def v2_update(id):
    global db_client

    update_result = db_client["ORLAB"]["ZagrebPristupacnostParkova"].update_one(
        {"_id": ObjectId(id)},
        {"$set": request.get_json()}
    )
    
    if update_result.matched_count > 0:
        updated_doc = get_document_with_id(id)

        return wrap_response(200, "Park with the given ID updated", updated_doc)
    else:
        return wrap_response(404, "Park with the given ID does not exist", None)

@app.route("/api/v2/parks/<id>", methods=["DELETE"])
def v2_delete(id):
    global db_client

    delete_result = db_client["ORLAB"]["ZagrebPristupacnostParkova"].delete_one(
        {"_id": ObjectId(id)}
    )
    
    if delete_result.deleted_count > 0:  
        return wrap_response(200, "Park with the given ID deleted", {"id" : id})
    else:
        return wrap_response(404, "Park with the given ID does not exist", None)

@app.route('/<path:unrouted_path>')
def unimplemented(unrouted_path):
    return wrap_response(501, "Method not implemented for requested resource", None)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5555)
