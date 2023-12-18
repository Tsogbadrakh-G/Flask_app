import os
import re
from datetime import datetime
import wave
import time
from flask import Flask, jsonify, render_template, request, redirect, session

from agora_token.RtcTokenBuilder import Role_Subscriber, RtcTokenBuilder
app = Flask(__name__)
from gradio_client import Client
from gradio_client import Client

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging


import requests

client = Client("https://facebook-seamless-m4t.hf.space/")
cred = credentials.Certificate("./language-exchange-app.json")
firebase_admin.initialize_app(cred)

app_init=False

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

@app.route("/sendChat", methods=['GET'])
def send_Notification():

    fcm=request.form.get('fcm')
    name=request.form.get('name')
    content=request.form.get('content')
    print('send notification:'+fcm+' name:'+name+' content:'+content)
    
    
    
   
  #  if not app_init:
        
        #app_init=True

    # Create a message with the notification payload
    message = messaging.Message(
        notification=messaging.Notification(
            title=name,
            body=content,
        ),
      
        token=fcm,  # Replace with the FCM token of the target device
    )

    # Send the message
    response = messaging.send(message)
    print("Successfully sent message:", response)
    return response

@app.route('/generate_agora_token/<channelName>', methods=['POST'])
def generate_token(channelName):
   
   
    # Your Agora App ID and App Certificate
    app_id = "d565b44b98164c39b2b1855292b22dd2"
    app_certificate = "caf2f127d2a64a5d92afaf7aee8b3609"
    # User ID (Optional)
    user_id =request.form.get('uid')
 
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channelName, user_id, 1, privilegeExpiredTs)
    print('token: ',token)
    print('channel name',channelName)
    print('uid',user_id)
    return jsonify({'token': token})



@app.route('/todo', methods=["POST"])
def get_todos():
    try:
        conv_type=request.form.get('type')
       
        input_lan=request.form.get('input')
        output_lan=request.form.get('output')
       
      
      
        print(input_lan)
        print(output_lan)
       

        # input_lan="English"
        # output_lan="Halh Mongolian"
        # translation="S2TT (Speech to Text translation)"
        if conv_type=="audio":
            chatroomid=request.form.get('roomId')
            username=request.form.get('myUsername')

            print('roomid',chatroomid)
            print('myusername',username)
            translation=request.form.get('translation')
            audio_file = request.files['audio']
            print(translation)
            if audio_file:
                print('1')
            #     # Save the audio file to a desired location
                save_path = os.path.join(os.getcwd(), 'uploads', audio_file.filename)
                audio_file.save(save_path)
                
                result = translate(save_path, input_lan, output_lan, translation)
                #result = translate(save_path)
                print(result)

                
                if output_lan == 'Halh Mongolian':
                    # to Mongol start block
                  targeted_languga_text=convertTuple(result)   
                  synthesize(targeted_languga_text,chatroomId=chatroomid,username=username)
                #to Mongol end block
                else:
                
                    print('to foriegn')
                
            
                    print(result[0])
                    path= result[0]

                    #  below is speech to speech start

                    with wave.open(path, 'r') as wf:
                            # Read audio data
                        audio_data = wf.readframes(-1)
                    print('Audio data read successfully.')

                    new_directory = '/home/ubuntu/download/'+chatroomid+'/'+username
                    print(new_directory)
                    print(os.path.exists(new_directory))
                    if not os.path.exists(new_directory):
                        print('creating direcotry')
                        os.makedirs(new_directory)
                        print('created')

                    translated_path = os.path.join(os.getcwd(), new_directory+ '/output.wav')
                    with wave.open(translated_path, 'w') as new_wf:
                            # Write audio data to the new file
                        new_wf.setnchannels(wf.getnchannels())
                        new_wf.setsampwidth(wf.getsampwidth())
                        new_wf.setframerate(wf.getframerate())
                        new_wf.writeframes(audio_data)
                    print('Audio data written to the new file:', translated_path)
                        
                    print('4')
                
            # end s2s
                return jsonify({'message': get_file_url(chatroomid,username)}), 200
            else:
                return jsonify({'error': 'No audio file provided'}), 400
        else:
             print('pre translate text')
             txt=request.form.get('text')
             result = translate_text(txt, input_lan, output_lan)
             targeted_languga_text=convertTuple(result)   
             print('translated text',targeted_languga_text)
             return jsonify({'message': targeted_languga_text}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


def get_file_url(chatroomid,username):
   
    url='http://13.125.68.71/download/'+chatroomid+'/'+username+'/output.wav'
    return url

def convertTuple(tup):
    if(len(tup)>0):
      st = ''.join(map(str, tup))
      return st[4:len(st)]
    
def translate(url, input_lan, output_lan,translate):

    if output_lan=='Halh Mongolian':
        result = client.predict(
                    translate,	# str  in 'Task' Dropdown component
                    "files",	# str in 'Audio source' Radio component
                    url,	# str (filepath or URL to file) in 'Input speech' Audio component
                    url,	# str (filepath or URL to file)in  'Input speech'# Audio component
                    "hi!",	# str in 'Input text' Textbox component
                    input_lan,	# str  in 'Source language' Dropdown component
                    output_lan,	# str  in 'Target language' Dropdown component
                    api_name="/run"
                    )       


        return result
    else:

        result = client.predict(  
                        translate,	# str  in 'Task' Dropdown component
                        "files",	# str in 'Audio source' Radio component
                        url,	# str (filepath or URL to file) in 'Input speech' Audio component
                        url,	# str (filepath or URL to file)in  'Input speech'# Audio component
                        "hi!",	# str in 'Input text' Textbox component
                        input_lan,	# str  in 'Source language' Dropdown component
                        output_lan,	# str  in 'Target language' Dropdown component
                        api_name="/run"
        )
        return result

def translate_text(txt, input_lan, output_lan):


        result = client.predict(  
                        'T2TT (Text to Text translation)',	# str  in 'Task' Dropdown component
                        "files",	# str in 'Audio source' Radio component
                        '',	# str (filepath or URL to file) in 'Input speech' Audio component
                        '',	# str (filepath or URL to file)in  'Input speech'# Audio component
                        txt,	# str in 'Input text' Textbox component
                        input_lan,	# str  in 'Source language' Dropdown component
                        output_lan,	# str  in 'Target language' Dropdown component
                        api_name="/run"
        )
        return result

def synthesize(text,chatroomId, username):
    url = "https://api.chimege.com/v1.2/synthesize"
    headers = {
        'Content-Type': 'plain/text',
        'Token': '7769d0fe9a57fda0588cae44dff6f469ad1ea464a003a0f004034c3443f9fe40',
    }
    print('pre calling chimege api')
    r = requests.post(
        url, data=text.encode('utf-8'), headers=headers)
    
    print('after calling chimege api')

    with open("/home/ubuntu/download/"+chatroomId+"/"+username+"/output.wav", 'wb') as out:
        out.write(r.content)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
