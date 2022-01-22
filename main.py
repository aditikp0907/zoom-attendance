import flask
from flask import request
from dotenv import load_dotenv
import requests
import gspread
from google.oauth2.service_account import Credentials
import os
import datetime
import json

load_dotenv()
# .env
whatsapp_api_url = os.getenv('whatsapp_api_url')
group_jid = os.getenv('group_jid')

sheetId = os.getenv('sheet_id')

scope = ['https://www.googleapis.com/auth/spreadsheets']

# Assign credentials ann path of style sheet
credentials = Credentials.from_service_account_file(
    'creds.json',
    scopes=scope
)
client = gspread.authorize(credentials)

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def updateAttendence(email):
    try:
        spreadsheet = client.open_by_key(
            sheetId)
        sheet1 = spreadsheet.worksheet("Sheet1")
        sheet1_data = sheet1.get_all_records()
        todayDate = datetime.datetime.now().date()
        
        headers = sheet1.row_values(1)
        
        enumerated_headers = list(enumerate(headers))
       
        lookup_table = dict(enumerated_headers)
 
        lookup_table_reversed = {value: key for key, value in lookup_table.items()}
        
        columnNumber=lookup_table_reversed[str(todayDate)]
        for i, row in enumerate(sheet1_data):
            # find email in google sheet
            if row['Email'] == email:
                # mark attendance
                sheet1.update_cell(i+2, columnNumber +1, 'P')
                print(f"{email} marked pressed")
                # get absent users
                getAbsentUser()

    except Exception as e:
        print(f"error {e}")


@app.route('/hello-world', methods=['GET'])
def hello_world():
    return "Hello World"


@app.route('/updateAttendance', methods=['POST'])
def log_attendence():
    try:
        data = request.json
        email=data['email']
        updateAttendence(email)
    except Exception as e:
        print(f"error {e}")
    return "", 200


def sendToWhatsapp(messageToSend):
    try:
        requests.post(whatsapp_api_url, data={
            "message": f"{messageToSend}", "chatJid": group_jid})
        print('message sent')
        return "OK"
    except Exception as e:
        print(f"error unable to send message{e}")
        print(messageToSend)
        return "Failed"


def getAbsentUser():
    try:
        spreadsheet = client.open_by_key(
            sheetId)
        sheet1 = spreadsheet.worksheet("Sheet1")
        sheet1_data = sheet1.get_all_records()
        messageToSend = '*Yet to join*\n'
        todayDate = datetime.datetime.now().date()

        for i, row in enumerate(sheet1_data):
            # find email in google sheet
            if row[str(todayDate)] == 'A':
                # user is absent
                messageToSend += f"\n{row['Name']} - {row['Angel']}"
                print(f"{row['Name']} is absent")
            else:
                # user is present
                print(f"{row['Name']} is present")
                
        #send message on whatsapp
        sendToWhatsapp(messageToSend)
    except Exception as e:
        print(f"error {e}")


@app.errorhandler(Exception)
def all_exception_handler(error):
    return 'Internal Error', 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5982)
