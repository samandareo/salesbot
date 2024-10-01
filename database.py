from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_service_account_file('files/credentials.json')
service = build('sheets', 'v4', credentials=creds)

spreadsheet_id = " " # spreadsheet_id for taking data from excel

def read_data(start_row=2):
    range_name = f'Sheet1!A{start_row}:B'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    return result.get('values', [])


# def remove_used_data():
#     range_name = f'Sheet1!A2:B'
#     service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_name).execute()

# def write_used_data():
#     range_name = f"Sheet1!A2:B"
#     range_name2 = f"Foydalanilgan!A2:B"
#     result = service.spreadsheets().values().get(
#             spreadsheetId=spreadsheet_id, range=range_name).execute()
#     values = result.get('values', [])
#     body = {
#         'values': values
#     }
#     service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name2,
#                                            valueInputOption='RAW', body=body).execute()





def move_specific_row():
    sheet = service.spreadsheets()
    
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range='Sheet1!A:B').execute()
    values = result.get('values', [])
    
    if not values:
        print('No data found.')
        return


    for i, row in enumerate(values[1:], start=2):
        if len(row) >= 2:
            body = {'values': [row]}
            sheet.values().append(spreadsheetId=spreadsheet_id,
                                  range='Foydalanilgan!A2:B',
                                  valueInputOption='USER_ENTERED',
                                  body=body).execute()
            
            sheet.values().clear(spreadsheetId=spreadsheet_id,
                                 range=f'Sheet1!A{i}:B{i}').execute()
            print(f"Moved successfully")
            request_body = {
                'requests': [
                    {
                        'deleteDimension': {
                            'range': {
                                'sheetId': 0,  # Adjust if 'Sheet1' is not the first sheet
                                'dimension': 'ROWS',
                                'startIndex': 1,  # Adjust index to 0-based
                                'endIndex': 2
                            }
                        }
                    }
                ]
            }
            sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=request_body).execute()
            break
        else:
            print("No data found.")
