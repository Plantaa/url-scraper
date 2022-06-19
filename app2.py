from flask import Flask, render_template, request
import requests
import pymongo
from bs4 import BeautifulSoup

app = Flask(__name__)

mongodb_connection_string = "mongodb+srv://vmcabredo:nDMJbuw_z-U_DY9i_gG.@cluster0.wdf8syz.mongodb.net/?retryWrites=true&w=majority"
db_name = "testedb"
url = 'https://www.geeksforgeeks.org/'

client = pymongo.MongoClient(mongodb_connection_string)
db = client.get_database(db_name)
collection = db.teste

@app.route("/", methods = ["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/scraper", methods = ["POST"])
def url_scraper():
    url = request.json["url"]
    if url:
        res_insert_one = requests.post("http://localhost:5000/insert/one", json={"url": url}).json()
        res_scrape = requests.post("http://localhost:5000/scrape", json={"url": url}).json()
        res_insert_many = requests.post("http://localhost:5000/insert/many", json={"urls": res_scrape["urls"]}).json()
        documents = list(collection.find())
        for document in documents:
            res_scrape = requests.post("http://localhost:5000/scrape", json={"url": document["url"]}).json()
            if res_scrape["urls"] == []:
                pass
            res_insert_many = requests.post("http://localhost:5000/insert/many", json={"urls": res_scrape["urls"]}).json()
            documents = list(collection.find())
        return {"message": "Scraping completed"}
    else:
        response = {"Message": "URL not present"}
        return response

@app.route("/scrape", methods = ["POST"])
def scrape():
    url = request.json["url"]
    if collection.find_one({"url": url})["visited"]:
        return {"urls": []}
    url = request.json["url"]
    try:
        req = requests.get(url)
    except requests.exceptions.InvalidSchema:
        return url
    except requests.exceptions.MissingSchema:
        return []
    soup = BeautifulSoup(req.text, "html.parser")
    urls = []
    for link in soup.find_all("a"):
        current_link = link.get("href")
        if current_link == "#main" or current_link == url:
            pass
        else:
            urls.append(current_link)
    collection.update_one({"url": url}, {"$set": {"visited": True}})
    unique_urls = list(set(urls))
    response = {"urls": unique_urls}
    return response

@app.route("/insert/one", methods = ["POST"])
def insert_url():
    url = request.json["url"]
    if url:
        if collection.find_one({"url": url}):
            return {"message": "url already stored"}
        collection.insert_one({"url": url,"visited": False})
        response = {"message": "url inserted"}
        return response
    else:
        {"message": "url not present"}

@app.route("/insert/many", methods = ["POST"])
def insert_urls():
    urls = request.json["urls"]
    inserted_urls = []
    if urls:
        for url in urls:
            data = collection.find_one({"url": url})
            if data == None:
                inserted_urls.append({
                    "url": url,
                    "visited": False
                })
        if inserted_urls != []:
            collection.insert_many(inserted_urls)
            response = {
                "message": "%d urls inserted" %len(inserted_urls)
            }
            print(response)
            return response
        else:
            response = {
                "message": "no urls were inserted"
            }
            print(response)
            return response
    else:
        response = {
            "message": "no new urls"
        }
        print(response)
        return response

if __name__ == "main":
    app.run(debug=True)