import os
import platform
import threading
import configparser
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk, Image
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from github import get_organization_data


def timestamp(datetime):
    return datetime.strftime("%Y-%m-%d")


timespan = 14
end_date = datetime.today()
start_date = end_date - timedelta(days=timespan)

config = configparser.RawConfigParser()
configFilePath = r".config"
config.read(configFilePath)

dir = os.path.dirname(__file__)
os.path.join(dir, "/theme/awthemes")
print(dir)

organization = config.get("project", "ORGANIZATION")
token = config.get("project", "TOKEN")

try:
    start_date = datetime.strptime(config.get("session", "START_DATE"), "%Y-%m-%d")
    end_date = datetime.strptime(config.get("session", "END_DATE"), "%Y-%m-%d")
except:
    config.add_section("session")
    config.set("session", "START_DATE", timestamp(start_date))
    config.set("session", "END_DATE", timestamp(end_date))
    config.write(open(configFilePath, "w"))

sys_os = platform.system()
sys_path = {"Darwin": "__OSX__", "Linux": "__LINUX__", "Windows": "__WINDOWS__"}
# print(f"OS->\t{sys_os}")

color_card = "#33382F"
color_input = "#191c1d"
color_bg = "#0d1117"
color_fg = "#eeefff"
color_white = "#ffffff"
auto_fetch = TRUE
fullscreen = FALSE
lastClickX = 0
lastClickY = 0
colors_activity = [color_card, "#197b4a", "#00c55a", "#45ff76", "#67ff96"]
colors_activity_disabled = [color_input, "#292929", "#363636", "#666666", "#868686"]


