import time
import nfc
import requests
import uuid
import appsettings #you shouldnt need to edit this file
import usersettings #this is the file you might need to edit
import sys

def read_tag(tag):
    global sonos_room_local

    if tag.ndef:
        for record in tag.ndef.records:
            try:
                received_text = record.text
            except:
                print("Error reading a *TEXT* tag from NFC.")
                return True
            
            received_text_lower = received_text.lower()

            print("")
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
                service_type "command"
                sonos_instruction = received_text[8:]
            
            if received_text_lower.startswith('room'):
                service_type = "room"
                sonos_room_local = received_text[5:]
                print("Sonos room changed to " + sonos_room_local)
                return True
            
            if service_type == "":
                print("Service type not recognised. NFC tag text should begin with spotify, tunein, command or room.")
            
            print("Detected " + service_type + " service request.")

            # Build the URL we want to request to Sonos local
            if service_type.lower() == 'completeurl':
                url_to_get = sonos_instruction
            else:
                url_to_get = usersettings.sonos_http_address + "/" + sonos_room_local + "/" + sonos_instruction

            # Check sonos
            check_sonos_api()

            # Clear the queue for every service request type except commands
            if service_type != "command":
                print("Clearing the Sonos queue")
                r = requests.get(usersettings.sonos_http_address + "/" + sonos_room_local + "/clearqueue")





def check_sonos_api():
    try:
        r = requests.get(usersettings.sonos_http_address)
    except:
        print("Failed to connect to Sonos API at " + usersettings.sonos_http_address)
        return True
    



            
            #check Sonos API is responding
            try:
                r = requests.get(usersettings.sonoshttpaddress)
            except:
                print ("Failed to connect to Sonos API at " + usersettings.sonoshttpaddress)
                return True

            #clear the queue for every service request type except commands
            if servicetype != "command":
                print ("Clearing Sonos queue")
                r = requests.get(usersettings.sonoshttpaddress + "/" + sonosroom_local + "/clearqueue")

            #use the request function to get the URL built previously, triggering the sonos
            print ("Fetching URL via HTTP: "+ urltoget)
            r = requests.get(urltoget)

            if r.status_code != 200:
                print ("Error code returned from Sonos API")
                return True
            
            print ("Sonos API reports " + r.json()['status'])

            #put together log data and send (if given permission)
            if usersettings.sendanonymoususagestatistics == "yes":
                logdata = {
                'time': time.time(),
                'value1': appsettings.appversion,
                'value2': hex(uuid.getnode()),
                'actiontype': 'nfcread',
                'value3': receivedtext,
                'servicetype': servicetype,
                'urltoget': urltoget
                }
                r = requests.post(appsettings.usagestatsurl, data = logdata)

    else:
        print("")
        print ("NFC reader could not read tag. This can be because the reader didn't get a clear read of the card. If the issue persists then this is usually because (a) the tag is encoded (b) you are trying to use a mifare classic card, which is not supported or (c) you have tried to add data to the card which is not in text format. Please check the data on the card using NFC Tools on Windows or Mac.")
        if usersettings.sendanonymoususagestatistics == "yes":
            r = requests.post(appsettings.usagestatsurl, data = {'time': time.time(), 'value1': appsettings.appversion, 'value2': hex(uuid.getnode()), 'value3': 'nfcreaderror'})

    return True

print("")
print("")
print("Loading and checking readnfc")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("")
print("SCRIPT")
print ("You are running version " + appsettings.appversion + "...")

print("")
print("NFC READER")
print("Connecting to NFC reader...")
try:
    reader = nfc.ContactlessFrontend(usersettings.nfc_reader_path)
except IOError as e:
    print ("... could not connect to reader")
    print ("")
    print ("You should check that the reader is working by running the following command at the command line:")
    print (">  python -m nfcpy")
    print ("")
    print ("If this reports that the reader is in use by readnfc or otherwise crashes out then make sure that you don't already have readnfc running in the background via pm2. You can do this by running:")
    print (">  pm2 status             (this will show you whether it is running)")
    print (">  pm2 stop readnfc       (this will allow you to stop it so you can run the script manually)")
    print ("")
    print ("If you want to remove readnfc from running at startup then you can do it with:")
    print (">  pm2 delete readnfc")
    print (">  pm2 save")
    print (">  sudo reboot")
    print ("")
    sys.exit()

print("... and connected to " + str(reader))

print ("")
print ("SONOS API")
sonosroom_local = usersettings.sonosroom
print ("API address set to " + usersettings.sonoshttpaddress)
print ("Sonos room set to " + sonosroom_local)

print ("Trying to connect to API ...")
try:
    r = requests.get(usersettings.sonoshttpaddress)
except:
    print ("... but API did not respond. This could be a temporary error so I won't quit, but carry on to see if it fixes itself")

if r.status_code == 200:
    print ("... and API responding")

print("")
print("OK, all ready! Present an NFC tag.")
print("")

if usersettings.sendanonymoususagestatistics == "yes":
    r = requests.post(appsettings.usagestatsurl, data = {'time': time.time(), 'value1': appsettings.appversion, 'value2': hex(uuid.getnode()), 'value3': 'appstart'})

while True:
    reader.connect(rdwr={'on-connect': touched, 'beep-on-connect': False})
    time.sleep(0.1);
