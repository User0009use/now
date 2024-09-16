from flask import Flask, request, render_template
from requests import get 

app = Flask(__name__)

@app.route("/")
def root():
    return "/root"

@app.route("/get")
def get_url():
    url = None
    try:
      url = request.args.get("url")
      html = get(url).text
      
      return html
    except Exception as e:
      return f"{e}"
    return " Oops!"

app.run('0.0.0.0')