class App(Tk):
    def __init__(self):
        super().__init__()
        # Create Window
        self.title("Group Insight")
        if fullscreen:
            width, height = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry("%dx%d+0+0" % (width, height))
            self.resizable(False, False)
        else:
            self.eval("tk::PlaceWindow . center")
        # Add custom style
        self.call("lappend", "auto_path", "./theme/awthemes")
        self.call("package", "require", "awdark")
        self.style = Style(self)
        self.style.theme_use("awdark")
        self.configure(background=color_card)
        # Remove the default window frame
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        # Make the window draggable
        self.bind("<Button-1>", self.SaveLastClickPos)
        self.bind("<B1-Motion>", self.Dragging)

        self.canvas_width = 545
        self.canvas_height = 90
        self.selected_user = ""
        
        self.image_icon = ImageTk.PhotoImage(Image.open("icon.png"))
        # The Label widget is a standard Tkinter widget used to display a text or image on the screen.
        self.icon = Label(self, image=self.image_icon)

        # The Pack geometry manager packs widgets in rows or columns.
        self.icon.grid(column=0, row=0, sticky=W, padx=10, pady=10)

        self.label_window = Label(
            self,
            text=title,
            font=("Arial", 12),
            background=color_card,
            foreground=color_white,
        )
        self.label_window.grid(row=0, column=0)
        # Add button to close window
        self.btn_close = Button(self, text="✕", command=self.destroy, width=2)
        # align button to the right
        self.btn_close.grid(row=0, column=0, sticky=E, padx=10, pady=10)

        frame_toolbar = LabelFrame(self, text="Github Contributions")
        frame_toolbar.grid(padx=10, pady=10, column=0, row=1)
        self.timespan = timespan
        self.date_start = DateEntry(
            frame_toolbar,
            width=12,
            background=color_input,
            foreground=color_fg,
            borderwidth=2,
        )
        self.date_start.set_date(start_date)
        self.date_start.grid(column=0, row=0)
        self.date_start.bind("<<DateEntrySelected>>", self.start_date_select)

        self.date_end = DateEntry(
            frame_toolbar,
            width=12,
            background=color_input,
            foreground=color_fg,
            borderwidth=2,
        )
        self.date_end.grid(column=1, row=0)
        self.date_end.set_date(end_date)
        self.date_end.bind("<<DateEntrySelected>>", self.end_date_select)

        # self.btn = Button(frame_toolbar, text="Update", command=self.async_request)
        # self.btn.grid(padx=0, pady=0, column=2, row=0)

        cols = ("#", "Member", "Role", "Total", "Period")
        self.listBox = Treeview(frame_toolbar, columns=cols, show="headings")
        self.listBox.column("Total", minwidth=0, width=60, stretch=NO)
        self.listBox.heading("#", text="")
        self.listBox.column("#", minwidth=0, width=20, stretch=NO)
        self.listBox.column("Period", minwidth=0, width=60, stretch=NO)
        self.listBox.bind("<<TreeviewSelect>>", self.on_select)
        self.listBox.grid(row=2, column=0, columnspan=3, rowspan=5, pady=5)
        for col in cols:
            self.listBox.heading(col, text=col)

        self.progress = Progressbar(
            self, orient=HORIZONTAL, length=self.canvas_width, mode="indeterminate"
        )

        # Contribution activity
        self.frame_contribution = LabelFrame(self, text="Activity")
        # self.frame_contribution.grid(padx=10, pady=10, column=0, row=2)
        self.label_user_name = Label(
            self.frame_contribution,
            text="",
            font=("Arial", 12),
            background=color_card,
            foreground=color_fg,
        )
        self.label_user_name.grid(row=0, columnspan=3)
        # Create a canvas
        self.canvas = Canvas(
            self.frame_contribution, width=self.canvas_width, height=self.canvas_height
        )
        self.canvas.grid(column=0, row=1, columnspan=3)
        # Remove canvas border
        self.canvas.config(highlightthickness=0)
        # Draw a partially transparent black square
        self.canvas.create_rectangle(
            0, 0, self.canvas_width - 1, self.canvas_height - 1, fill=color_card
        )

        if auto_fetch:
            self.async_request()

    def store_period(self):
        global start_date, end_date
        config.set("session", "START_DATE", timestamp(start_date))
        config.set("session", "END_DATE", timestamp(end_date))
        config.write(open(configFilePath, "w"))
    
    def start_date_select(self, event):
        global start_date, end_date
        self.timespan = (end_date - start_date).days
        set_end_date = datetime.strptime(timestamp(self.date_end.get_date()), "%Y-%m-%d")
        set_start_date = datetime.strptime(timestamp(self.date_start.get_date()), "%Y-%m-%d")
        
        if set_start_date >= end_date:
            set_end_date = set_start_date + timedelta(days=self.timespan)
            end_date = set_end_date
            self.date_end.set_date(set_end_date)
        
        start_date = set_start_date
        end_date = set_end_date
        
        self.store_period()
        self.async_request()
        
    def end_date_select(self, event):
        global start_date, end_date
        self.timespan = (end_date - start_date).days
        set_end_date = datetime.strptime(timestamp(self.date_end.get_date()), "%Y-%m-%d")
        set_start_date = datetime.strptime(timestamp(self.date_start.get_date()), "%Y-%m-%d")
        
        if set_end_date <= start_date:
            set_start_date = set_end_date - timedelta(days=self.timespan)
            start_date = set_start_date
            self.date_start.set_date(set_start_date)
        
        start_date = set_start_date
        end_date = set_end_date
        
        self.store_period()
        self.async_request()

    def SaveLastClickPos(self, event):
        global lastClickX, lastClickY
        lastClickX = event.x
        lastClickY = event.y

    def Dragging(self, event):
        x, y = (
            event.x - lastClickX + self.winfo_x(),
            event.y - lastClickY + self.winfo_y(),
        )
        self.geometry("+%s+%s" % (x, y))

    def on_select(self, event):
        # clear the canvas
        self.canvas.create_rectangle(
            0, 0, self.canvas_width - 1, self.canvas_height - 1, fill=color_bg
        )
        # Get the selected row
        selected_row = self.listBox.focus()
        # Get the values of the selected row
        user = self.listBox.item(selected_row, "values")
        if len(user) == 0:
            user = self.selected_user
        else:
            self.selected_user = user

        user_id = user[1]
        # find user data in organization team
        user_data = next(
            user for user in self.organization_data["team"] if user["login"] == user_id
        )
        # find user contribution data
        day_size = 10
        offset = {"x": 5, "y": 10}
        contributions = user_data["contributions"]

        top_day = {"contributionCount": 0}
        # get the contributionCount of the day with the highest contribution count from all the weeks
        for week in contributions["weeks"]:
            for day in week["contributionDays"]:
                if day["contributionCount"] > top_day["contributionCount"]:
                    top_day = day

        for i, week in enumerate(contributions["weeks"]):
            for j, day in enumerate(week["contributionDays"]):
                # get what color to use from the colors list based on the contribution count and total normalize using top_day
                count = day["contributionCount"]
                if top_day["contributionCount"] == 0 or count == 0:
                    index = 0
                else:
                    index = int((count / top_day["contributionCount"]) * 3) + 1
                cell_color = colors_activity_disabled[index]
                if day["date"] <= timestamp(self.date_end.get_date()) and day[
                    "date"
                ] >= timestamp(self.date_start.get_date()):
                    cell_color = colors_activity[index]

                self.canvas.create_rectangle(
                    ((i * day_size) + 1) + offset["x"],
                    ((j * day_size) + 1) + offset["y"],
                    ((i + 1) * day_size) + offset["x"],
                    ((j + 1) * day_size) + offset["y"],
                    fill=cell_color,
                    outline=color_bg,
                )
        # Set the label text to the values of the selected row
        self.label_user_name.config(text=user_data["name"] or user_data["login"])
        self.frame_contribution.grid(padx=10, pady=10, column=0, row=2)

    def update_leaderboard(self, organization_data):
        self.listBox.delete(*self.listBox.get_children())
        for i, user in enumerate(organization_data["leader_board"], start=1):
            self.listBox.insert(
                "",
                "end",
                iid=f'"{user["login"]}"',
                values=(
                    i,
                    user["login"],
                    user["role"],
                    user["contributions"]["totalContributions"],
                    user["periodSum"]
                ),
            )
        self.organization_data = organization_data
        try:
            self.listBox.selection_set(f'"{self.selected_user[1]}"')
        except:
            self.frame_contribution.grid_forget()

    def start_data_fetch(self):
        end_date = min(timestamp(self.date_end.get_date()), timestamp(datetime.today()))

        self.organization_data = get_organization_data(
            token=token,
            period=[
                timestamp(self.date_start.get_date()),
                end_date,
            ],
            organization=organization,
            log=False,
        )
        self.update_leaderboard(self.organization_data)
        self.progress.stop()
        self.progress.grid_forget()

    def async_request(self):
        def real_async_request():
            self.progress.grid(row=3, column=0, columnspan=3, pady=2)
            self.progress.start()
            self.start_data_fetch()
            # self.btn["state"] = "normal"
            self.date_start["state"] = "normal"
            self.date_end["state"] = "normal"

        threading.Thread(target=real_async_request).start()
        # self.btn["state"] = "disabled"
        self.date_start["state"] = "disabled"
        self.date_end["state"] = "disabled"


if __name__ == "__main__":
    app = App()
    app.mainloop()
