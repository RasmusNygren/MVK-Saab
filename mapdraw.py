"""
Code for drawing a matplotlib map of drone movements

Authors --Group 12 of MVK at KTH 2020.
Version --2020.05.01
"""

import datetime
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import osmnx as ox
# FOR HELP INSTALLING OSMNX, SEE THIS LINK:
# https://stackoverflow.com/questions/45901732/could-not-find-or-load-spatialindex-c-dll-in-windows/45970431


def read_drone_csv(csv_path):
    """
    Read data csv

    Args:
        csv_path: The path to the .csv drone flight file.

    Returns:
        data: A pandas dataframe with time, longitude, latitude, pitch, yaw,
        heigh and speed of the drone.
    """

    data = pd.read_csv(csv_path, delimiter=",", encoding="utf-8")
    data = data[["CUSTOM.updateTime", "OSD.latitude", "OSD.longitude", "OSD.pitch", "OSD.yaw", "OSD.roll", "OSD.height [m]", "CALC.hSpeed [m/s]"]]

    # get date, if possible
    dates = pd.to_datetime(data["CUSTOM.updateTime"],
                           errors="coerce",
                           format="%d/%m/%Y %H:%M")
    dates = dates.dropna()
    try:
        date = dates.iloc[0]
    except IndexError:
        print("No date found - default time applied: 01/01/1990 00:00 ")
        date = datetime.datetime.strptime(
            "01/01/1990 00:00", "%d/%m/%Y %H:%M")

    # convert time to datetime
    data["CUSTOM.updateTime"] = pd.to_datetime(data["CUSTOM.updateTime"],
                                               errors="coerce",
                                               format="%M:%S.%f")
    # drop nonconforming dates
    data = data.dropna()
    # Add date. NOTE: This does not handle the changing of the hour well :(
    data["CUSTOM.updateTime"] = data["CUSTOM.updateTime"].apply(
        lambda x: x.replace(year=date.year,
                            month=date.month,
                            day=date.day,
                            hour=date.hour))
    return data


def read_wind_csv(csv_path, start_date):
    """
    Read wind data csv

    Args:
        csv_path: The path to the .csv drone flight file.

    Returns:
        data: A pandas dataframe with time, speed and direction
    """
    data = pd.read_csv(csv_path, delimiter=",", encoding="utf-8")
    data = data.dropna()

    # add start date
    data["INCREMENTED.time"] = data["INCREMENTED.time"].apply(
        lambda x: start_date + datetime.timedelta(seconds=x))

    return data


