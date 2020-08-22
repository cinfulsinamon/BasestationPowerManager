import asyncio
import configparser
import bleak
import os
import sys
import time
import pywinusb.hid as hid

BS_CMD_BLE_ID = "0000cb01-0000-1000-8000-00805f9b34fb"
BS_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"
BS_UNIQUE_ID = "0xFFFFFFFF"
HS_VENDOR_ID = "0x0000"

loop = asyncio.get_event_loop()
 
def make_config():
    global BS_MAC_ADDRESS, BS_UNIQUE_ID, HS_VENDOR_ID
    
    defConfig = open("bsinfo.ini", "w")
    defConfig.write("[BaseStation]")
    defConfig.write("\nB_MAC_ADDRESS = " + BS_MAC_ADDRESS)
    defConfig.write("\nB_UNIQUE_ID = " + BS_UNIQUE_ID)
    defConfig.write("\n")
    defConfig.write("\n[HeadSet]")
    defConfig.write("\nUSB_VENDOR_ID = " + HS_VENDOR_ID)
    defConfig.close()
    
def load_configuration():
    config = configparser.ConfigParser()
    config.read('bsinfo.ini')
    global BS_MAC_ADDRESS, BS_UNIQUE_ID, HS_VENDOR_ID
    BS_MAC_ADDRESS = config['BaseStation']['B_MAC_ADDRESS']
    BS_UNIQUE_ID = config['BaseStation']['B_UNIQUE_ID']
    HS_VENDOR_ID = config['HeadSet']['USB_VENDOR_ID']
    
def get_BS_b():
    global BS_UNIQUE_ID, BS_MAC_ADDRESS
    BS_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"
    BS_UNIQUE_ID = "0xFFFFFFFF"
    
    print("Please enter the ID of the base station set to channel B.")
    print("This can be found on the back of the base station, near the bottom edge of the label.")
    print("It should be 8 characters, using only 0-9 or a-z, case-insensitive.")
    print("NOTE: Only the last 4 characters are checked to find the MAC address, but if the first 4 are wrong then they can't be set to power on with a timeout.")
    while BS_UNIQUE_ID == "0xFFFFFFFF":
        tempID = input("ID: ").upper()
        if len(tempID) == 8 and not any(c not in '0123456789ABCDEF' for c in tempID):
            BS_UNIQUE_ID = "0x" + tempID   
        else:
            print("\nInvalid ID. Enter a valid ID.")
            print("It should be 8 characters, using only 0-9 or a-f, case-insensitive.") 
    scanTries = 0
    while "X" in BS_MAC_ADDRESS and scanTries < 10:
        scan(tempID)
        scanTries += 1
    if scanTries < 10:
        make_config()
        print("Basestation information saved.")
    else:
        print("Error finding your base station after 10 attempts. Check your bluetooth device.")
    
def scan(bsID):
    bsList = loop.run_until_complete(get_BS_list())
    for base in bsList:
        print("Base station found:", base)
        if bsID[4:].casefold() in str(base).casefold():
            print("Base station B located. Saving MAC address: " + str(base)[:17])
            global BS_MAC_ADDRESS
            BS_MAC_ADDRESS = str(base)[:17]
            return
    print("Base station not found. Make sure your bluetooth is enabled.")
    
async def get_BS_list():
    devices = []
    try:
        scan = await bleak.discover()
        for bleDevice in scan:
            if "HTC BS" in str(bleDevice):
                devices.append(bleDevice)
    except:
        print("Exception while scanning BLE devices: " + str(sys.exc_info()[0])) 
    return devices
    
def get_HS_id():
    global HS_VENDOR_ID
    print("You can enter the USB Vendor ID for your headset here.")
    print("This will allow the script to skip the menu and simply keep the base stations running until the headset is unplugged.")
    print("You can use Device Manager to find this on Windows, or look it up online.")
    print("Enter the VID below, or leave the field blank to return to the menu.")
    print("Alternatively, enter 0000 to overwrite the current entry and disable the auto prompt.")
    tempVID = "0"
    while tempVID:
        tempVID = input("VID: ").upper()
        if not tempVID:
            return
        elif len(tempVID) == 4 and not any(c not in '0123456789ABCDEF' for c in tempVID):
            HS_VENDOR_ID = "0x" + tempVID
            make_config()
            print("Vendor ID saved.")
            return
        else:
            print("\nInvalid VID. VID should be 4 characters, using only 0-9 or a-f, case-insensitive.")
            
