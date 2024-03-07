import tkinter as tk
from urllib.request import urlopen
import json
import datetime


class Main:
    def __init__(self, trackSels, prefs, win):
        self.__win = win
        self.__bgCol = "#D7D7D7"
        self.__winMenu = tk.Menu(self.__win)
        self.__win.config(menu=self.__winMenu)
        self.__winMenu.add_command(label="Prefs", command=self.__showPrefs)
        self.__winMenu.add_command(label="Help")

        # to do: add a previous menu where you select what you will do ?
        # -- might not be necessary? mayb instead a help icon in a menu bar at top !!
        # -- not included in class/ mainframe
        # add in comments to explain all this
        # instead of anything fancy, just say "NO DATA" if no keys in list : )
        # make it look nice - little image an everything
        # add the help window : )
        self.__prefs = {"air temp": 5, "track temp": 5}
        self.__selections = {}
        self.__compoundKeys = []
        self.__airTempKeys = []
        self.__trackTempKeys = []
        self.__trackKeys = []
        self.__weatherKeys = []
        self.__KEYS = [self.__compoundKeys, self.__airTempKeys, self.__trackTempKeys, self.__trackKeys, self.__weatherKeys]
        self.__COMMON_KEYS = []

        self.__trackNames = trackSels

        self.__mainFrame = tk.Frame(self.__win, bg=self.__bgCol)
        self.__mainFrame.pack(anchor="w")

        self.__compoundLabel = tk.Label(self.__mainFrame, text="Tyre compound: ", bg=self.__bgCol)
        self.__compoundLabel.pack()

        self.__compoundVar = tk.StringVar()
        self.__compoundVar.set("SOFT")
        self.__compoundFieldSoft = tk.Radiobutton(self.__mainFrame, text="Soft", value="SOFT", variable=self.__compoundVar, bg=self.__bgCol)
        self.__compoundFieldSoft.pack()
        self.__compoundFieldMedium = tk.Radiobutton(self.__mainFrame, text="Medium", value="MEDIUM", variable=self.__compoundVar, bg=self.__bgCol)
        self.__compoundFieldMedium.pack()
        self.__compoundFieldHard = tk.Radiobutton(self.__mainFrame, text="Hard", value="HARD", variable=self.__compoundVar, bg=self.__bgCol)
        self.__compoundFieldHard.pack()

        self.__trackNameLabel = tk.Label(self.__mainFrame, text="Track: ", bg=self.__bgCol)
        self.__trackNameLabel.pack()

        self.__trackNameVar = tk.StringVar()
        self.__trackNameVar.set("Any")
        self.__trackNameField = tk.OptionMenu(self.__mainFrame, self.__trackNameVar, *self.__trackNames)
        self.__trackNameField.pack()

        self.__airTempLabel = tk.Label(self.__mainFrame, text="Air Temperature: ", bg=self.__bgCol)
        self.__airTempLabel.pack()

        self.__airTempVar = tk.StringVar()
        self.__airTempVar.set("-99")
        # need a button at the bottom that does all this !!
        self.__airTempFieldText = tk.Entry(self.__mainFrame, textvariable=self.__airTempVar, bg=self.__bgCol)
        self.__airTempFieldText.pack()

        self.__trackTempLabel = tk.Label(self.__mainFrame, text="Track Temperature: ", bg=self.__bgCol)
        self.__trackTempLabel.pack()

        self.__trackTempVar = tk.StringVar()
        self.__trackTempVar.set("-99")
        self.__trackTempFieldText = tk.Entry(self.__mainFrame, textvariable=self.__trackTempVar, bg=self.__bgCol)
        self.__trackTempFieldText.pack()

        self.__weatherLabel = tk.Label(self.__mainFrame, text="Weather Conditions: ", bg=self.__bgCol)
        self.__weatherLabel.pack()

        self.__weatherVar = tk.IntVar()
        self.__weatherVar.set(-1)
        self.__weatherFieldSunny = tk.Radiobutton(self.__mainFrame, text="Sunny", value=0, variable=self.__weatherVar, bg=self.__bgCol)
        self.__weatherFieldSunny.pack()
        self.__weatherFieldRain = tk.Radiobutton(self.__mainFrame, text="Rain", value=1, variable=self.__weatherVar, bg=self.__bgCol)
        self.__weatherFieldRain.pack()

        self.__submit = tk.Button(self.__mainFrame, text="Search", command=self.__submitSearch)
        self.__submit.pack()

    def __submitSearch(self):
        self.__selections["compound"] = self.__compoundVar.get()
        self.__selections["rain"] = self.__weatherVar.get()
        self.__selections["airTemp"] = self.__airTempVar.get()
        self.__selections["trackTemp"] = self.__trackTempVar.get()
        self.__selections["track"] = self.__trackNameVar.get()
        print(self.__selections)
        self.__gatherData()

    def __gatherData(self):
        self.__compoundData()

        if self.__selections["rain"] != -1:
            self.__weatherData()

        if self.__selections["airTemp"] != "-99":
            self.__airTempData()

        if self.__selections["trackTemp"] != "-99":
            self.__trackTempData()

        if self.__selections["track"] != "Any":
            self.__trackData()

        print(self.__KEYS)

        ## new function here -- sort data
        self.__commonKeys()

    def __compoundData(self):
        compoundResponse = urlopen(f'https://api.openf1.org/v1/stints?compound={self.__selections["compound"]}')
        data = json.loads(compoundResponse.read().decode('utf-8'))
        for item in data:
            if item["session_key"] not in self.__compoundKeys:
                self.__compoundKeys.append(item["session_key"])

    def __weatherData(self):
        weatherTempResponse = urlopen(f'https://api.openf1.org/v1/weather?rainfall={self.__selections["rain"]}')
        data = json.loads(weatherTempResponse.read().decode('utf-8'))

        for item in data:
            if item["session_key"] not in self.__weatherKeys:
                self.__weatherKeys.append(item["session_key"])

    def __airTempData(self):
        airTempResponse = urlopen(f'https://api.openf1.org/v1/weather?air_temperature<={float(self.__selections["airTemp"]) + 5}&air_temperature>={float(self.__selections["airTemp"]) - 5}')
        data = json.loads(airTempResponse.read().decode('utf-8'))

        for item in data:
            if item["session_key"] not in self.__airTempKeys:
                self.__airTempKeys.append(item["session_key"])

    def __trackTempData(self):
        trackTempResponse = urlopen(f'https://api.openf1.org/v1/weather?track_temperature<={float(self.__selections["trackTemp"]) + 5}&track_temperature>={float(self.__selections["trackTemp"]) - 5}')
        data = json.loads(trackTempResponse.read().decode('utf-8'))

        for item in data:
            if item["session_key"] not in self.__trackTempKeys:
                self.__trackTempKeys.append(item["session_key"])

    def __trackData(self):
        trackResponse = urlopen(f'https://api.openf1.org/v1/sessions?circuit_short_name={self.__selections["track"]}')
        data = json.loads(trackResponse.read().decode('utf-8'))

        for item in data:
            if item["session_key"] not in self.__trackKeys:
                self.__trackKeys.append(item["session_key"])

    def __commonKeys(self):
        for key in self.__compoundKeys:
            for set in self.__KEYS:

                if len(set) > 0:
                    pass

    def __showPrefs(self):
        prefWindow = Preferences()
        self.__prefs = prefWindow.getPrefs()


