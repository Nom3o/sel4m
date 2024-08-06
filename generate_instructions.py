from gtts import gTTS
import os

instructions = {
    'blink_your_eyes': 'Please blink your eyes.',
    'open_your_mouth': 'Please open your mouth.'
}

if not os.path.exists('static/instructions'):
    os.makedirs('static/instructions')

for instruction, text in instructions.items():
    tts = gTTS(text=text, lang='en')
    tts.save(f'static/instructions/{instruction}.mp3')