class DroneMap():
    """
    Class that contains a drone map, with figure, axes and data
    """

    def __init__(self):
        self.flight_percent = 0
        self.time_span = None
        self.drone_points = None
        self.arrows = []
        self.xlim_diff = 0
        self.wind_data = None
        self.drone_data = read_drone_csv("Data/attitutf.csv")
        self.merged_data = self.grid_bin_data(self.drone_data)
        self.data = None
        self.draw_map()
        self.draw_drone()

    def get_fig(self):
        """Fetch figure"""
        return self.fig

    def get_data_length(self):
        return len(self.drone_data)

    def get_drone_data(self):
        """Fetch drone data, a dataframe with longitude and latitude points"""
        return self.drone_data

    def set_drone_data(self, csv_path):
        """Set the drone data to be shown on the map"""
        self.drone_data = read_drone_csv(csv_path)
        self.draw_drone()

    def draw_map(self, padx=0.001, pady=0.001):
        """
        Generate a 2d matplotlib plot with buildings and the drone flight path

        Args:
            padx: the number of meters to add either side of the drone data.
                TODO: Actually make this meters, not latitude
            pady: the number of meters to add top and bottom of the drone data.
                TODO: Actually make this meters, not longitude

        Returns:
            fig: A matplotlib figure containing the drone map
        """
        north = max(self.drone_data["OSD.latitude"]) + pady
        south = min(self.drone_data["OSD.latitude"]) - pady
        east = max(self.drone_data["OSD.longitude"]) + padx
        west = min(self.drone_data["OSD.longitude"]) - padx

        # Fetch the OSM data
        place = "Åkersberga, Sweden"
        graph = ox.graph_from_bbox(north, south, east, west)
        area = ox.gdf_from_place(place)
        buildings = ox.create_footprints_gdf(
            "shapely Polygon", north, south, east, west)
        _, edges = ox.graph_to_gdfs(graph)

        # Plot the different map features
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        area.plot(ax=self.ax, facecolor='black')
        edges.plot(ax=self.ax, linewidth=1, edgecolor='#BC8F8F')
        buildings.plot(ax=self.ax, facecolor='khaki', alpha=0.7)
        try:
            leisure = ox.create_footprints_gdf(
                "shapely Polygon", north, south, east, west, "leisure")
            parks = leisure[leisure["leisure"].isin(["park","playground"])]
            parks.plot(ax=self.ax, facecolor='limegreen')
        except:
            print("No parks within bbox")

        self.ax.axis("equal")
        self.ax.set_xlim(west, east)
        self.xlim_diff = east - west
        self.ax.set_ylim(north, south)
        plt.tight_layout()

        # Event handlers
        def on_xlims_change(axes):
            # Update the reference scale for arrow drawing
            # TODO: Find some way to update the map on zoom action, rather than
            #       having to wait for the slider to be updated
            x, xmax = self.ax.get_xlim()
            self.xlim_diff = xmax - x

        # Set callback, to update arrow size when screen is zoomed
        self.ax.callbacks.connect('xlim_changed', on_xlims_change)

    def grid_bin_data(self, data, grid_size=0.00002):
        """
        Collapse data points into chunks of size grid_size,
        taking only the latest point
        TODO: Do something cool with clustering
        TODO: Weight averaging by time
            Newer points should have more weight in the average
        TODO: Dont bin points outside of slider scope maybe?

        args:
            grid_size: The size of each grid square
        """
        # Get bin bounds
        xmin = round_down(min(data["OSD.longitude"]), grid_size)
        xmax = round_up(max(data["OSD.longitude"]), grid_size)
        ymin = round_down(min(data["OSD.latitude"]), grid_size)
        ymax = round_up(max(data["OSD.latitude"]), grid_size)

        # new dataframe
        binned_data = pd.DataFrame(columns=data.columns)

        # Bin for each grid location
        for x in np.arange(xmin, xmax, grid_size):
            for y in np.arange(ymin, ymax, grid_size):
                xend = x + grid_size
                yend = y + grid_size
                points = data.loc[(data["OSD.longitude"] >= x)
                                       & (data["OSD.longitude"] < xend)
                                       & (data["OSD.latitude"] >= y)
                                       & (data["OSD.latitude"] < yend)].copy()
                if points.size == 0:
                    continue

                # get most recent point
                point = points.loc[points["CUSTOM.updateTime"]
                                   == max(points["CUSTOM.updateTime"])]

                binned_data = binned_data.append(point, ignore_index=True)

        return binned_data

    def draw_drone(self, flight_percent=None, time_span=None):
        """
        Function that draws (or redraws) drone data points

        Args:
            flight_percent: The percent of the flight to draw points up to
            time_span: The number of seconds before end to draw points.
                This creates a window of time that you can see points for
        """
        # Cache time_end and time_stamp so they are not
        # reset after wind data is loaded in.
        if flight_percent is None:
            flight_percent = self.flight_percent
        else:
            self.flight_percent = flight_percent
        if time_span is None:
            time_span = self.time_span
        else:
            self.time_span = time_span

        if self.merged_data is not None:
            self.data = self.merged_data
        else:
            self.data = self.drone_data.copy()
        all_time_points = self.data["CUSTOM.updateTime"]

        # If history box is checked, time_span is the entire flight
        # duration so all points are drawn. If unchecked, time_span
        # is default 10 so only the last 10 seconds are drawn.
        if time_span is None or time_span == 0:
            time_span = (max(all_time_points) - min(
                all_time_points)).seconds

        # Set the time interval where points are draw
        time_end_seconds = (max(all_time_points) - min(
            all_time_points)).seconds * flight_percent
        time_end = min(all_time_points) + \
            datetime.timedelta(seconds=time_end_seconds)
        time_start = time_end - \
            datetime.timedelta(seconds=time_span)

        # Drop all points that aren't within our time interval
        data_subset = self.data.drop(self.data[(all_time_points < time_start) | (
            all_time_points > time_end)].index)
        if data_subset.size == 0:
            return

        self.data = data_subset.copy()  # Update data to contain currently displayed points

        # Extract the latest point to distinguish it from the rest
        last_point = data_subset.loc[data_subset["CUSTOM.updateTime"] == max(
            data_subset["CUSTOM.updateTime"])]
        data_subset = data_subset.drop(last_point.index)

        # Remove old points from screen and reset drone_points to
        # avoid memory leak.
        if self.drone_points is not None:
            for point in self.drone_points:
                point.remove()
            self.drone_points = None

        # Plot all points except last in cyan
        previous_points = self.ax.plot(
            data_subset["OSD.longitude"].to_numpy(),
            data_subset["OSD.latitude"].to_numpy(), 'co', picker=5)

        # Plot last point in red
        latest_point = self.ax.plot(
            last_point["OSD.longitude"].to_numpy(),
            last_point["OSD.latitude"].to_numpy(), 'ro', markersize=7,
            picker=5)

        # Concatenate last point to previous points and draw to screen
        self.drone_points = previous_points + latest_point

        # Clear arrows for redrawing
        if self.arrows:
            for arrow in self.arrows:
                arrow.remove()
            self.arrows = []
        # Draw wind vectors, if applicable
        if "RANDOM.windSpeed" in data_subset.columns:
            xleft, xright = self.ax.get_xlim()
            xdiff = xright - xleft
            arrow_size_mod = 0.006 * xdiff
            for _, point in data_subset.iterrows():
                x = point["OSD.longitude"]
                y = point["OSD.latitude"]
                try:
                    wx = math.cos(math.radians(point["RANDOM.direction"])) * \
                        point["RANDOM.windSpeed"] * arrow_size_mod
                    wy = math.sin(math.radians(point["RANDOM.direction"])) * \
                        point["RANDOM.windSpeed"] * arrow_size_mod
                except KeyError:
                    print("Wind data missing for " +
                          str(point["CUSTOM.updateTime"]) + "!")
                    continue
                self.arrows.append(self.ax.arrow(
                    x, y, wx, wy, width=arrow_size_mod))

        self.fig.canvas.draw()  # Update canvas

    def draw_wind(self, csv_path):
        """
        Draw vectors from csv data onto the map

        Args:
            csv_path: The path to the csv file
        """
        self.wind_data = read_wind_csv(csv_path, self.drone_data["CUSTOM.updateTime"].iloc[0])
        self.merged_data = self.drone_data.merge(self.wind_data, how="left", left_on="CUSTOM.updateTime", right_on="INCREMENTED.time")
        self.merged_data = self.grid_bin_data(self.merged_data)
        self.draw_drone()


def round_down(x, a):
    return math.floor(x / a) * a


def round_up(x, a):
    return math.ceil(x / a) * a
