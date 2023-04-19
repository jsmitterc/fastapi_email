from __future__ import print_function
from fastapi import FastAPI
import os.path
import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



class Email(BaseModel):
    email: str
    sales_id: int

origins = ["*"]




app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']



    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return 1

@app.get("/send")
async def root():
    return 1

@app.post("/send-message")
async def send_message(data: Email):
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except HttpError as error:
                return 1
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        html_file = open('template.html', 'r', encoding='utf-8')
        source_code = html_file.read()

        x = source_code.replace("$salesId$" , str(data.sales_id))

        message.set_content("")
        message.add_alternative(x, subtype='html')

        message['To'] = data.email
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
