from __future__ import print_function
from fastapi import FastAPI
from quickstart import main
import os.path
import base64
from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText


app = FastAPI()

#937457129680-g2s895p7uiucgrbqfa7j4s2817alnika.apps.googleusercontent.com

#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

@app.get("/")
async def root():
    return main()

@app.get("/send")
async def root():
    return gmail_create_draft()

@app.get("/send-message")
async def root():

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        html_file = open('template.html', 'r', encoding='utf-8')
        source_code = html_file.read()
        message.set_content("1")
        message.add_alternative(source_code, subtype='html')

        message['To'] = 'jsmitterc@gmail.com'
        message['From'] = 'poshlashcl@gmail.com'
        message['Subject'] = '¡Queremos conocer tu opinion!'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message
