import tkinter as tk
from urllib.request import urlopen
import json
import datetime
import statistics


class Main:
    def __init__(self, trackSels, prefs, win):
        ## tells object which tk object they are on
        self.__win = win
        self.__bgCol = "#D7D7D7"
        ## setting up help and pref tabs at top
        self.__winMenu = tk.Menu(self.__win)
        self.__win.config(menu=self.__winMenu)
        self.__winMenu.add_command(label="Prefs", command=self.__showPrefs)
        self.__winMenu.add_command(label="Help", command=self.__showHelp)

        # to do: add a previous menu where you select what you will do ?
        # -- might not be necessary? mayb instead a help icon in a menu bar at top !!
        # -- not included in class/ mainframe
        # add in comments to explain all this
        # (instead of anything fancy, just say "NO DATA" if no keys in list : )
        # (add the help window : )
        # todo: to keep prefs same, have a getter func thats called b4 reset

        ## sets the preferences to what's been passed in
        self.__prefs = prefs

        ## gets the current track names for prix to show to user
        self.__trackNames = trackSels

        ## starts up the actual program
        self.__startProgram()

    def __startProgram(self):
        ## initialises the selections for parameters
        self.__selections = {"compound": "", "rain": 0, "airTemp": "", "trackTemp": "", "track": ""}
        ## initialises the lists for each parameter's keys
        self.__compoundKeys = []
        self.__airTempKeys = []
        self.__trackTempKeys = []
        self.__trackKeys = []
        self.__weatherKeys = []
        ## todo: can be taken out if not used i think
        self.__selectionsData = {"compound": self.__compoundKeys, "rain": self.__weatherKeys,
                                 "airTemp": self.__airTempKeys, "trackTemp": self.__trackTempKeys,
                                 "track": self.__trackKeys}
        ## 2d list -- holds all of the key lists so can be looped through
        self.__KEYS = [self.__compoundKeys, self.__airTempKeys, self.__trackTempKeys, self.__trackKeys,
                       self.__weatherKeys]
        ## initialises list that will hold the keys all parameters contain
        self.__COMMON_KEYS = []

        ## initialises the result variables -
        # average/median length set to impossible value to show if no data has been inputted
        self.__averageLength = -1
        self.__medianLength = -1
        self.__maxLength = -1

        ## initialises frames that all buttons/text fields will be placed onto
        self.__mainFrame = tk.Frame(self.__win, bg=self.__bgCol)
        self.__mainFrame.pack(anchor="w")

        self.__resultFrame = tk.Frame(self.__win, bg=self.__bgCol)

        ## sets up label/inputs for compound selection
        self.__compoundLabel = tk.Label(self.__mainFrame, text="Tyre compound: ", bg=self.__bgCol)
        self.__compoundLabel.pack()

        self.__compoundVar = tk.StringVar()
        self.__compoundVar.set("SOFT")
        self.__compoundFieldSoft = tk.Radiobutton(self.__mainFrame, text="Soft", value="SOFT",
                                                  variable=self.__compoundVar, bg=self.__bgCol)
        self.__compoundFieldSoft.pack()
        self.__compoundFieldMedium = tk.Radiobutton(self.__mainFrame, text="Medium", value="MEDIUM",
                                                    variable=self.__compoundVar, bg=self.__bgCol)
        self.__compoundFieldMedium.pack()
        self.__compoundFieldHard = tk.Radiobutton(self.__mainFrame, text="Hard", value="HARD",
                                                  variable=self.__compoundVar, bg=self.__bgCol)
        self.__compoundFieldHard.pack()

        ## sets up label/inputs for track selection
        self.__trackNameLabel = tk.Label(self.__mainFrame, text="Track: ", bg=self.__bgCol)
        self.__trackNameLabel.pack()

        self.__trackNameVar = tk.StringVar()
        self.__trackNameVar.set("Any")
        self.__trackNameField = tk.OptionMenu(self.__mainFrame, self.__trackNameVar, *self.__trackNames)
        self.__trackNameField.pack()

        ## sets up label/inputs for air temp
        self.__airTempLabel = tk.Label(self.__mainFrame, text="Air Temperature: ", bg=self.__bgCol)
        self.__airTempLabel.pack()

        self.__airTempVar = tk.StringVar()
        self.__airTempVar.set("-99")
        self.__airTempFieldText = tk.Entry(self.__mainFrame, textvariable=self.__airTempVar, bg=self.__bgCol)
        self.__airTempFieldText.pack()

        ## sets up label/inputs for track temp
        self.__trackTempLabel = tk.Label(self.__mainFrame, text="Track Temperature: ", bg=self.__bgCol)
        self.__trackTempLabel.pack()

        self.__trackTempVar = tk.StringVar()
        self.__trackTempVar.set("-99")
        self.__trackTempFieldText = tk.Entry(self.__mainFrame, textvariable=self.__trackTempVar, bg=self.__bgCol)
        self.__trackTempFieldText.pack()

        ## sets up label/inputs for weather selections
        self.__weatherLabel = tk.Label(self.__mainFrame, text="Weather Conditions: ", bg=self.__bgCol)
        self.__weatherLabel.pack()

        self.__weatherVar = tk.IntVar()
        self.__weatherVar.set(-1)
        self.__weatherFieldSunny = tk.Radiobutton(self.__mainFrame, text="Sunny", value=0, variable=self.__weatherVar,
                                                  bg=self.__bgCol)
        self.__weatherFieldSunny.pack()
        self.__weatherFieldRain = tk.Radiobutton(self.__mainFrame, text="Rain", value=1, variable=self.__weatherVar,
                                                 bg=self.__bgCol)
        self.__weatherFieldRain.pack()

        ## button that runs submit search function to collect data
        self.__submit = tk.Button(self.__mainFrame, text="Search", command=self.__submitSearch)
        self.__submit.pack()

    def __submitSearch(self):
        ## collects the data user has inputted in fields : )
        self.__selections["compound"] = self.__compoundVar.get()
        self.__selections["rain"] = self.__weatherVar.get()
        self.__selections["airTemp"] = self.__airTempVar.get()
        self.__selections["trackTemp"] = self.__trackTempVar.get()
        self.__selections["track"] = self.__trackNameVar.get()
        self.__gatherData()

    def __gatherData(self):
        ## gets the compound keys
        self.__compoundData()

        ## if user has inputted a weather type, it collects weather data - otherwise skips it
        ## otherwise, any key is viable as weather type doesn't matter
        if self.__selections["rain"] != -1:
            self.__weatherData()

        ## only runs if user has inputted an air temp
        if self.__selections["airTemp"] != "-99":
            self.__airTempData()

        ## only runs if user has inputted a track temp
        if self.__selections["trackTemp"] != "-99":
            self.__trackTempData()

        ## only runs if user has inputted a specific track
        if self.__selections["track"] != "Any":
            self.__trackData()

        # print(self.__KEYS)

        self.__commonKeys()

    ## gets all the session (race) keys that have the needed compound in
    def __compoundData(self):
        ## contacts the api with filtering
        compoundResponse = urlopen(f'https://api.openf1.org/v1/stints?compound={self.__selections["compound"]}')
        data = json.loads(compoundResponse.read().decode('utf-8'))
        for item in data:
            if item["session_key"] not in self.__compoundKeys:
                self.__compoundKeys.append(item["session_key"])

    ## gets all the session keys that had this type of weather (rain/sun)
    def __weatherData(self):
        weatherTempResponse = urlopen(f'https://api.openf1.org/v1/weather?rainfall={self.__selections["rain"]}')
        data = json.loads(weatherTempResponse.read().decode('utf-8'))
        ## only adds in session keys that haven't been added yet -- same with all other data functions
        for item in data:
            if item["session_key"] not in self.__weatherKeys:
                self.__weatherKeys.append(item["session_key"])

    ## gets all the session keys that fit in the range of air temperature given
    def __airTempData(self):
        airTempResponse = urlopen(f'https://api.openf1.org/v1/weather?air_temperature<='
                                  f'{float(self.__selections["airTemp"]) + self.__prefs["air temp"]}'
                                  f'&air_temperature>={float(self.__selections["airTemp"]) - self.__prefs["air temp"]}')
        data = json.loads(airTempResponse.read().decode('utf-8'))

        for item in data:
            if item["session_key"] not in self.__airTempKeys:
                self.__airTempKeys.append(item["session_key"])

    ## gets all the session keys that fit in the range of track temp given
    def __trackTempData(self):
        trackTempResponse = urlopen(f'https://api.openf1.org/v1/weather?track_temperature<='
                                    f'{float(self.__selections["trackTemp"]) + self.__prefs["track temp"]}'
                                    f'&track_temperature>={float(self.__selections["trackTemp"]) - self.__prefs["track temp"]}')
        data = json.loads(trackTempResponse.read().decode('utf-8'))

        for item in data:
            if item["session_key"] not in self.__trackTempKeys:
                self.__trackTempKeys.append(item["session_key"])

    ## gets all the session keys that take place on the track given
    def __trackData(self):
        trackResponse = urlopen(f'https://api.openf1.org/v1/sessions?circuit_short_name={self.__selections["track"]}')
        data = json.loads(trackResponse.read().decode('utf-8'))

        for item in data:
            if item["session_key"] not in self.__trackKeys:
                self.__trackKeys.append(item["session_key"])

    def __commonKeys(self):
        ## may be able to take this out : )
        self.__COMMON_KEYS = []
        for key in self.__compoundKeys:
            ## default state -- assumes key is in all sets
            present = True
            for kSet in self.__KEYS:
                ## doesn't check if the key is in compound keys (always true) or sets that have no data (always false)
                # -- would lead to no data being collected
                if kSet != self.__compoundKeys and len(kSet) > 0:
                    if key not in kSet:
                        ## the first instance of it not being present in a set sets it false : )
                        present = False
            ## only adds key if in all sets checked
            if present:
                self.__COMMON_KEYS.append(key)

        ## if there's no keys in common with each other
        if len(self.__COMMON_KEYS) == 0:
            self.__showNODATA()
        else:
            ## if there are keys in common -- processes them here
            self.__getResults()
            ## todo: need to add in a little note that says thingy -- make this into a function similar to results

    def __getResults(self):
        ## number of keys being used for average
        numKeys = 0
        ## adds up all the number of laps to calculate average
        totalLength = 0
        ## adds the number of laps a set of tyres lasts to a list to calculate the median
        medianList = []

        # searches all the keys that are shared between given parameters
        for key in self.__COMMON_KEYS:
            ## gets the data needed to find tyre length
            tyreLengthResponse = urlopen(f'https://api.openf1.org/v1/stints?session_key={key}')
            data = json.loads(tyreLengthResponse.read().decode('utf-8'))[0]
            ## only gets data where the compound matches user input (otherwise all tyres from a race is counted)
            if data["compound"] == self.__selections["compound"]:
                ## takes away the lap number the tyres were put on from the lap num. they were taken off
                numLaps = int(data["lap_end"]) - int(data["lap_start"])
                ## checks preferences -- if the number is too low (e.g 2 or less) isn't counted towards average
                if numLaps >= self.__prefs["lap dif"]:
                    numKeys += 1
                    totalLength += numLaps
                ## the median is not influenced by the lap dif preference as it isn't as skewed by outliers
                medianList.append(numLaps)

        if numKeys > 0:
            self.__averageLength = round(totalLength / numKeys)
        ## if no keys went towards the average, self.__averageLength isn't calculated to avoid dividing by 0

        ## median and max lifespan calculated
        if len(medianList) > 0:
            self.__medianLength = statistics.median(sorted(medianList))
            self.__maxLength = max(medianList)

        # print(self.__averageLength, self.__medianLength, self.__maxLength)
        self.__showResults()

    def __showResults(self):
        ## get rid of main menu to show results : )
        self.__mainFrame.forget()
        self.__resultFrame.pack()

        ## show average result
        averageLabel = tk.Label(self.__resultFrame, text="Average No. Laps Tyres Last: ")

        ## if average exists, show it
        if self.__averageLength != -1:
            averageResult = tk.Label(self.__resultFrame, text=str(self.__averageLength))
        ## else: show that there is no data for it
        else:
            averageResult = tk.Label(self.__resultFrame,
                                     text="Not enough data -- try again with different preferences!!")

        averageLabel.pack()
        averageResult.pack()

        ## show median result
        medianLabel = tk.Label(self.__resultFrame, text="Median No. Laps Tyres Last: ")
        if self.__medianLength != -1:
            medianResult = tk.Label(self.__resultFrame, text=str(self.__medianLength))
        else:
            medianResult = tk.Label(self.__resultFrame,
                                    text="Not enough data -- try again with different preferences!!")

        medianLabel.pack()
        medianResult.pack()

        ## show max result
        maxLabel = tk.Label(self.__resultFrame, text="Max No. Laps Tyres Last: ")
        if self.__maxLength != -1:
            maxResult = tk.Label(self.__resultFrame, text=str(self.__maxLength))
        else:
            maxResult = tk.Label(self.__resultFrame,
                                 text="Not enough data -- try again with different preferences!!")

        maxLabel.pack()
        maxResult.pack()

        ## show button that restarts program
        reenterButton = tk.Button(self.__resultFrame, text="Retry", command=self.__redo)
        reenterButton.pack()

    def __showNODATA(self):
        ## forgets old menu to show this : )
        self.__mainFrame.forget()
        self.__resultFrame.pack()

        ## gives some advice
        NODATALabel = tk.Label(self.__resultFrame,
                               text="No data found for these parameters\n- please reenter/ change your preferences!!")
        NODATALabel.pack()

        ## show button that restarts program
        reenterButton = tk.Button(self.__resultFrame, text="Retry", command=self.__redo)
        reenterButton.pack()

    def __redo(self):
        ## gets rid of result screen
        self.__resultFrame.forget()
        ## restarts program from beginning : )!!
        self.__startProgram()

    def __showPrefs(self):
        ## this is a function that opens the preference window
        prefWindow = Preferences(self.__win, self.__prefs)
        ## sets the preferences as to what has been entered
        self.__prefs = prefWindow.getPrefs()

    def __showHelp(self):
        ## opens up help menu
        Help(self.__win)


