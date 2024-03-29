# ---------------------------------------------------------------------------
# Name: Template ArcPy Script for Writing Messages to Text File
#
# Author: Patrick McKinney
#
# Created on: 01/06/2017
#
# Updated on: 9/21/2022
#
# Description: This is a template script for running ArcGIS geoprocessing tool(s).
# It is ideally suited for scripts that run as Windows scheduled tasks.
# The script writes success or error messages in a text file.
# You must update the path and name of the text file.
# ---------------------------------------------------------------------------

# Import system modules
import arcpy
import sys
import time
from datetime import date
from os import path

# Run geoprocessing tool.
# If there is an error with the tool, it will break and run the code within the except statement
try:
    # Date the script is being run
    date_today = date.today()
    # Date formatted as month-day-year (1-1-2020)
    formatted_date_today = date_today.strftime("%m-%d-%Y")

    # Create text file for logging results of script
    # Update file path with your parameters
    # Each time the script runs, it creates a new text file with the date1 variable as part of the file name
    # The example would be GeoprocessingReport_1-1-2017
    log_file = path.join(r'C:\GIS\Results', f'Geoprocessing_Report_{formatted_date_today}.txt')

    # variable to store messages for log file. Messages written in finally statement at end of script
    log_message = ''

    # get time stamp for start of processing
    start_time = time.perf_counter()

    # Put ArcPy geoprocessing code here

    # add message for text file
    log_message += '\nAdd message about geoprocessing tool process completing\n'

    # Get the end time of the geoprocessing tool(s)
    finish_time = time.perf_counter()
    # Get the total time to run the geoprocessing tool(s)
    elapsed_time = finish_time - start_time
    # total time in minutes
    elapsed_time_minutes = round((elapsed_time / 60), 2)

    # add final message to log file
    log_message += f"\nSuccessfully ran the geoprocessing tool in {elapsed_time} seconds on {formatted_date_today}\n"
# If an error occurs running geoprocessing tool(s) capture error and write message
except (Exception, EnvironmentError) as e:
    tbE = sys.exc_info()[2]
    # add the line number the error occured to the log message
    log_message += f"\nFailed at Line {tbE.tb_lineno}\n"
    # add the error message to the log message
    log_message += f"\nError: {str(e)}\n"
finally:
    # write message to log file
    try:
        with open(log_file, 'w') as f:
            f.write(str(log_message))
    except:
        pass