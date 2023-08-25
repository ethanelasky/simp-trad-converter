import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


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
    return """Correctly convert Simplified Chinese to Traditional Chinese.

Simplified: 老干妈
Traditional: Correct: 老乾媽 (Note: 幹 is incorrect—it is slang for fuck.)
Simplified: 牛肉面
Traditional: 牛肉麵 (Note: 面 is incorrect—it refers to "surface" or "face")
Simplified: {}
Traditional: """.format(simp_phrase)