class Preferences:
    def __init__(self, parent, currentPrefs):
        ## setting up preference window -- set prefs to default
        # parent is the parent/main window
        self.__parent = parent
        self.__prefs = currentPrefs
        self.__screen = tk.Toplevel(self.__parent)
        self.__prefFrame = tk.Frame(self.__screen)
        self.__prefFrame.pack()

        ## prevents user from editing main window while pref window is open
        self.__screen.grab_set()
        self.__screen.title("Parameter Prefs")

        ## sets up label/inputs for air temp
        self.__airTempPrefLabel = tk.Label(self.__prefFrame, text="Air Temp Preference: ")
        self.__airTempPrefField = tk.Entry(self.__prefFrame)
        self.__airTempPrefField.insert(0, "5")

        self.__airTempPrefLabel.pack()
        self.__airTempPrefField.pack()

        ## sets up label/inputs for track temp
        self.__trackTempPrefLabel = tk.Label(self.__prefFrame, text="Track Temp Preference: ")
        self.__trackTempPrefField = tk.Entry(self.__prefFrame)
        self.__trackTempPrefField.insert(0, "5")

        self.__trackTempPrefLabel.pack()
        self.__trackTempPrefField.pack()

        ## sets up label/inputs for lap dif min
        self.__lapDifPrefLabel = tk.Label(self.__prefFrame, text="Lap Difference Preference: ")
        self.__lapDifPrefField = tk.Entry(self.__prefFrame)
        self.__lapDifPrefField.insert(0, "2")

        self.__lapDifPrefLabel.pack()
        self.__lapDifPrefField.pack()

        ## button that calls setPrefs
        self.__prefSubmit = tk.Button(self.__prefFrame, text="Set Prefs", command=self.__setPrefs)
        self.__prefSubmit.pack()

    def __setPrefs(self):
        ## if possible, sets temps to what user has inputted and shows success
        try:
            self.__prefs["air temp"] = int(float(self.__airTempPrefField.get()))
            self.__prefs["track temp"] = int(float(self.__trackTempPrefField.get()))
            self.__prefs["lap dif"] = int(float(self.__lapDifPrefField.get()))
            self.__prefFrame.destroy()
            successLabel = tk.Label(self.__screen, text="Success! Preferences updated.")
            successLabel.pack()
        except ValueError:
            ## if user entered something that isn't a number, shows error without breaking program : )!!
            self.__prefFrame.destroy()
            errorLabel = tk.Label(self.__screen, text="ERROR -- Non-number entered.\nPlease close this window and "
                                                      "try again.")
            errorLabel.pack()
        ## wait 2.5 s before auto closing window
        self.__screen.after(2500, self.__screen.destroy)

    ## waits until window has been closed to send preferences to main window - stops them from being updated before
    # user can change them
    def getPrefs(self):
        self.__screen.wait_window()
        return self.__prefs


