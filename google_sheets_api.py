import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheets():
    def __init__(self,workbook):
        self.credentials = 'keys/golden-operator-313523-5c874249f8e9.json'
        self.workbook = workbook
    def export_google_sheet(self,df,sheet_number):
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
        # Add your service account file
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials, scope)
        # Authorize the clientsheet 
        client = gspread.authorize(creds)
        # Get the instance of the Spreadsheet
        sheet = client.open(self.workbook)
        # Get the first sheet of the Spreadsheet
        sheet_instance = sheet.get_worksheet(sheet_number)
        sheet_instance.clear()
    # Export the DataFrame to Google Sheets
        set_with_dataframe(worksheet=sheet_instance,dataframe=df,include_index=False, include_column_header=True, resize=True)
