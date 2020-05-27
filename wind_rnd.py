"""
Simple program for generating pseudo-random values for wind speed and wind
direction. The program outputs the data in a CSV-file with incremented
timestamps at 10Hz

Written by Magnus Lindahl, 25/3 2020
Tomass Wilson, 13/04 2020
"""

import random


# MAIN
def generate_wind_data(filename, num_data_points):
    """Generate a csv with num_data_points points"""
    last_dir = 45
    last_wind = 10

    # Functions for generating pseudo-random values for wind speed,
    # and wind direction.
    def wind_rnd():
        return random.uniform(last_wind-1, last_wind+1)  # +- interval

    def dir_rnd():
        return random.uniform(last_dir-5, last_dir+5)  # +- interval

    # Functions for formating the output as CSV
    def time_csv(i):
        time = i * 0.1
        # Limit number of decimals to 3, and convert int -> string
        new_time_csv = (str("%.3f" % time) + ",")
        return new_time_csv

    def wind_csv():
        new_wind = str("%.3f" % wind_rnd())
        new_wind_csv = (new_wind + ",")
        return new_wind_csv

    def dir_csv():
        new_dir = (str("%.3f" % dir_rnd()) + "\n")
        return new_dir

    main = open(filename+".csv", "w+")  # Create file and give R/W-privileges

    # Write CSV-header
    main.write("INCREMENTED.time,RANDOM.windSpeed,RANDOM.direction\n")

    for i in range(num_data_points):  # Number of data-points
        # Print data
        main.write(time_csv(i))
        main.write(wind_csv())
        main.write(dir_csv())

    main.close()  # End
