from websockets.client import ClientConnection

import settings
import special_types
import asyncio
import websockets
import uuid
import argparse
import json


def make_connection_packet(player_uuid:str,name:str,websocket:ClientConnection,password:str|None=None) -> str:
    version:dict=special_types.version
    items_handling:int=0b011
    tags:list[str]=["Tracker","Autosplitter"]
    slot_data:bool=True
    if password is None:
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

def make_empty_datapackage() -> str:
    datapackages:list[str]=[""]
    datapackage:list=[{"cmd": "GetDataPackage","games":datapackages}]

    return json.dumps(datapackage)






async def websocket_loop(server:str,port:str,settings_dict:dict) -> None:
    full_uri:str="wss://" + server +":"+ port
    player_uuid=uuid.uuid4()
    continuous:bool=True
    connected:bool=False
    step:int=0
    slot:int
    team:int
    while True:
        try:
            async with websockets.connect(full_uri) as websocket:

                async for message in websocket:
                    print(f"Message= {message}")
                    data:list = json.loads(message)
                    for dictitem in data:
                        if dictitem["cmd"] == "RoomInfo":
                            uuidstr = str(player_uuid)
                            if dictitem["password"]:
                                connection_packet = make_connection_packet(uuidstr, settings_dict["username"], websocket,
                                                                           settings_dict["password"])
                            else:
                                connection_packet = make_connection_packet(uuidstr,
                                                                           settings_dict["username"], websocket,)
                            await websocket.send(connection_packet)
                            print(f"connection packet sent = {connection_packet}")
                        if dictitem["cmd"] == "Connected":
                            team=dictitem["team"]
                            slot=dictitem["slot"]

                        if dictitem["cmd"] == "PrintJSON":
                            if "type" in dictitem:
                                if dictitem["type"] == "Countdown":
                                        if dictitem["countdown"] == 0:
                                            ...
                                if dictitem["type"] == "Goal":
                                    if dictitem["team"] == team and dictitem["slot"] == slot:
                                        ...





        except (websockets.ConnectionClosedError, OSError) as e:
            print(f"Connection lost ({e}). Reconnecting in 3 seconds...")
            await asyncio.sleep(3)











def main() -> None:
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="A connector to speedrun timers livesplit and open speedrun")

    parser.add_argument("--autoconnect",type=bool,default=False,help="Has you autoconnect without going through the opening scripts. only use after seed has genned")
    parser.add_argument("--server",type=str,help="changes the server setting via the command line")
    parser.add_argument("--password",type=str,help="changes the password setting via the command line")
    parser.add_argument("--user",type=str,help="changes the username setting via the command line")
    parser.add_argument("--port",type=str,help="changes the port setting via the command line")
    parser.add_argument("--filePath",type=str,help="use a custom file path")

    args:argparse.Namespace = parser.parse_args()
#
    #if not args.count == 0:
    #    if args.autoconnect is True:
    #        settings_dict:dict=settings.load_json_settings()
    #        websocket_loop(settings_dict["server"],settings_dict["port"],settings_dict)
    #    else:
    #         ...
    try:
        settings_dict: dict = settings.load_json_settings()
        asyncio.run(websocket_loop(settings_dict["server"], settings_dict["port"], settings_dict))
    except KeyboardInterrupt:
        print("Client stopped by user")




if __name__ == '__main__':
    main()