def print_menu():
    os.system('cls')
    print("\n ____                    _____ _        _   _                         ")
    print("|  _ \                  / ____| |      | | (_)                          ")
    print("| |_) | __ _ ___  ___  | (___ | |_ __ _| |_ _  ___  _ __                ")
    print("|  _ < / _` / __|/ _ \  \___ \| __/ _` | __| |/ _ \| '_ \               ")
    print("| |_) | (_| \__ \  __/  ____) | || (_| | |_| | (_) | | | |              ")
    print("|____/ \__,_|___/\___| |_____/ \__\__,_|\__|_|\___/|_| |_|              ")
    print("|  __ \                       |  \/  |                                  ")
    print("| |__) |____      _____ _ __  | \  / | __ _ _ __   __ _  __ _  ___ _ __ ")
    print("|  ___/ _ \ \ /\ / / _ \ '__| | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|")
    print("| |  | (_) \ V  V /  __/ |    | |  | | (_| | | | | (_| | (_| |  __/ |   ")
    print("|_|   \___/ \_/\_/ \___|_|    |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   ")
    print("                                                         __/ |          ")
    print("                                                       |___/            ")
    print("\nCurrent paired base station:")
    print("MAC Address: " + BS_MAC_ADDRESS)
    print("Unique ID: " + BS_UNIQUE_ID[2:])
    if HS_VENDOR_ID != "0x0000":
        print ("\nHeadset VID: " + HS_VENDOR_ID)
    print("\n\nSelect an option:")
    print("\n1: Choose new base station B")
    print("2: Enter Headset Vendor ID")
    print("3: Power on base stations (no timeout)")
    print("4: Power on base stations (specified timeout)")
    print("5: Power off base stations")
    print("6: Exit the script")
    
def get_selection():
    switcher = {
        0: print_menu,
        1: get_BS_b,
        2: get_HS_id,
        3: wakeBS,
        4: wakeBS_timeout,
        5: sleepBS,
        6: sys.exit,
    }
    selection = input("[1-6]: ")
    if not selection or int(selection) > 6 or int(selection) < 1:
        print("Invalid selection. Please try again.\n")
    else:
        func = switcher.get(int(selection),0)
        print("")
        func()
        input("\n\nPress enter to continue...")
    
def wakeBS():
    print("This will wake your base stations with no timeout.")
    print("Any base stations set to C or A should automatically wake within 30 seconds of B waking up.")
    print("They will remain on unless they can't find B for a while.")
    print("B will remain on until you send a power off command.")
    while True:
        cont = input("Continue? (y/n): ")
        if cont == "y":
            print("Waking up base station...")
            cmd = make_cmd(0x00,0)
            loop.run_until_complete(send_cmd(cmd))
            print("Basestation awake.")
            return
        elif cont == "n":
            return
    
def wakeBS_timeout():
    print("This will wake your base station with an established timeout.")
    print("The script will then loop, pinging the base station before the timeout expires to extend it.")
    print("If you close the script or lose bluetooth connectivity, it will shut off automatically.")
    print("You may alternatively press CTRL+C to exit this loop.")
    while True:
        cont = input("Continue? (y/n): ")
        if cont == "y":
            while True:
                print("Choose a timeout. 30 seconds should be fine, set it longer if you have issues with them turning off between successful pings.")
                timeout = input("Enter a timeout length in seconds [10-60]: ")
                if not timeout or int(timeout) > 60 or int(timeout) < 10:
                    print("Invalid timeout length.\n")
                else:    
                    cmd = make_cmd(0x02,int(timeout))
                    pingloop = True
                    while pingloop:
                        try:
                            print("Ping base station...")
                            result = loop.run_until_complete(send_cmd(cmd))
                            if not result:
                                raise Exception("Could not ping base station.")
                            print("Sleep for " + str(int(timeout)/2) + " seconds")
                            time.sleep(int(timeout)/2)
                        except KeyboardInterrupt:
                            print("Exiting loop. Wait a second...")
                            pingloop = False
                        except:
                            print("Pinging base station failed. Check your bluetooth settings.")
                            sys.exit(1)
                    return
        elif cont == "n":
            return
    