class Preferences:
    def __init__(self):
        ## add commenting in here
        self.__prefs = {"air temp": 5, "track temp": 5}
        self.__screen = tk.Tk()
        self.__screen.title("Parameter Prefs")

        self.__airTempPrefLabel = tk.Label(self.__screen, text="Air Temp Preference: ")
        self.__airTempPrefField = tk.Entry(self.__screen)

        self.__airTempPrefLabel.pack()
        self.__airTempPrefField.pack()

        self.__trackTempPrefLabel = tk.Label(self.__screen, text="Track Temp Preference: ")
        self.__trackTempPrefField = tk.Entry(self.__screen)

        self.__trackTempPrefLabel.pack()
        self.__trackTempPrefField.pack()

        self.__prefSubmit = tk.Button(self.__screen, text="Set Prefs", command=self.__setPrefs)

        self.__prefSubmit.pack()

        self.__screen.mainloop()

    def __setPrefs(self):
        self.__prefs["air temp"] = self.__airTempPrefField.get()
        self.__prefs["track temp"] = self.__trackTempPrefField.get()
        print(self.__prefs)

    def getPrefs(self):
        return self.__prefs


year = ((datetime.datetime.now()).date()).strftime("%Y")
trackSelectionsURL = urlopen(f'https://api.openf1.org/v1/sessions?year={year}')
trackSelectionJSON = json.loads(trackSelectionsURL.read().decode('utf-8'))
trackSelections = ["Any"]
for session in trackSelectionJSON:
    if session["circuit_short_name"] not in trackSelections:
        trackSelections.append(session["circuit_short_name"])

window = tk.Tk()
window.geometry("300x400")
window.resizable(False, False)

window.title("F1 Tyre Prediction")

backgroundImage = tk.PhotoImage(file="IMAGES/F1_BG.png")

backgroundLabel = tk.Label(window, image=backgroundImage)
backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)

main = Main(trackSelections, "",  window)
window.mainloop()
