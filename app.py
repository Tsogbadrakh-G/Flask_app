import os
import re
from datetime import datetime
import wave
from flask import Flask, jsonify, render_template, request, redirect, session
app = Flask(__name__)
from gradio_client import Client
from gradio_client import Client
import requests

client = Client("https://facebook-seamless-m4t.hf.space/")

@app.route("/")
def home():
    return "Hello, Flask!"


@app.route("/hello/<name>")
def hello_there(name):
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")

    # Filter the name argument to letters only using regular expressions. URL arguments
    # can contain arbitrary text, so we restrict to safe characters only.
    match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return content


@app.route('/todo', methods=["POST"])
def get_todos():
    try:
        audio_file = request.files['audio']


        if audio_file:
        #     # Save the audio file to a desired location
            save_path = os.path.join(os.getcwd(), 'uploads', audio_file.filename)
            audio_file.save(save_path)
            result = translate(save_path)

            # to Mongol start block
            targeted_languga_text=convertTuple(result)   
            synthesize(targeted_languga_text)
            #to Mongol end block

            print(result[0])
            path= result[0]

          #  below is speech to speech start

            # with wave.open(path, 'r') as wf:
            #     # Read audio data
            #     audio_data = wf.readframes(-1)
            #     print('Audio data read successfully.')

            # translated_path = os.path.join(os.getcwd(), 'translated', audio_file.filename)
            # with wave.open(translated_path, 'w') as new_wf:
            #     # Write audio data to the new file
            #     new_wf.setnchannels(wf.getnchannels())
            #     new_wf.setsampwidth(wf.getsampwidth())
            #     new_wf.setframerate(wf.getframerate())
            #     new_wf.writeframes(audio_data)
            #     print('Audio data written to the new file:', translated_path)
            

           # audio_file.save(os.path.join('path/to/save', audio_file.filename))
           # end s2s
            return jsonify({'message': get_file_url()}), 200
        else:
            return jsonify({'error': 'No audio file provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_file_url():
   
    url='http://51.20.44.63:5000/translated/output.wav'
    return url

def convertTuple(tup):
    if(len(tup)>0):
      st = ''.join(map(str, tup))
      return st[4:len(st)-1]
    
def translate(url):
    result = client.predict(
				"S2TT (Speech to Text translation)",	# str  in 'Task' Dropdown component
                "files",	# str in 'Audio source' Radio component
				url,	# str (filepath or URL to file) in 'Input speech' Audio component
				url,	# str (filepath or URL to file)in  'Input speech'# Audio component
				"hi!",	# str in 'Input text' Textbox component
				"English",	# str  in 'Source language' Dropdown component
				"Halh Mongolian",	# str  in 'Target language' Dropdown component
				api_name="/run"
                )       

       
    return result
    # result = client.predict(  
    #                 "S2ST (Speech to Speech translation)",	# str  in 'Task' Dropdown component
    #                 "files",	# str in 'Audio source' Radio component
    #                 url,	# str (filepath or URL to file) in 'Input speech' Audio component
    #                 url,	# str (filepath or URL to file)in  'Input speech'# Audio component
    #                 "hi!",	# str in 'Input text' Textbox component
    #                 "Halh Mongolian",	# str  in 'Source language' Dropdown component
    #                 "English",	# str  in 'Target language' Dropdown component
    #                 api_name="/run"
    # )
    # return result



def synthesize(text):
    url = "https://api.chimege.com/v1.2/synthesize"
    headers = {
        'Content-Type': 'plain/text',
        'Token': '7769d0fe9a57fda0588cae44dff6f469ad1ea464a003a0f004034c3443f9fe40',
    }

    r = requests.post(
        url, data=text.encode('utf-8'), headers=headers)

    with open("translated/output.wav", 'wb') as out:
        out.write(r.content)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)