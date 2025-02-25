# Import packages
import requests
from datetime import datetime
import boto3
import mysql.connector
import json
import dataset

# Define Lambda function
def lambda_handler(event, context):
    reddit_scraper(event["url_list"])
    return {'StatusCode': 200}  
    
# Define scraping functions

# scrape each url in list
def reddit_scraper(url_list):
    db = db_generator()
    for url in url_list:
        try:
            r = requests.get(url)
            doc = r.json()
            rds_input(doc, db)
        except:
            print("Failed to Scrape the following reddit link:" + url)

# once in url iterate through reddit posts and read data into RDS
def rds_input(doc, db):
    # Update rds table
    for post in doc["data"]:
        if len(post["selftext"]) > 0 and post["selftext"] != "[removed]":
            title = post["title"]
            link = post["full_link"]
            text = post["selftext"]
            author = post["author"]
            category = post["link_flair_text"]
            n_comments = post["num_comments"]
            upvotes = post["score"]
            upvote_ratio = post["upvote_ratio"]
            n_awards = post["total_awards_received"]
            date = post["created_utc"]
            db["wsb_posts"].upsert({"link": link,
                                    "title": title,
                                    "text": text,
                                    "author": author,
                                    "category": category,
                                    "n_comments": n_comments, 
                                    "upvotes": upvotes,
                                    "upvote_ratio": upvote_ratio,
                                    "n_awards": n_awards,
                                    "date": date},
                                   ["date"])

    
def db_generator():
    # Open up SQL connection
    rds = boto3.client("rds")
    db = rds.describe_db_instances()['DBInstances'][0]
    endpoint = db['Endpoint']['Address']
    port = db['Endpoint']['Port']
    user = "username"
    passw = "password"

    # Access table to store scraped data
    db_url = "mysql+mysqlconnector://{}:{}@{}:{}/wsb_rds".format(user,
                                                                passw,
                                                                endpoint,
                                                                port)
    db = dataset.connect(db_url)
    return db