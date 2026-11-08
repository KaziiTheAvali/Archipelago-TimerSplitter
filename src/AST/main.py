import ssl
import subprocess
import sys

from websockets.client import ClientConnection #this was an auto import. probably not needed. thanks fucking pycharm

import settings
import special_types
import timer_connectors

import asyncio
import websockets
import uuid
import argparse
import json
import os


def make_connection_packet(player_uuid:str,name:str,password:str|None=None) -> str: #this makes the package that is sent to the server when connecting
    version:dict=special_types.version #gets the version from specal_types. that file name should be changed because its not really types but shh
    items_handling:int=0b011 #reseves items. probably could be 0b000
    tags:list[str]=["Tracker","Autosplitter"] #tracker removes the game check.
    slot_data:bool=True #unused. will remove later if i rember
    if password is None: #check if the password is None which means that the server does not need a password
        connection_packet: list = [
            {"cmd": "Connect",
             "game": "",
             "password":"",
             "name": name,
             "uuid": player_uuid,
             "version": version,
             "tags": tags,
             "items_handling":items_handling,
             "slot_data":True
            }
            ]
    else:
        connection_packet: list = [
            {"cmd": "Connect",
             "game": "",
             "password": password,
             "name": name,
             "uuid": player_uuid,
             "version": version,
             "tags": tags,
             "items_handling": items_handling,
             "slot_data": True
             }
        ]

    return  json.dumps(connection_packet)

def make_empty_datapackage() -> str: #unused atm.
    datapackages:list[str]=[""]
    datapackage:list=[{"cmd": "GetDataPackage","games":datapackages}]

    return json.dumps(datapackage)






async def websocket_loop(server:str,port:str,settings_dict:dict) -> None:
    full_uri:str="wss://" + server +":"+ port #default is secure.
    player_uuid=uuid.uuid4() #i never knew what the intended uuid thing was so just gen this shit
    secure:bool=True
    slot:int#will be filled with the actual slot and team number
    team:int
    while True:
        try:
            print(f"trying to connect with {full_uri}")
            async with websockets.connect(full_uri) as websocket:
                #connected!
                async for message in websocket: #checks for messages that are sent.
                    print(f"Message= {message}") #dev shit. will remove later
                    data:list = json.loads(message) #this just makes it useable
                    for dictitem in data:
                        if dictitem["cmd"] == "RoomInfo": #waiting for the first message. this is required to actually connect
                            uuidstr = str(player_uuid)
                            if dictitem["password"]:
                                connection_packet:str = make_connection_packet(uuidstr, settings_dict["username"],
                                                                           settings_dict["password"])
                            else:
                                connection_packet:str = make_connection_packet(uuidstr,
                                                                           settings_dict["username"],)
                            await websocket.send(connection_packet)
                            print(f"connection packet sent = {connection_packet}")
                        if dictitem["cmd"] == "Connected": #hey i am actually connected everything is good!. get the team and slot numbers and put them in
                            team=dictitem["team"]
                            slot=dictitem["slot"]

                        if dictitem["cmd"] == "PrintJSON": #the server sends printjson for the majority of stuff. all the things i need is here
                            if "type" in dictitem:
                                if dictitem["type"] == "Countdown": #check for the countdown
                                        if dictitem["countdown"] == 0: #checks if it is 0 (will for some reason error if it is with the other when type is not equal to countdown)
                                            if settings_dict["speedrunType"] == "OSR": #the linux side of things
                                                timer_connectors.send_osr_command("start",
                                                                                  settings_dict["openSpeedrunSocket"])
                                            else:
                                                timer_connectors.send_livesplit_command("starttimer", #the windows side of things
                                                                                        settings_dict["livesplitHost"],
                                                                                        int(settings_dict[
                                                                                                "livesplitPort"]))
                                if dictitem["type"] == "Goal": #checks if someone has goaled
                                    if dictitem["team"] == team and dictitem["slot"] == slot: #checks the team and slot. yet again errors if this isnt the goal type
                                        if settings_dict["speedrunType"] == "OSR": #linux
                                            timer_connectors.send_osr_command("split",
                                                                              settings_dict["openSpeedrunSocket"])
                                        else:#windows
                                            timer_connectors.send_livesplit_command("split",settings_dict["livesplitHost"],int(settings_dict["livesplitPort"]))





        except ssl.SSLError as error:
            if "WRONG_VERSION_NUMBER" in str(error):
                #allows testing bolth the ws(unsecure) and wss (secure) websocket connection.
                if secure:
                    full_uri: str = "ws://" + server + ":" + port
                    secure=False
                else:
                    full_uri: str = "wss://" + server + ":" + port
                    secure = True
        except (websockets.ConnectionClosedError, OSError) as error:

            print(f"Connection lost ({error}). Reconnecting in 3 seconds...")# my capitilization consistancy is horrendous
            await asyncio.sleep(3)


def start_server() -> None:
    settings_dict: dict = settings.load_json_settings()
    asyncio.run(websocket_loop(settings_dict["server"], settings_dict["port"], settings_dict))

def clear_screen() -> None:
    if os.name=='nt':
        subprocess.run('cls')
    else:
        subprocess.run('clear')


def main_menu()-> None:
    ...





def main() -> None:
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="A connector to speedrun timers livesplit and open speedrun")

    parser.add_argument("--autoconnect",type=bool,default=False,help="Has you autoconnect without going through the opening scripts. only use after seed has genned")
    parser.add_argument("--server",type=str,help="changes the server setting via the command line")
    parser.add_argument("--password",type=str,help="changes the password setting via the command line")
    parser.add_argument("--user",type=str,help="changes the username setting via the command line")
    parser.add_argument("--port",type=str,help="changes the port setting via the command line. must be a whole number in string format")
    #parser.add_argument("--filePath",type=str,help="use a custom file path") currently unused. unshure how to impliment it well.
    parser.add_argument("--splitterType",type=str, help="changes the setting via command line. use OSR for open speedrun or LiveSplit for linux")
    parser.add_argument("--OSRSocket",type=str, help="changes the socket path via command line")
    parser.add_argument("--livesplitHost",type=str,help="changes the livesplit host name setting via command line")
    parser.add_argument("--livesplitPort",type=str,help="changes the livesplit port setting via the command line, needs to be a whole number in string format")
    #no version argument because you can not manually change the version


    args:argparse.Namespace = parser.parse_args() #avrage arg parser section/

    current_settings:dict = settings.load_json_settings()

    if not current_settings["SettingsVersion"] == special_types.settings_dict["SettingsVersion"]:
        current_settings=settings.update_json_settings(current_settings)
        print("settings update has been added")


    if not len(sys.argv) == 1:#if there is not args you can just go straight to the (eventual) cli menu
        if args.autoconnect is True:
            start_server() #this skips everything.
        else:
             for key, value in vars(args).items():
                 print(f"key = {key}, value = {value}")
                 if not value == None:
                     if key == 'port' or key == 'livesplitPort': #make shure the user actually inputted something reasonable as a port
                         #we dont want no 'fuck' as a port number
                         try:
                             int(value)
                             current_settings=settings.save_setting_to_json(key,current_settings,value)

                         except ValueError as error:
                             print(f"the port has to be a number in string format.")

                     else
                         current_settings=settings.save_setting_to_json(key,current_settings,value)



    start_server()#just so it doesnt break while testing.





if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Program Stopped via user.")
