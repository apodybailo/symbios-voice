
import os
import telebot
import whisper
from pydub import AudioSegment
from flask import Flask, request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
model = whisper.load_model("base")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        ogg_path = f"voice_inputs/{message.voice.file_id}.ogg"
        wav_path = ogg_path.replace(".ogg", ".wav")

        os.makedirs("voice_inputs", exist_ok=True)
        with open(ogg_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        audio = AudioSegment.from_file(ogg_path)
        audio.export(wav_path, format="wav")

        result = model.transcribe(wav_path)
        recognized_text = result["text"]

        bot.send_message(message.chat.id, f"🎧 Розпізнано: {recognized_text}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Помилка обробки голосу: {str(e)}")

if __name__ == "__main__":
    app.run(port=8000)
