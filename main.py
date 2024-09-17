from flask import Flask, request
from requests import get, post
from re import sub

app = Flask(__name__)

@app.route("/")
def root():
    url = request.args.get("url")
    try:
      html = get(url).text 
      
      return html
    except:
       return "Opps!"

app.run("0.0.0.0")