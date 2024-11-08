from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient
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
                    print(text, value)
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

@app.route("/search", methods=["GET"])
def search():
    text = request.args.get("text")
    field = request.args.get("field")

    documents = db_client["ORLAB"]["ZagrebPristupacnostParkova"].find()
    filtered_docs = [doc for doc in filter_documents(documents, text, field)]
    
    for doc in filtered_docs:
        del doc["_id"]

    filtered_docs_json_string = json.dumps(filtered_docs, default=str)

    print(filtered_docs_json_string)

    return filtered_docs_json_string, 200, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5555)
