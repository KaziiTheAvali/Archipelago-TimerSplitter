import json
from pathlib import Path
from platformdirs import user_config_path
import special_types

class NonsupportedSetting(Exception):
    ...
class NoFileFound(Exception):
    ...


def load_json_settings(file_path: Path|None = None) -> dict: #loads the settings from a json file
    if file_path is None:
        base_file_path: Path = user_config_path(appname="Archipelago Speedrun Splitter", appauthor="Kazii")
        file_path = base_file_path / "connection.json"

    if not file_path.is_file():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        settings_dict:dict = special_types.settings_dict
        save_json_file(settings_dict,file_path)
        return settings_dict
    with open(file_path, "r") as file:
        settings_dict:dict = json.load(file)
    return settings_dict

def reload_json_settings(file_path: Path|None = None) -> dict: #reloads the settings to factory dfault
    if file_path is None:
        base_file_path: Path = user_config_path(appname="Archipelago Speedrun Splitter", appauthor="Kazii")
        file_path = base_file_path / "connection.json"
    if not file_path.is_file():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    settings_dict:dict = special_types.settings_dict
    save_json_file(settings_dict,file_path)
    return settings_dict

def update_json_settings(json_data:dict, file_path: Path|None = None) -> dict: #updates the settings when everything changes while keeping previous settings
    default_settings:dict = special_types.settings_dict #defaults

    new_settings_dict:dict = {}

    for key in default_settings: #go through making shure all of the keys are in there. if there is not one then put it in.
        if key in json_data:
            new_settings_dict[key] = json_data[key]
        else:
            new_settings_dict[key] = default_settings[key]
    new_settings_dict['SettingsVersion']=default_settings['SettingsVersion']#update the version.
    if file_path is None:
        base_file_path: Path = user_config_path(appname="Archipelago Speedrun Splitter", appauthor="Kazii")
        file_path = base_file_path / "connection.json"
    save_json_file(new_settings_dict,file_path)
    return new_settings_dict




def save_setting_to_json(setting: str,  json_data:dict, value:str, file_path: Path|None = None) -> dict: #saves a single setting.
    try:
        accepted_settings=special_types.settings_dict.keys() #the accepted settings. cant figure out how to static type this :(
                                                             #unshure why i did it this way. like im pritty shure you can just check normally but ohwell
        if file_path is None:#make the file
            base_file_path: Path = user_config_path(appname="Archipelago Speedrun Splitter", appauthor="Kazii")
            file_path = base_file_path / "connection.json"
        if setting in accepted_settings:
            new_json_data:dict = json_data
            new_json_data[setting]=value
            save_json_file(new_json_data,file_path)
            return new_json_data
        else :
            print(f"The setting {setting} is not found. please make shure it is a valid setting from the following:"
                  f" {accepted_settings}.")
        return json_data
    except NoFileFound as error:  #this should never trigger. was previously used.
        print(error)
        return json_data #added this to stop a warning.


def save_json_file(json_dict:dict, file_path:Path) -> None: #saves the json file
    if not file_path.is_file():
        file_path.parent.mkdir(parents=True,exist_ok=True)
    with open(file_path,"w",encoding="utf_8") as file:
        json.dump(json_dict,file,indent=4)





def main() -> None: #used for testing settings functions. should never run
    currrent_settings=load_json_settings()
    print(update_json_settings(currrent_settings))

if __name__ == '__main__':
    main()
