"""
This program is a prototype to illustrate the wind velocity of a drone.

Authors --Group 12 of MVK at KTH 2020.
Version --2020.03.30
"""

# Make file from other directory accessable for import
import sys
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from wind_rnd import generate_wind_data
from mapdraw import DroneMap
import math
import csv
sys.dont_write_bytecode = True

# Implement the default Matplotlib key bindings.


"""
This class is our .csv file frame, it will contain all the information necessary when it comes to reading .csv files.
Both from the drone and wind data. Frame is an object from tkinter.
"""

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.parent = parent
        self.controller = controller
        self.widgets()

class CsvFrame(MainFrame):

    """
    Here all the object declarations for this frame is produced.
    Their position relative to one another and their attributes.
    """

    def widgets(self):
        self.text_csv_1 = tk.Text(self, width=30, height=2)
        self.text_csv_1.insert(tk.INSERT, "CSV Frame")
        self.text_csv_1.grid(row=0, column=0)

        self.label_csv_1 = tk.Label(
            master=self, text="Generate wind data .csv file called:")
        self.entry_csv_1 = tk.Entry(master=self)
        self.label_csv_2 = tk.Label(
            master=self, text="Enter number of data points:")
        self.button_csv_1 = tk.Button(
            master=self, text="Generate", command=self.generate_data)

        self.button_csv_2 = tk.Button(
            master=self, text="Browse for wind file", command=self.display_data)
        self.button_csv_3 = tk.Button(
            master=self, text="Browse for drone file", command=self.display_flight)  # TODO
        self.text_csv_2 = tk.Text(master=self, width=30, height=6)

        self.label_csv_1.grid(row=1, column=0)
        self.entry_csv_1.grid(row=2, column=0, pady=5)
        self.button_csv_1.grid(rowspan=1, column=1)

        self.button_csv_2.grid(row=5, column=0)
        self.button_csv_3.grid(row=6, column=0)
        self.text_csv_2.grid(row=8, column=0, pady=15, padx=10)

    """
    This function opens a file explorer to select a .csv file for display
    and produces the data within that file on the map.
        (The function is very similar to display_data() and could be integrated
         if we don't want to do further different things with the functions)
    """

    def display_flight(self):
        # Clear contents of displayField.
        self.text_csv_2.delete(0.0, "end")  # END isn't a string
        self.filename = filedialog.askopenfilename(
            title="Select A File", filetypes=(
                ("csv files", "*.csv"), ("all files", "*.*")))
        opened = False
        if(self.filename[-4:] == ".csv"):
            try:
                csv = open(self.filename)
                self.output = csv.read()
                opened = True
            except SyntaxError:
                if isinstance(self.filename, str):
                    self.output = "The file '" + self.filename + \
                        "'is not of correct type. Please enter only .csv files."
                else:
                    self.output = "No drone .csv file selected"
        elif isinstance(self.filename, str):
            self.output = "The file '" + self.filename + \
                "'is not of correct type. Please enter only .csv files."
        else:
            self.output = "No drone .csv file selected"
        if opened:
            self.parent.mapFrame.map.set_drone_data(self.filename)
            self.output = "Drone data loaded"

        self.text_csv_2.insert("end", self.output)  # END isn't a string

    """
    This function reads the number of data points requested in the "entry_csv_2",
    and produces a file according to the name written in "entry_csv_1".
    """

    def generate_data(self):
        try:
            self.numDataPoints = 0
            # Get contents of entry and cast to int
            self.numDataPoints = self.parent.mapFrame.map.get_data_length()
        except:
            print("Number of datapoints need to be a positive number.")

        self.filename = self.entry_csv_1.get()  # Get contents of entry

        if (len(self.filename) > 0):
            generate_wind_data(self.filename, self.numDataPoints)
        else:
            print("File name must have a minimal length of 1.")

    """
    This function opens a file explorer to select a .csv file for display
    and produces the data within that file in the "text_csv_2".
    """

    def display_data(self):
        # Clear contents of displayField.
        self.text_csv_2.delete(0.0, "end")  # END isn't a string
        self.filename = filedialog.askopenfilename(
            title="Select A File", filetypes=(
                ("csv files", "*.csv"), ("all files", "*.*")))
        opened = False
        if(self.filename[-4:] == ".csv"):
            try:
                csv = open(self.filename)
                self.output = csv.read()
                opened = True
            except BaseException:
                if isinstance(self.filename, str):
                    self.output = "The file '" + self.filename + \
                        "'is not of correct type. Please enter only .csv files."
                else:
                    self.output = "No wind .csv file selected"
        elif isinstance(self.filename, str):
            self.output = "The file '" + self.filename + \
                "'is not of correct type. Please enter only .csv files."
        else:
            self.output = "No wind .csv file selected"
        if opened:
            self.parent.mapFrame.map.draw_wind(self.filename)
            self.output = "Wind data loaded"

        self.text_csv_2.insert("end", self.output)  # END isn't a string


