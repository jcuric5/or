from flask import Flask, request, redirect, url_for, session, send_file, render_template
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from pymongo import MongoClient
from http import HTTPStatus
from bson.objectid import ObjectId
import json
import subprocess
import os

app = Flask(__name__, template_folder="../")
app.secret_key = "nijetajna"
CORS(app)

db_client = MongoClient("mongodb+srv://josipcuric:1234@or.g7eeo.mongodb.net/")

AUTH0_DOMAIN = "dev-bem7xtv5wt8e2c82.us.auth0.com"
AUTH0_CLIENT_ID = "WD1cTcnHTLfgfwv7GhrCM6Iaa6MCdF2Q"
AUTH0_CLIENT_SECRET = "8dEL8MULpwkNmdjrLTDzIKhbUqJumjhBkupGNZiFnVpVaONC0jnTkLgfDcRkyLmj"
AUTH0_CALLBACK_URL = "http://127.0.0.1:5555/callback"
AUTH0_BASE_URL = f"https://{AUTH0_DOMAIN}"

oauth = OAuth(app)
auth0 = oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=f"{AUTH0_BASE_URL}/oauth/token",
    authorize_url=f"{AUTH0_BASE_URL}/authorize",
    client_kwargs={
        "scope": "openid profile email",
    },
    jwks_uri=f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
)

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
    if type(response_json) == list:
        for i in range(len(response_json)):
            response_json[i]["@context"] = {
                "@vocab" : "http://schema.org/",
                "location" : "GeoCoordinates",
                "name" : "name"
            }
    else:
        response_json["@context"] = {
            "@vocab" : "http://schema.org/",
            "location" : "GeoCoordinates",
            "name" : "name"
        }
    
    upper_level_response = {
        "status" : HTTPStatus(status_code).phrase,
        "message" : user_message,
        "response" : response_json
    }

    return json.dumps(upper_level_response, default=str), status_code, {'Content-Type': 'application/json'}

@app.route("/", endpoint="splash")
def splash():
    if "user" in session.keys():
        return redirect(url_for("home"))
    else:
        return send_file("../index.html")

@app.route("/home")
def home():
    if "user" not in session.keys():
        return redirect(url_for("splash"))
    else:
        return render_template("main.html", user=session["user"]["nickname"])

@app.route("/login")
def login():
    if "user" in session.keys():
        return redirect(url_for("home"))
    else:
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)

@app.route("/logout")
def logout():
    if "user" not in session.keys():
        return redirect(url_for("splash"))
    else:
        del session["user"]

        return redirect(url_for("splash"))

@app.route("/user")
def user():
    if "user" not in session.keys():
        return redirect(url_for("splash"))
    else:
        return send_file("../user.html")
    
@app.route("/explorer")
def explorer():
    if "user" not in session.keys():
        return redirect(url_for("splash"))
    else:
        return send_file("../database.html")

@app.route("/refresh_dump")
def refresh_dump():
    if "user" not in session.keys():
        return redirect(url_for("splash"))
    
    subprocess.Popen("export_csv.bat", shell=True, cwd="D:\\curic\\Desktop\\FER\\7. semestar\\Otvoreno računarstvo\\Laboratorijske vježbe\\or\\backend")
    subprocess.Popen("export_json.bat", shell=True, cwd="D:\\curic\\Desktop\\FER\\7. semestar\\Otvoreno računarstvo\\Laboratorijske vježbe\\or\\backend")

    return redirect(url_for("user"))

@app.route("/ZagrebPristupacnostParkova.csv")
def dump_csv():
    return send_file("./ZagrebPristupacnostParkova.csv")

@app.route("/ZagrebPristupacnostParkova.json")
def dump_json():
    return send_file("./ZagrebPristupacnostParkova.json")

@app.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    session["user"] = token["userinfo"]

    return redirect(url_for("home"))

@app.route("/main.css")
def serve_css():
    return send_file("../frontend/main.css")

@app.route("/main.js")
def serve_js():
    return send_file("../frontend/main.js")

@app.route("/search", methods=["GET"])
def search():
    text = request.args.get("text")
    field = request.args.get("field")

    documents = db_client["ORLAB"]["ZagrebPristupacnostParkova"].find()
    filtered_docs = [doc for doc in filter_documents(documents, text, field)]
    
    for i, doc in enumerate(filtered_docs):
        del doc["_id"]
        
        filtered_docs[i]["@context"] = {
            "@vocab": "http://schema.org/",
            "location": "GeoCoordinates",
            "name" : "name"
        }

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
