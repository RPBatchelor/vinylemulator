import time
import nfc
import requests
import uuid
import appsettings #you shouldnt need to edit this file
import usersettings #this is the file you might need to edit
import secrets #edit this with Spotify developer credentials. Hidden in .gitignore
import sys
import ndef

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import difflib


def find_uri_from_spotify(album, artist):
   print("Looking up album " + str(album) + " by artist " + str(artist)) 
   sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(secrets.spotipy_client_id, secrets.spotipy_client_secret))
   results = sp.search('album:' + str(album) + " artist:" + str(artist), type="album")
   albums = results['albums']['items']
   items = {a['name']:a['uri'] for a in albums}
   elem = difflib.get_close_matches(album, items.keys(), 1)[0]
   uri = items[elem]
   return uri

def find_current_album():
   url = "/".join((usersettings.sonos_http_address, usersettings.sonos_room, "state"))
   response = requests.get(url)
   items = response.json()
   return items['currentTrack']['album'], items['currentTrack']['artist']

def write_current_album(tag):
   res = find_current_album()
   if not res:
      print("No album found")
      return False

   album, artist = res
   print('Current album ' + str(album) + "by artist " + str(artist)) 
   uri = find_uri_from_spotify(album, artist)

   print('URI is '+ str(uri))

   print("Formatting tag")
   tag.format()

   print("Tag Formatted " + str(tag))
   record = ndef.TextRecord(uri)
   tag.ndef.records = [record]
 
   print("Finished writing NDEF")  

   say_command = "Finished creating tag for artist %s and album %s" % (artist, album)
   url = "/".join((usersettings.sonos_http_address,usersettings.sonos_room, "say",say_command))
   requests.get(url)
   return True 


def touched(tag):
    read_mode = tag.ndef and tag.ndef.records
    if read_mode:
        print('Received ' + str(len(tag.ndef.records)) + ' records')
        for record in tag.ndef.records:
            received_text = record.text

            print("Read from NFC tag: " + received_text)

            service_type = ""

            # Check if full HTTP URL read from NFC
            if received_text_lower.startswith('http'):
                service_type = "completeurl"
                sonos_instruction = received_text
            
            if received_text_lower.startswith('spotify'):
                service_type = "spotify"
                sonos_instruction = "spotify/now/" + received_text
            
            if received_text_lower.startswith('tunein'):
                service_type = "tuneine"
                sonos_instruction = received_text
            
            # Check if Sonos "command" or room change read from NFC
            if received_text_lower.startswith('command'):
                service_type = "command"
                sonos_instruction = received_text[8:]

            if service_type == "":
                print("Service type not recognised. NFC tag text should begin with spotify, tunein, command or room.")
                return True
            
            print("Detected " + service_type + " service request")

            url_to_get = usersettings.sonos_http_address + "/" + usersettings.sonos_room + "/" + sonos_instruction

            # Clear the queue for every service request type except commands
            if service_type != "command":
                print("Clearing the Sonos queue")
                r = requests.get(usersettings.sonos_http_address + "/" + sonos_room_local + "/clearqueue")

            # Use the request function to get the URL built previously, triggering the sonos
            print("Fetching URL via HTTP: " + url_to_get)
            r = requests.get(url_to_get)
            print("")
    else:
        print("Tag Blank - trying to format/write")
        write_current_album(tag)
    
    return True

def connect_to_reader():
    print("Connecting to NFC reader...")
    try:
        reader = nfc.ContaclessFrontend(usersettings.nfc_reader_path)
    except IOError as e:
        print('''... could not connect to reader.

        You should check that the reader is working by running the following command:
        > python -m nfcpy

        If this reports that the reader is in use by readnfc or otherwise crashes out then make sure you don't already have read nfc running in the background via pm2. You can do this by running:
        > pm2 status        (this will show you whether it is running)
        > pm2 stop readnfc  (this will allow you to stop it so you can run the script manually)

        If you want to remove readnfc from running at startup then you can do it with:
        > pm2 delete readnfc
        > pm2 save
        > sudo reboot
        ''')
        sys.exit()
    print("Ready! Connected to " + str(reader))
    print("")
    return reader         
 


# Initialise the reader
print("")
print("Reading and checking readnfc")
print("")
print("Script;")
print("You are running version " + appsettings.appversion + "...")

print("")
print("NFC reader:")
connect_to_reader()

print("")
print("Sonos API:")
sonos_api_connection()

old_response = ""

while True:
    response = reader.connect(rdrw={'on-connect' : touched, "beep-on-connect": False})
    if response:
        r = requests.get(usersettings.sonos_http_address + "/" + usersettings.sonos_room + "/playpause")
    else:
        r = requests.get(usersettings.sonos_http_address + "/" + usersettings.sonos_room + "/pause")
    break

    time.sleep(0.1);
