import sys
import threading
import tkinter

import main as mainapp
import settings
import special_types

import tkinter as tk
from tkinter import ttk, Label
import json

class ConsoleRedirector:
    def __init__(self, console_box: tk.Text):
        self.console_box:tk.Text = console_box

        self.console_box.config(state="disabled")

    def write(self,string:str):
        self.console_box.after(0,self._append_text,string)

    def _append_text(self,string:str):
        self.console_box.config(state="normal")
        self.console_box.insert(tk.END, string)
        self.console_box.see(tk.END)
        self.console_box.config(state="disabled")

    def flush(self):
        ...

def launch_server(stoping_event:threading.Event):
    mainapp.start_server(stoping_event)

def number_only(input_text:str):
    return input_text.isdigit() or input_text == ""

def toggle_timer_boxes():
    ...
def reset_settings():
    settings.reload_json_settings()

def save_settings():
    speedrun_type:str=chosen_timer.get()
    if speedrun_type=="Open Speed Run":
        speedrun_type="OSR"
    else:
        speedrun_type="LiveSplit"

    save_data:dict={
        "server":connection_fields[2].get(),
        "port":connection_fields[3].get(),
        "password":connection_fields[1].get(),
        "username":connection_fields[0].get(),
        "speedrunType":speedrun_type,
        "openSpeedrunSocket":timer_connection_fields[0].get(),
        "livesplitHost":timer_connection_fields[1].get(),
        "livesplitPort":timer_connection_fields[2].get(),
        "SplitOnAllGoals":split_on_all_goals_var.get(),
        "SettingsVersion":special_types.settings_dict["SettingsVersion"]
    }
    settings.save_json_file(save_data)

def start_server():
    save_settings()
    stop_event.clear()
    threading.Thread(target=launch_server, daemon=True,args=(stop_event,)).start()

def stop_server():
    print("stopping server")
    stop_event.set()


current_settings:dict=settings.load_json_settings()
if not current_settings["SettingsVersion"] == special_types.settings_dict["SettingsVersion"]:
    current_settings = settings.update_json_settings(current_settings)
app:tkinter.Tk = tk.Tk()
app.title("Archipelago Speedrun Splitter GUI")
app.geometry("500x500")

connection_frame_top: tkinter.Frame = tk.Frame(app)
connection_frame_top.columnconfigure(0,weight=1)
connection_frame_top.pack(fill="x",side="top",pady=(10,0),anchor="n")

check_number:str=app.register(number_only)
connection_labels:list[str] = ["Slotname","Password","Address","Port"]
current_connection_settings:list[str] = [current_settings["username"],current_settings["password"],current_settings["server"],current_settings["port"]]
app.rowconfigure(0,weight=1)

connection_fields:list[tkinter.Entry] = []

for i, text in enumerate(connection_labels):
    connection_frame_top.columnconfigure(i,weight=1)

    connection_frame: tkinter.Frame = tk.Frame(connection_frame_top)
    connection_frame.grid(row=0,column=i, padx=10, pady=10, sticky="new")
    connection_frame.columnconfigure(0 ,weight=1)

    connection_label:tkinter.Label = tk.Label(connection_frame, text=text, font=("Arial", 10, "bold"))
    connection_label.pack(anchor="w", pady=(0, 5))
    if text == "Port":
        connection_entry: tkinter.Entry = tk.Entry(connection_frame,validate="key",validatecommand=(check_number, "%P"))
    else:
        connection_entry:tkinter.Entry = tk.Entry(connection_frame)
    connection_entry.pack(fill="x")
    connection_entry.insert(0, current_connection_settings[i])
    connection_fields.append(connection_entry),

timer_options_result_frame:tkinter.Frame = tk.Frame(app)
timer_options_result_frame.pack(fill="x",side="top",pady=10,anchor="w")

timer_options:list[str] =["Open Speed Run","Livesplit"]
chosen_timer:ttk.Combobox = ttk.Combobox(timer_options_result_frame,values=timer_options,state="readonly")
chosen_timer.set("Open Speed Run")
chosen_timer.pack(fill="x",padx=20,pady=(5,2),side=tk.RIGHT,anchor="n")

split_on_all_goals_var:tkinter.BooleanVar=tk.BooleanVar(value=current_settings["SplitOnAllGoals"])
split_on_all_goals_checkbox:tkinter.Checkbutton=tk.Checkbutton(timer_options_result_frame,text="Split when anyone goals",variable=split_on_all_goals_var)
split_on_all_goals_checkbox.pack(side=tk.LEFT)

timer_connection_frame_top: tkinter.Frame = tk.Frame(app)
timer_connection_frame_top.columnconfigure(0,weight=1)
timer_connection_frame_top.pack(fill="x",side="top",pady=(10,0),anchor="n")

timer_connection_labels:list[str] = ["OpenSpeedrun Socket Location","livesplit Address","Livesplit Port"]
current_timer_connection_settings:list[str] = [current_settings["openSpeedrunSocket"],current_settings["livesplitHost"],current_settings["livesplitPort"]]

timer_connection_fields:list[tkinter.Entry] = []

for i, text in enumerate(timer_connection_labels) :
    timer_connection_frame_top.columnconfigure(i,weight=1)

    timer_frame:tkinter.Frame = tk.Frame(timer_connection_frame_top)
    timer_frame.grid(row=0,column=i, padx=10, pady=10, sticky="new")
    timer_frame.columnconfigure(0 ,weight=1)

    timer_label:tkinter.Label=tk.Label(timer_frame, text=text, font=("Arial", 10, "bold"))
    timer_label.pack(anchor="w", pady=(0, 5))

    if text == "Livesplit Port" :
        timer_entry: tkinter.Entry = tk.Entry(timer_frame, validate="key", validatecommand=(check_number, "%P"))
    else:
        timer_entry: tkinter.Entry = tk.Entry(timer_frame)
    timer_entry.pack(fill="x")
    timer_entry.insert(0, current_timer_connection_settings[i])
    timer_connection_fields.append(timer_entry)

buttons_frame:tkinter.Frame = tk.Frame(app)
buttons_frame.pack(fill="x",side="top",pady=10,anchor="w")

save_btn:tkinter.Button=tk.Button(buttons_frame,text="Save Settings", command=save_settings)
save_btn.pack(side=tk.RIGHT)

reset_btn:tkinter.Button=tk.Button(buttons_frame,text="Reset Settings",command=reset_settings)
reset_btn.pack(side=tk.RIGHT)

stop_btn:tkinter.Button=tk.Button(buttons_frame,text="Stop Server",command=stop_server)
stop_btn.pack(side=tk.LEFT)

start_btn:tkinter.Button=tk.Button(buttons_frame,text="Save and start", command=start_server)
start_btn.pack(side=tk.LEFT)

konsol_label:tkinter.Label=tk.Label(buttons_frame,text="LogBox",font=("Arial", 10, "bold"))
konsol_label.pack(side="bottom", pady=(0,5))

logbox:tkinter.Text = tk.Text(app,wrap=tk.WORD)
logbox.pack(fill=tk.BOTH,expand=True)

stop_event = threading.Event()

sys.stdout = ConsoleRedirector(logbox)



def main() -> None:
    app.mainloop()


if __name__ == '__main__':
    main()

