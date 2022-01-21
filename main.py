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
meeting_id = os.getenv('meeting_id')

sheetId = '1BxrOnp_RHHjhMAOhFnLyo4qQQ8aSFG2_MPlESqWuPWw'

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

        for i, row in enumerate(sheet1_data):
            # find email in google sheet
            if row['Email'] == email:
                # mark attendance
                sheet1.update_cell(i+2, 3, 'P')
                # get absent users
                getAbsentUser()
            else:
                print(f"{row['Email']} not found")

    except Exception as e:
        print(f"error {e}")


@app.route('/hello-world', methods=['GET'])
def hello_world():
    return "Hello World"


@app.route('/zoom', methods=['POST'])
def log_attendence():
    if(request.headers['authorization']=='Q7PG2W_NQyOgwTrIDEs7Lw'):
        try:
            data = request.json
            obj = data['payload']['object']
            user = obj['participant']
            zoomMeetinId=obj['id']
            if(zoomMeetinId==meeting_id):
                if data['event'] == 'meeting.participant_joined':
                    updateAttendence(user['email'])
        
        except Exception as e:
            print(f"error {e}")

        
    else:
        print('invalid headers')
    return "", 200

@app.route('/getAbsentUsers', methods=['GET'])
def getAbsentUserRoute():
    getAbsentUser()
    return "Ok", 200


def sendToWhatsapp(messageToSend):
    try:
        requests.post(whatsapp_api_url, data={
            "message": f"{messageToSend}", "chatJid": group_jid})
        print('message sent')
        return "OK"
    except Exception as e:
        print(f"error {e}")
        print("An exception occurred. unable to send message")
        print(messageToSend)
        return "Failed"


def getAbsentUser():
    try:
        spreadsheet = client.open_by_key(
            sheetId)
        sheet1 = spreadsheet.worksheet("Sheet1")
        sheet1_data = sheet1.get_all_records()

        messageToSend = '*yet to join*\n'
        todayDate = datetime.datetime.now().date()

        for i, row in enumerate(sheet1_data):
            # find email in google sheet
            if row[str(todayDate)] == 'A':
                # user is absent
                messageToSend += f"\n{row['Name']} - {row['Angel']}"
            else:
                # user is present
                print(f"{row['Name']} present")

        # send message on whatsapp
        sendToWhatsapp(messageToSend)
    except Exception as e:
        print(f"error {e}")


@app.errorhandler(Exception)
def all_exception_handler(error):
    return 'Internal Error', 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5982)