"""
This frame class houses everything that is wanted when inspecting something on the DroneMap.
"""


class InspectFrame(MainFrame):
    def updateInfo(self, point_data, displayWindData=False):
        """
        Write data about a specific point to the inspection
        frame on the screen.

        Args:
            point_data: A dictionary containing the positional data
                and wind data at a certain point.
            displayWindData: A boolean indicating whether or not 'point_data'
                includes wind data.
        """
        self.text_inspect_1.delete(1.0, tk.END)
        self.text_inspect_1.insert(tk.INSERT, "Inspect Frame")
        self.text_inspect_1.grid(row=0, column=0)
        display_data_string = (
            "\n\nLatitude       = {0} \nLongitude      = {1} "
            "\nHeight         = {2} [m] \nSpeed          = {3} [m/s] ")
        formatted_string = display_data_string.format(
            str(point_data["xmouse"]), str(point_data["ymouse"]),
            str(point_data["height"]), str(point_data["hSpeed"]))
        if displayWindData:
            formatted_string = formatted_string + \
                "\nWind Speed     = {0} [m/s] \nWind direction = {1} [deg.]" \
                .format(str(point_data["windSpeed"]), str(point_data["windDir"]))

        self.text_inspect_1.insert(tk.END, formatted_string)
        self.text_inspect_1.grid(row=1, column=0)

    def widgets(self):
        self.text_inspect_1 = tk.Text(self, width=40, height=10)
        self.text_inspect_1.insert(tk.INSERT, "Inspect Frame")
        self.text_inspect_1.grid(row=0, column=0)


"""
This frame houses everything that has to do with attitude.
"""


class AttitudeFrame(MainFrame):
    # Inserts the pitch yaw and roll variables into the AttitudeFrame.
    def updateInfo(self, attitude):
        self.slider_attitude_1.configure(state=tk.NORMAL)
        self.slider_attitude_2.configure(state=tk.NORMAL)
        self.slider_attitude_3.configure(state=tk.NORMAL)

        self.slider_attitude_1.set(float(attitude["pitch"]))
        self.slider_attitude_2.set(float(attitude["yaw"]))
        self.slider_attitude_3.set(float(attitude["roll"]))

        self.slider_attitude_1.configure(state=tk.DISABLED)
        self.slider_attitude_2.configure(state=tk.DISABLED)
        self.slider_attitude_3.configure(state=tk.DISABLED)

    def widgets(self):
        self.slider_attitude_1 = tk.Scale(
            master=self, from_=-180, to=180, tickinterval=1, label="Pitch", bg="Red", length=160, state=tk.DISABLED)
        self.slider_attitude_1.grid(row=0, column=1, columnspan=2)
        self.slider_attitude_2 = tk.Scale(master=self, from_=-180, to=180, tickinterval=1,
                                       label="Yaw", bg="Green", orient=tk.HORIZONTAL, length=160, state=tk.DISABLED)
        self.slider_attitude_2.grid(row=1, column=0, columnspan=2)
        self.slider_attitude_3 = tk.Scale(master=self, from_=-180, to=180, tickinterval=1,
                                       label="Roll", bg="Blue", orient=tk.HORIZONTAL, length=160, state=tk.DISABLED)
        self.slider_attitude_3.grid(row=1, column=2, columnspan=2)


"""
This frame houses the DroneMap itself and anything that is must display.
"""


