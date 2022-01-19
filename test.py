import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

scope = [ 'https://www.googleapis.com/auth/spreadsheets']

# Assign credentials ann path of style sheet
credentials = Credentials.from_service_account_file(
    'creds.json',
    scopes=scope
)
client = gspread.authorize(credentials)

spreadsheet  = client.open_by_key('1BxrOnp_RHHjhMAOhFnLyo4qQQ8aSFG2_MPlESqWuPWw')
sheet1 = spreadsheet.worksheet("Sheet1")

print(sheet1.get_all_records())