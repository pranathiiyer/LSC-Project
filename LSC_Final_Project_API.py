from flask import Flask, render_template, jsonify
import boto3
from datetime import datetime
import mysql.connector

# Create an instance of Flask class (represents our application)
# Pass in name of application's module (__name__ evaluates to current module name)
app = Flask(__name__)
application = app # AWS EB requires it to be called "application"

# on EC2, needs to know region name as well; no config
rds = boto3.client('rds', region_name='us-east-1')
ENDPOINT = "relational-db.cpwt7pwqqywi.us-east-1.rds.amazonaws.com"
PORT = "3306"

# Provide a landing page with some documentation on how to use API
@app.route("/")
def home():
    return render_template('index.html')

# Get items from RDS "wsb_posts" table based on date
@app.route("/api/start_date:<start_date>&end_date:<end_date>")
def post_timeline(start_date, end_date):
    start_utc = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_utc = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    conn =  mysql.connector.connect(host=ENDPOINT, user="username", passwd="password", port=PORT, database="wsb_rds")
    cur = conn.cursor()
    cur.execute("""SELECT * 
                   FROM wsb_posts 
                   WHERE date  
                   BETWEEN %s and %s""",
                (start_utc, end_utc))
    query_results = cur.fetchall()
    conn.close()
    return jsonify(query_results)

# Get items from RDS based on category
@app.route("/api/category:<category>")
def post_category(category):
    conn =  mysql.connector.connect(host=ENDPOINT, user="username", passwd="password", port=PORT, database="wsb_rds")
    cur = conn.cursor()
    cur.execute("""SELECT * 
                   FROM wsb_posts 
                   WHERE category=%s""",
                (category,))
    query_results = cur.fetchall()
    conn.close()
    return jsonify(query_results)

# Get items from RDS based on author
@app.route("/api/author:<author>")
def post_author(author):
    conn =  mysql.connector.connect(host=ENDPOINT, user="username", passwd="password", port=PORT, database="wsb_rds")
    cur = conn.cursor()
    cur.execute("""SELECT * 
                   FROM wsb_posts 
                   WHERE author=%s""",
                (author,))
    query_results = cur.fetchall()
    conn.close()
    return jsonify(query_results)

if __name__ == "__main__":
    application.run()