from urllib import response
from flask import Flask, redirect, render_template, request, url_for
import requests
import pymongo
from bs4 import BeautifulSoup

app = Flask(__name__)

mongodb_connection_string = "mongodb+srv://vmcabredo:nDMJbuw_z-U_DY9i_gG.@cluster0.wdf8syz.mongodb.net/?retryWrites=true&w=majority"
db_name = "testedb"

client = pymongo.MongoClient(mongodb_connection_string)
db = client.get_database(db_name)
collection = db.teste

def insert_url(url):
    if collection.find_one({"url": url}):
            return {"message": "url already stored"}
    return collection.insert_one({"url": url,"visited": False})

def insert_urls(urls):
    inserted_urls = []
    for url in urls:
        if collection.find_one({"url": url}) == None:
            inserted_urls.append({"url": url, "visited": False})
    if inserted_urls == []:
        return inserted_urls
    collection.insert_many(inserted_urls)
    return inserted_urls

def scrape_url(url):
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
    urls = list(set(urls))
    collection.update_one({"url": url}, {"$set": {"visited": True}})

    return urls

def get_unscraped_urls():
    unscraped_urls = list(collection.find({"visited": False}))
    return unscraped_urls

@app.route("/", methods = ["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/scraper", methods = ["POST"])
def url_scraper():
    url = request.json["url"]
    if url:
        insert_url(url)
        print("URL inserted: ", url)
        urls = scrape_url(url)
        print("URLS scraped: ", urls)
        insert_urls(urls)
        print("URLS inserted: ", urls)
        unscraped_urls = get_unscraped_urls()
        print("Unscraped URLS: ", unscraped_urls)
        for unscraped_url in unscraped_urls:
            print("unscraped url: ", unscraped_url)
            urls = scrape_url(unscraped_url["url"])
            print("%d URLS scraped" %len(urls))
            insert_urls(urls)
            print("%d URLS inserted" %len(urls))
            unscraped_urls = get_unscraped_urls()
            print("%d Unscraped URLS" %len(unscraped_urls))
        response = {"message": "done"}
    else:
        response = {"message": "url not set"}
    return response
