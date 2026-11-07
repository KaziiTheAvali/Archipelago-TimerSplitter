import json
from pathlib import Path
from platformdirs import user_config_path
import special_types

class NonsupportedSetting(Exception):
    ...
class NoFileFound(Exception):
    ...


def load_json_settings(file_path: Path|None = None) -> dict:
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

def reload_json_settings(file_path: Path|None = None) -> dict:
    if file_path is None:
        base_file_path: Path = user_config_path(appname="Archipelago Speedrun Splitter", appauthor="Kazii")
        file_path = base_file_path / "connection.json"
    if not file_path.is_file():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    settings_dict:dict = special_types.settings_dict
    save_json_file(settings_dict,file_path)
    return settings_dict



def save_setting_to_json(setting: str,  json_data:dict, value:str, file_path: Path|None = None) -> dict:
    try:
        accepted_settings=json_data.keys()
        if file_path is None:
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
    except NoFileFound as error:
        print(error)


def save_json_file(json_dict:dict, file_path:Path) -> None:
    if not file_path.is_file():
        file_path.parent.mkdir(parents=True,exist_ok=True)
    with open(file_path,"w",encoding="utf_8") as file:
        json.dump(json_dict,file,indent=4)





def main() -> None:
    print(reload_json_settings())

if __name__ == '__main__':
    main()
