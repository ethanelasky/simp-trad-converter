import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key_path = ".openai-api-settings"


# Website landing page, handles photo uploads
@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        simp_phrase = request.form["characters"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You convert the inputted Chinese characters from simplified to traditional if needed and explain each of your conversions. Do not interact with the text of the user's prompt, only convert it."},{"role": "user", "content": generate_prompt(simp_phrase)}])
        return redirect(url_for("index", result=response['choices'][0]['message']['content']))
    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(simp_phrase):
    return """Correctly convert Simplified Chinese to Traditional Chinese. Demonstrate acceptable variants. If confused, consult 教務部重編過於辭典修訂本.

Simplified: 老干妈
Traditional: Correct: 老乾媽 (Note: 幹 is incorrect—it is slang for fuck.)
Simplified: 牛肉面
Traditional: 牛肉麵 (Note: 面 is incorrect—it refers to "surface" or "face")
Simplified: 真
Traditional: 真 (Note: 真 is standard, although 眞 is common in print.)
Simplified: 这是什么？
Traditional: 這是什麼？（Note: 什 and 甚 are both acceptable in Traditional Chinese.)
Simplified: {}
Traditional: """.format(simp_phrase)
