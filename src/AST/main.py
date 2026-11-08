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
uwu:str="uwu"

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






async def websocket_loop(server:str,port:str|int,settings_dict:dict) -> None:
    port=str(port)
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
                                    if settings_dict["SplitOnAllGoals"]:
                                        if dictitem["team"] == team: #coppy paste job
                                            if settings_dict["speedrunType"] == "OSR": #linux
                                                timer_connectors.send_osr_command("split",
                                                                                  settings_dict["openSpeedrunSocket"])
                                            else:#windows
                                                timer_connectors.send_livesplit_command("split",settings_dict["livesplitHost"],int(settings_dict["livesplitPort"]))
                                    else:
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

def config_lsp_menu(json_settings:dict)-> None:
    while True:
        clear_screen()
        setting: str = input("input what Livesplit port you are using. this must be a number. type E to go back :")
        if setting == "e":
            break
        try:
            int(setting)
            settings.save_setting_to_json("livesplitPort", json_settings, setting)
            break
        except ValueError as error:
            print(f"the port has to be a number in string format.")

    config_menu()


def config_lss_menu(json_settings:dict)-> None:
    clear_screen()
    setting:str=input("Input the Live split server. type E to go back :").lower()
    if not setting=="e":
        settings.save_setting_to_json("livesplitHost",json_settings,setting)
    config_menu()

def config_osrs_menu(json_setting:dict)-> None:
    clear_screen()
    setting:str=input("Input where the open speedrun timer's socket resides. type E to go back :")
    if not setting=="e" or setting=="E":
        settings.save_setting_to_json("openSpeedrunSocket",json_setting,setting)
    config_menu()

def config_tt_menu(json_setting:dict) -> None:
    clear_screen()
    setting:str=input("Input which timer you are using. OSR or LiveSplit. type E to go back :").lower()
    match setting:
        case "osr":
            settings.save_setting_to_json("speedrunType",json_setting,"OSR")
        case "livesplit":
            settings.save_setting_to_json("speedrunType",json_setting,"LiveSplit")
        case _:
            ...
    config_menu()

def config_usr_menu(json_setting:dict) -> None:
    clear_screen()
    setting:str=input("input what slotname you are using. type E to go back :")
    if not setting=="e" or setting=="E":
        settings.save_setting_to_json("username",json_setting,setting)
    config_menu()

def config_pw_menu(json_settings:dict)-> None:
    clear_screen()
    setting:str=input("input what archipelago password you are using if any. type E to go back :")
    if not setting=="e" or setting=="E":
        settings.save_setting_to_json("password",json_settings,setting)
    config_menu()


def config_app_menu(json_settings:dict)-> None:
    while True:
        clear_screen()
        setting:str=input("input what archipelago port you are using. this must be a number. type E to go back :")
        if setting=="e":
            break
        try:
            int(setting)
            settings.save_setting_to_json("port",json_settings,setting)
            break
        except ValueError as error:
            print(f"the port has to be a number in string format.")

    config_menu()


def config_aps_menu(json_settings:dict)-> None:
    clear_screen()
    setting:str=input("input what archipelago server you are using. ie: archipelago.gg. type E to go back :").lower()
    if not setting=="e":
        settings.save_setting_to_json("server",json_settings,setting)
    config_menu()

def config_tst_swap(json_settings:dict)-> None:
    reverse_soag = not json_settings["SplitOnAllGoals"]
    settings.save_setting_to_json("SplitOnAllGoals", json_settings, reverse_soag)
    config_menu()

def config_menu() -> None:
    json_settings:dict=settings.load_json_settings()
    clear_screen()
    print(f"Type APS or APServer to change the archipelago server")
    print(f"Type APP or APPort to change the archipelago port")
    print(f"Type PW or Password to change the password")
    print(f"Type Usr or Username to change the username")
    print(f"Type TT or TimerType to change which timer your using")
    print(f"Type OSRS or OpenSpeedRunSocket to change the socket")
    print(f"Type LSS or LiveSplitServer to change the live split server")
    print(f"Type LSP or LiveSplitPort to change the live split port")
    print(f"Type tst or ToggleSplitType to change weather you split on single goal or on all goals of your team")
    print(f"Type E, or Exit to go back to the main menu")
    print(f"Type Q  or Quit to quit")
    command:str= input("input :").lower()

    match command:
        case "aps" | "apserver":
            config_aps_menu(json_settings)
        case "app" | "apport":
            config_app_menu(json_settings)
        case "pw" | "password":
            config_pw_menu(json_settings)
        case "usr" |"username":
            config_usr_menu(json_settings)
        case "tt" | "timertype":
            config_tt_menu(json_settings)
        case "osrs"| "openspeedrunsocket":
            config_osrs_menu(json_settings)
        case "lss" | "livesplitserver":
            config_lss_menu(json_settings)
        case "lsp" | "livesplitport":
            config_lsp_menu(json_settings)
        case "tst" | "togglesplittype":
            config_tst_swap(json_settings)

        case "e" | "exit":
            main_menu()
        case _:
            print("Goodbye")


def main_menu()-> None: #could totally use some need text scrolling effect but that is a lot of work for like no effort.
    clear_screen()
    print(f"Type S or Start to start the application server")
    print(f"Type C,Config, or Settings to go to the settings menu")
    print(f"Type Q or Quit to exit the application")
    command:str= input("input: ").lower()

    match command:
        case "s" | "start":
            start_server()
        case "c" | "config" | "settings":
            config_menu()
        case _:
            print("Goodbye")








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
    parser.add_argument("--livesplitPort",type=str,help="changes the livesplit port setting via the command line, needs to be a whole number")
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
                 if not value is None:
                     if key == 'port' or key == 'livesplitPort': #make shure the user actually inputted something reasonable as a port
                         #we dont want no 'fuck' as a port number
                         try:
                             int(value)
                             current_settings=settings.save_setting_to_json(key,current_settings,value)

                         except ValueError as error:
                             print(f"the port has to be a number in string format.")

                     else:
                         current_settings=settings.save_setting_to_json(key,current_settings,value)



    main_menu()#just so it doesnt break while testing.





if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Program Stopped via user.")