class MapFrame(MainFrame):
    flight_percent = 0
    point_data = {}
    location = {}
    time_end = 0

    def onpick(self, event):
        """
        Handles the event when an object in the canvas is clicked.

        It extracts the coordinate of a given click and uses the csv file
        of the drone data to retrieve the attitude data that was recorded at
        that given coordinate.

        It also calls a function in the AttitudeFrame that displays the retrieved
        attitude data.
        """
        line = event.artist
        xmouse, ymouse = event.mouseevent.xdata, event.mouseevent.ydata
        xdata, ydata = line.get_data()
        # reader = csv.reader(open("Data/attitutf.csv", "r",
        #                         encoding="UTF-8"), delimiter=",")
        reader = self.map.data
        # next(reader, None)  # Skips the first row with the headers

        pitch = []
        yaw = []
        roll = []
        height = []
        hSpeed = []
        windSpeed = []
        windDir = []

        """
        Because of how pick events work in matplotlib we can not click individual points
        when history mode is enabled because the points are interpreted as a line.
        The way the correct point is determined is by calculating the euclidean distance
        between the coordinates of the different points on the line and the coordinates of
        the mouse click. The point with the least euclidean distance from the mouse click
        is classified as the clicked point.
        """
        low = 9999  # A dummy value, it just has to be larger than the expected euclidean distance.
        closest_index = 0
        i = 0

        points = tuple(zip(xdata, ydata))
        for p in points:
            x = p[0]
            y = p[1]
            current = math.sqrt(((x - xmouse) + (y - ymouse))**2)
            if (current < low):
                low = current
                closest_index = i

            i += 1

        hasWindData = "RANDOM.windSpeed" in reader.columns
        for _, row in reader.iterrows():
            if (math.isclose(float(row["OSD.longitude"]), float(xdata[closest_index]), abs_tol=0.0000001) and
                    math.isclose(float(row["OSD.latitude"]),
                                float(ydata[closest_index]), abs_tol=0.0000001)):

                pitch.append(float(row["OSD.pitch"]))
                yaw.append(float(row["OSD.roll"]))
                roll.append(float(row["OSD.yaw"]))
                height.append(float(row["OSD.height [m]"]))
                hSpeed.append(float(row["CALC.hSpeed [m/s]"]))
                if hasWindData:
                    windSpeed.append(float(row["RANDOM.windSpeed"]))
                    windDir.append(float(row["RANDOM.direction"]))

        self.point_data["pitch"] = sum(pitch) / len(pitch)
        self.point_data["yaw"] = sum(yaw) / len(yaw)
        self.point_data["roll"] = sum(roll) / len(roll)
        self.point_data["xmouse"] = xmouse
        self.point_data["ymouse"] = ymouse
        self.point_data["height"] = sum(height) / len(height)
        self.point_data["hSpeed"] = sum(hSpeed) / len(hSpeed)
        if hasWindData:
            self.point_data["windSpeed"] = sum(windSpeed) / len(windSpeed)
            self.point_data["windDir"] = sum(windDir) / len(windDir)

        self.controller.attitudeWindow.updateInfo(self.point_data)
        self.controller.inspectWindow.updateInfo(self.point_data, hasWindData)

    def drawMap(self):
        self.map = DroneMap()
        self.fig = self.map.get_fig()
        # A tk.DrawingArea.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.mpl_connect('pick_event', self.onpick)

    def widgets(self):
        self.drawMap()
        self.slider_value = tk.IntVar()
        self.slider = tk.Scale(master=self, from_=0, to=100,
                            command=self.slider_move, length=850, orient=tk.HORIZONTAL)
        self.checkbox_value = tk.IntVar()
        self.checkbox = tk.Checkbutton(
            master=self, text="Show history", variable=self.checkbox_value, onvalue=0,
            offvalue=10, command=self.updateMap)
        self.checkbox.deselect()
        self.slider.pack(side=tk.LEFT)
        self.checkbox.pack(side=tk.RIGHT)

    def slider_move(self, event):
        """
        Update the map, based on slider position (% of whole flight),
        and show a 10 second span of drone points until that point. If show
        history is checked, show all points up until the slider position
        """
        self.flight_percent = self.slider.get() / 100
        self.updateMap()

    def updateMap(self):
        """Update the map"""
        self.map.draw_drone(flight_percent=self.flight_percent,
                            time_span=self.checkbox_value.get())
        self.canvas.draw()
        self.canvas.mpl_connect('pick_event', self.onpick)

def main():
    """
    This is the main window of the program,
    it houses all the frames and their location relative to
    one another.
    """
    mainWindow = tk.Tk()
    mainWindow.title("GUI-Prototype")
    mainWindow.geometry("1280x720")
    mainWindow.csvWindow = CsvFrame(mainWindow, controller = mainWindow)
    mainWindow.csvWindow.grid(row=0, column=1)
    mainWindow.attitudeWindow = AttitudeFrame(mainWindow, controller = mainWindow)
    mainWindow.attitudeWindow.grid(row=1, column=1)
    mainWindow.inspectWindow = InspectFrame(mainWindow, controller = mainWindow)
    mainWindow.inspectWindow.grid(row=2, column=1)
    mainWindow.mapFrame = MapFrame(mainWindow, controller = mainWindow)
    mainWindow.mapFrame.grid(row=0, column=0, rowspan=3)
    mainWindow.mainloop()


"""
This is the main loop of the program.
"""
if __name__ == "__main__":
    main()
