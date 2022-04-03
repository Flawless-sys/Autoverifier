from __future__ import print_function

import os.path
import base64, requests, re, time
import threading, fake_useragent 

from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)


ua = fake_useragent.UserAgent()

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    check_email(creds)


def check_email(creds):
    try:
        threading.Timer(20.0, check_email, args=[creds]).start()
        print("[GMAIL] Service reading emails.")

        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = results.get('messages', [])

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            if "Hi there Your email address" in msg['snippet']:
                with open('verifiedusernames.txt', 'r+') as f:
                    if message['id'] in f.read():
                        continue
                    else:
                        print(f"[RECIEVED EMAIL] {message['id']}")

                        f.write(f'{message["id"]}\n')

                        latest_link = str(base64.urlsafe_b64decode(msg['payload']['body']['data']), "utf-8")

                        soup = BeautifulSoup(latest_link, 'lxml')

                        links = soup.find_all('a') 

                        print(links[3].get('href'))


                        driver.get(links[3].get('href'))
                        driver.find_element_by_xpath('//*[@id="verify-email"]/button').click()


    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()



