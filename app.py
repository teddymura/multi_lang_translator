from flask import Flask, request, jsonify, render_template, url_for
from googletrans import Translator
from gtts import gTTS
import os
import glob
import time

app = Flask(__name__)

# 出力フォルダ
OUTPUT_DIR = "static"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# TTS対応言語
SUPPORTED_TTS_LANGS = [
    "ja", "en", "fr", "de", "es", "ko", "it", "vi", "zh-cn", "zh-tw", "id"
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/translate_tts", methods=["POST"])
def translate_tts():
    try:
        data = request.get_json()
        text = data.get("text")
        target_lang = data.get("target_lang", "en")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # 翻訳
        translator = Translator()
        translated = translator.translate(text, dest=target_lang)
        translated_text = translated.text
        tts_lang = target_lang

        audio_url = None
        if tts_lang in SUPPORTED_TTS_LANGS:
            filename = f"output_{tts_lang}_{int(time.time())}.mp3"
            filepath = os.path.join(OUTPUT_DIR, filename)

            tts = gTTS(translated_text, lang=tts_lang)
            tts.save(filepath)
            audio_url = url_for("static", filename=filename)

            # 古いMP3は最新5つだけ残す
            cleanup_old_files()

        return jsonify({
            "translated_text": translated_text,
            "audio_url": audio_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cleanup_old_files():
    """staticフォルダ内の古いMP3を削除して最新5つだけ残す"""
    files = glob.glob(os.path.join(OUTPUT_DIR, "output_*.mp3"))
    files.sort(key=os.path.getmtime, reverse=True)
    for old_file in files[5:]:
        try:
            os.remove(old_file)
        except Exception as e:
            print(f"File delete error: {e}")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
