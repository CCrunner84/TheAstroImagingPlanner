

# About This Project
The goal of this dashboard project is to offer the ability to view at a glance the planning and progress of astronomical targets for imaging.  

On the left are settings to change the date and site location in case you are planning weeks, etc. in advance of a trip. 
These are the main components to the dashboard:
1. Target tracking and status - what are the best times in the night to image targets, allowing you to decide when to move on to another target
2. Tracking target progress - how much data each target has, broken down by filter and instrument
2. Acquired data - a birds-eye view of how much data has been collected on each target
3. Inspection of subexposure data - inspect subexposure data, including all FITs header data, extracted stars, and other star analyses.  Integrates with the main file store where all subexposure is stored.
5. Standalone image/star inspector for ad-hoc inspection of new frames
3. Weather forecast data

The targets are collected from either a [Voyager](https://software.starkeeper.it/) RoboClip Database, [Sequence Generator Pro](https://www.sequencegeneratorpro.com/sgpro/), or [N.I.N.A](https://nighttime-imaging.eu/) sequence files.  

## Running the app
1. Install [Docker](https://docs.docker.com/get-docker/)
2. Download and extract the [source code](https://github.com/gshau/TheAstroImagingPlanner/archive/refs/heads/master.zip)
3. Edit the [`conf/env.conf`](https://github.com/gshau/TheAstroImagingPlanner/blob/master/conf/env.conf) file and specify the following
    - `DATA_PATH` - directory where you store subframes.
    - `TARGETS_PATH` - directory where you have Voyager RoboClip, or SGP/NINA sequence files.
    - `APP_VERSION` - the app version you'd like to run.
4. Run the [`run-app.bat`](https://github.com/gshau/TheAstroImagingPlanner/blob/master/run-app.bat) file if on Windows, or the [`run-app.sh`](https://github.com/gshau/TheAstroImagingPlanner/blob/master/run-app.sh) file if on Linux/MacOS.  
5. The watchdog processes all the stored data (it can take some time, depending on how much data is available and computing resources).  
6. Once the watchdog starts to process star data, the app should be ready to use. ou can navigate to `http://localhost:8050`
7. To update the app, you can run the [`update-app`](https://github.com/gshau/TheAstroImagingPlanner/blob/master/update-app.sh) file to pull the latest build from Docker Hub.

