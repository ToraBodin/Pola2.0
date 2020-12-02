from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload



class APIconnection():
    """
    This class handles the API connection to the selected drive folder. 
    The easiset way to activate an API token is to run the quickstart.py program from your computer, 
    select the proper drive account and then add the generated token.pickle file to the Pola project folder. 
    If modifying the API SCOPe, te pickle needs to be deleted and re-generated. 
    """
    def __init__(self):
        self.service = None
        self.images = []
        self.folderID = ""
        
        
        self.setupConnection()
        
        self.mainFolder = "Pola2020"
        self.imageFolder = "Pola_Images"
        self.settingsFile = "PolaSettings.csv"
        
        
        
        
    def setupConnection(self):
        # If modifying these scopes, delete the file token.pickle.
        """Most probably, the reason why the upload (ex. for the log file) does 
        not work right now is because the scope needs to be updated"""
        
        SCOPES = ['https://www.googleapis.com/auth/drive']
              
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
       
        self.service = build('drive', 'v3', credentials=creds)
       
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        imageFolder = None
        if not items:
            print('No files found.')
        else:
            for item in items:
                if item['name'] == self.mainFolder:
                    self.folderID = item['id']
                    break         
        
        
    
    def updateImageNames(self):
        """
        Identify the image folder and get the names of all the files in the folder
        """
        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        imageFolder = None
        if not items:
            print('No files found.')
        else:
            for item in items:
                if item['name'] == self.imageFolder:
                    imageFolder = item
                    break 
            
            page_token = None
            while True:
                response = self.service.files().list(q="'"+(str(imageFolder['id']) + "' in parents"), spaces='drive',fields='nextPageToken, files(id, name)',pageToken=page_token).execute()
                self.images = response.get('files', [])
                #for file in images:
                    # Process change
                    #print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
                
        return self.images
                
          
    
    def downloadImage(self, index):
        """
        Download the next image in the image queue
        """
        currentImage = self.images[index]
        request = self.service.files().get_media(fileId=currentImage['id'])
        fh = io.FileIO("Img/"+currentImage['name'], 'wb') 
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))
            print('fh',fh)
        return currentImage['name'] 
    
    
    def getSettings(self, filename):
        """
        Download the settings file
        """
        """
        The setting ID is currently static for Tora's settings doc. Make it so that it goes by name instead! 
        """
        request = self.service.files().get_media(fileId="17TaO0KkdNBM7vzLdfsolKzNlMggbHmQu")
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))
            print('fh',fh)
        return True


    def sendLogfile(self, filename):
        """
        Upload the log file
        THIS DOES NOT WORK
        """
        file_metadata = {'name': filename,  'parents': self.folderID}
        media = MediaFileUpload(filename, mimetype='csv')
        file = self.service.files().create(body=file_metadata,media_body=media,fields='id').execute()
         
    
    
    