## help window class
class Help:
    def __init__(self, parent):
        ## sets main window
        self.__parent = parent
        self.__screen = tk.Toplevel(self.__parent)
        self.__helpFrame = tk.Frame(self.__screen)
        self.__helpFrame.pack()

        self.__screen.grab_set()

        ## text that explains the program : )
        self.__helpText = tk.Text(self.__screen)
        self.__helpText.insert(tk.END, "Welcome to the F1 Historic Tyre Lifespan System.\nTo use this:\n"
                                       "1. If needed, change the preferences of the parameters by clicking \"Prefs\" "
                                       "at the top of the main window. These preferences determine what range of values"
                                       " it will search for in the Air and Track Temp fields, "
                                       "as well as lap differences. If you enter 25 degrees with a preference of 2 "
                                       "degrees, you will receive data from races with temperatures of 23-27 degrees. "
                                       "It is set at a default of 5 degrees either way. Lap difference is to determine "
                                       "how many laps at minimum a set of tyres has to have been in for the data to go "
                                       "towards an *average* lifespan result. This helps get rid of any tyre sets that "
                                       "lasted only one lap and bring the average down. Default at 2 laps. To make"
                                       " the average closer to the median, use a lower number, and raising it too high"
                                       " can show discrepancies between max and median data, or provide no average."
                                       "\n\n2. Enter your current race parameters into the respective boxes. If you do "
                                       "not want to use a certain parameter, leave it as it is/ do not select. This "
                                       "will give a greater chance for more data to calculate from "
                                       "but may be less accurate to your exact conditions."
                                       "\n\n3. Press \"Search\" at the bottom when finished, and wait for results. If "
                                       "no data found for a certain parameter, it will say \"NO DATA\", this means the "
                                       "estimation given may not be accurate in respect to this parameter. If no data "
                                       "found for temperature, try making the preferences larger."
                                       "\n\nNOTE: Compound is the most important parameter: it is automatically set to "
                                       "SOFT.")
        self.__helpText.pack()


defaultPrefs = {"air temp": 5, "track temp": 5, "lap dif": 2}

## gets current date so that track selection list is accurate
year = ((datetime.datetime.now()).date()).strftime("%Y")
trackSelectionsURL = urlopen(f'https://api.openf1.org/v1/sessions?year={year}')
trackSelectionJSON = json.loads(trackSelectionsURL.read().decode('utf-8'))
## default track selection
trackSelections = ["Any"]
for session in trackSelectionJSON:
    if session["circuit_short_name"] not in trackSelections:
        ## adds in any tracks from current year
        trackSelections.append(session["circuit_short_name"])

window = tk.Tk()

window.geometry("300x400")
window.resizable(False, False)

window.title("F1 Tyre Prediction")

backgroundImage = tk.PhotoImage(file="IMAGES/F1_BG.png")

backgroundLabel = tk.Label(window, image=backgroundImage)
backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)

## runs main -- opens program
prefs = Main(trackSelections, defaultPrefs, window)
## do something with this please
window.mainloop()

