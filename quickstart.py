from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload
from google_drive_downloader import GoogleDriveDownloader as gdd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    imageFolder = None
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            if item['name'] == "Pola_Images":
                imageFolder = item
                break 
        
        print(u'{0} ({1})'.format(imageFolder['name'], imageFolder['id']))
        page_token = None
        while True:
            response = service.files().list(q="'"+(str(imageFolder['id']) + "' in parents"), spaces='drive',fields='nextPageToken, files(id, name)',pageToken=page_token).execute()
            images = response.get('files', [])
            for file in images:
                # Process change
                print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
            
        print(images)
        
        
        file_id = '1HAnRK_hDxEZvjfP9pZAUaSc9bEXuaFRO'
        request = service.files().get_media(fileId=images[1]['id'])
        fh = io.FileIO("Img/"+images[1]['name'], 'wb') 
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))
            print(fh)
          
if __name__ == '__main__':
    main()
    
    
    
    