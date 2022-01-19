import flask
from flask import request

import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

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
        spreadsheet = client.open_by_key('1BxrOnp_RHHjhMAOhFnLyo4qQQ8aSFG2_MPlESqWuPWw')
        sheet1 = spreadsheet.worksheet("Sheet1")
        sheet1_data = sheet1.get_all_records()

        for i, row in enumerate(sheet1_data):
            #find email in google sheet
            if row['Email'] == email:
                #mark attendance
                sheet1.update_cell(i+2 , 3, 'P')
            else:
                print(f"{row['Email']} not found")

    except:
        print("Exception thrown. x does not exist.")


@app.route('/hello-world', methods=['GET'])
def hello_world():
    return "Hello World"


@app.route('/zoom', methods=['GET', 'POST'])
def log_attendence():
    data = request.json

    obj = data['payload']['object']
    user = obj['participant']

    if data['event'] == 'meeting.participant_joined':
        try:
            updateAttendence(user['email'])
        except:
            return "failed ", 400

    return "Ok", 200


#function- getAbsentUsers()
# get name and angel name

#cronjob
#every 1 minute call getAbsentUsers() and send message on Whatsapp useing POST req



# @app.errorhandler(Exception)
# def all_exception_handler(error):
#     return 'Internal Error', 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