def sleepBS():
    print("This will send a command to put your base station to sleep.")
    print("The base station should power off within a few second after recieving the command.")
    print("Any paired A or C base stations should power off when they are unable to find a B station.")
    while True:
        cont = input("Continue? (y/n): ")
        if cont == "y":
            cmd = make_cmd(0x02,1)
            loop.run_until_complete(send_cmd(cmd))
            return
        elif cont == "n":
            return
    
def make_cmd(cmd_id,cmd_timeout):
    ba = bytearray()
    ba += (0x12).to_bytes(1, 'big')
    ba += cmd_id.to_bytes(1, 'big')
    ba += (cmd_timeout).to_bytes(2, 'big')
    ba += int(BS_UNIQUE_ID,0).to_bytes(4, byteorder='little')
    ba += (0).to_bytes(12, byteorder='big')
    return ba
    
async def send_cmd(cmd):
    tries = 0
    while tries < 10:
        try:
            async with bleak.BleakClient(BS_MAC_ADDRESS, loop=loop) as client:
                await client.write_gatt_char(BS_CMD_BLE_ID, cmd)
            print("Command recieved.")
            return True
        except:
            print("Error sending command: " + str(sys.exc_info()[0]))
            tries += 1
        if tries == 10:
            print("Unable to contact base station. Check your bluetooth settings, and ensure your basestation unique ID is correct.")
            return False
    
def ask_auto():
    all_devices = hid.HidDeviceFilter(vendor_id = int(HS_VENDOR_ID,0)).get_devices()
    if not all_devices:
        print("No USB device found with saved VID. Check that your headset is plugged in and rerun for auto mode.")
        print("Moving to menu in 5 seconds...")
        time.sleep(5)
        return
    print("This script can automatically loop and keep your base station powered on until your headset is unplugged.")
    print("It will check for any device connected with the Vendor ID of " + HS_VENDOR_ID + ", so check that only your headset or its sensors are in the below list: \n")
    for device in all_devices:
        print(device)
    while True:
        cont = input("\nEnter auto mode? (y/n): ")
        if cont == "y":
            pings = 0
            cmd = make_cmd(0x02,30)
            autoloop = True
            while autoloop:
                try:
                    print("Now in auto mode. Press CTRL+C to exit. Number of pings: ", pings)
                    loop.run_until_complete(send_cmd(cmd))
                    pings += 1
                    time.sleep(15)
                    all_devices = hid.HidDeviceFilter(vendor_id = int(HS_VENDOR_ID,0)).get_devices()
                    if not all_devices:
                        autoloop = False
                except KeyboardInterrupt:
                    print("Stopping loop & shutting down base stations.")
                    time.sleep(10)
                    autoloop = False
            cmd = make_cmd(0x02,1)
            loop.run_until_complete(send_cmd(cmd))
            print("Sleep command sent. Your B base station should shut off immediately, and any others will be of within 30 seconds.")
            print("This script will exit in 5 seconds.")
            time.sleep(5)
            sys.exit(0)
        elif cont == "n":
            return

if __name__ == '__main__':
    print("Welcome to the BaseStation Power Manager script.")
    if os.path.exists("bsinfo.ini"):
        print("Config file found. Checking for base station info..")
        load_configuration()
        if "X" not in BS_MAC_ADDRESS:
            print("Basestation info found.")
        else:
            print("No base station info found.")
            get_BS_b()
            input("\n\nPress enter to continue...")
    else:
        print("No config file found. Generating one.")
        make_config()
        get_BS_b()
        input("\n\nPress enter to continue...")
    if HS_VENDOR_ID != "0x0000":
        ask_auto()
    while True:
        print_menu()
        get_selection()