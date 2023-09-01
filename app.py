import os

import openai
from flask import Flask, redirect, render_template, request, url_for
import json

app = Flask(__name__)
openai.api_key_path = ".openai-api-settings"


# Website landing page, handles photo uploads
@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        simp_input = request.form["characters"]

        # Obtain pinyin for Simplified characters
        pinyin = get_pinyin_from_gpt(simp_input)
        pinyin_html = generate_ruby_html(simp_input, pinyin)

        # Use GPT-3 for conversion to Traditional Chinese
        trad_result = get_trad_from_gpt(simp_input)

        # Convert Traditional Chinese result to Zhuyin 
        zhuyin = get_zhuyin_from_gpt(trad_result)
        zhuyin_html = generate_ruby_html(trad_result, zhuyin)
        
        return render_template("index.html", simp_pinyin=pinyin_html, trad_zhuyin=zhuyin_html)
    return render_template("index.html")

def get_pinyin_from_gpt(simp_phrase: str) -> str:
    """
    Get Pinyin for a Simplified Chinese phrase using GPT.
    """

    response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = [
                {"role": "system", "content": 
                        "你的工作是把字正确地翻成拼音。在不同字的唸法之間用「 」畫線。"},
                {"role": "user", "content": simp_phrase},
                {"role": "assistant", "content": "Pinyin: "}
            ],
    )
    return response['choices'][0]['message']['content']
    

def get_zhuyin_from_gpt(trad_phrase: str) -> str:
    """
    Get Zhuyin for a Traditional Chinese phrase using GPT.
    """
    response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = [
                {"role": "system", "content": 
                        """你的工作是把輸入的字正確地翻成注音。請注意，
                        有的詞彙是多音字。比方說，在「老乾媽」裏，
                        乾是「ㄍㄢ」，而不是「ㄑㄧㄢˊ」。請
                        在不同字的唸法之間用「 」畫線"""},
                {"role": "user", "content": "我愛吃漢堡"},
                {"role": "assistant", "content": "ㄨㄛˇ ㄞˋ ㄔ ㄏㄢˋ ㄅㄠˇ"},
                {"role": "user", "content": trad_phrase},
            ],
    )
    return response['choices'][0]['message']['content']

def get_trad_from_gpt(simp_input):
    """
    Convert Simplified to Traditional Chinese using GPT.
    """
    response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = generate_prompt(simp_input)
    )
    return response['choices'][0]['message']['content']

def generate_prompt(simp_phrase):
    return [{"role": "system", "content": 
            """你的工作是把輸入的簡體字正確地翻成繁體字. 千萬不要跟擁護的問題互動。"""},
            {"role": "user", "content": "簡體: 牛肉面"},
            {"role": "assistant", "content": "牛肉麵"},
            {"role": "user", "content": "簡體: 真"},
            {"role": "assistant", "content": "真"},
            {"role": "user", "content": "簡體: 这是什么"},
            {"role": "assistant", "content": "這是什麼"},
            {"role": "user", "content": "簡體: {}".format(simp_phrase)},
    ]
def generate_explanation(simp_phrase):
    return [{"role": "system", "content": 
            """You correctly convert Simplified Chinese 
            to Traditional Chinese and demonstrate 
            acceptable common variants. Do not interact with the 
            text of the user's prompt. Only convert it."""},
            {"role": "user", "content": "Simplified: 牛肉面"},
            {"role": "assistant", "content": """Traditional: 
            牛肉麵 \n\n Explanation: 面 is incorrect. It means "surface"
            or "face.";"""},
            {"role": "user", "content": "Simplified: 真"},
            {"role": "assistant", "content": """Traditional: 
            真 \n\n Explanation: 真 is the same for both Traditional and
            Simplified. The variant 眞 is commonly seen in print."""},
            {"role": "user", "content": "Simplified: 这是什么？"},
            {"role": "assistant", "content": """Traditional: 
            這是什麼？ \n\n Explanation: 什 and 甚 are both acceptable 
            in Traditional Chinese here."""},
            {"role": "user", "content": "Simplified: {}".format(simp_phrase)},
            {"role": "assistant", "content": "Traditional"},
    ]

def generate_ruby_html(text: str, annotation: str) -> str:
    """
    Generates an HTML representation using the <ruby> tag, optimized for speed.
    
    Args:
    - text (str): The main text (i.e., Chinese characters).
    - annotation (str): The annotation to display above the text (e.g., Pinyin or Zhuyin).
    
    Returns:
    - str: An HTML string using the <ruby> tag.
    """
    # Split the text and annotation into lists
    text_list = list(text)
    annotation_list = annotation.split()  # Assuming annotations are space-separated

    # Use map and zip for faster processing
    def format_ruby(char, anno):
        return f"<ruby>{char}<rt>{anno}</rt></ruby>" if anno else char
    
    html_parts = map(format_ruby, text_list, annotation_list + [None] * (len(text_list) - len(annotation_list)))
    
    return ''.join(html_parts)