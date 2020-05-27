# Drone Graphical Interface
A GUI that display drone position and wind information on a map, alongside detailed data from drone flights

## Installation
1. Download and install python (if you dont already have it. GUI built in python 3.7 stable release)
2. Install packages. Do this by opening the command line and running `pip install <package name>`
   1. matplotlib
   2. numpy
   3. pandas
   4. osmnx
      * for problems installing see [this](https://stackoverflow.com/questions/45901732/could-not-find-or-load-spatialindex-c-dll-in-windows/45970431) link.
      You need to install some of the requirements for osmnx manually. These are usually `fiona` `gdal` and `rtree` for which you can install from a .whl file which you can download from 
      [here](https://www.lfd.uci.edu/~gohlke/pythonlibs). Make sure you get the correct version, most likely the ones for python 3.7 32-bit, which usually have the suffix `...cp37‑cp37m‑win32.whl`.
3. run guimain.py with the correct python version
   * make sure you arent running it with a different version of python

## Using the GUI
1. On the left you will se the map of the default drone data set. You can load different drone data wiht the `load drone csv` button
2. You can generate random wind data by specifying a file name, inputting a number of data points and then pressing generate. Load this file with the `load wind csv` button
3. Use the slider below the map to scrub through the dataset. Tick the `show history` checkbox below the map and drag the slider all the way to the right to see the entire dataset.
4. Click on any point on the map to see attitude data and point specific data on the right of the window
