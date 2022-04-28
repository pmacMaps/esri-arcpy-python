# ---------------------------------------------------------------------------
# Name: Run Replication from SDE Enterprise Geodatabase to File Geodatabase
#
# Author: Patrick McKinney (pnmcartography@gmail.com)
#
# Created on: 05/12/2016
#
# Updated on: 4/26/2022
#
# Description: Synchronizes updates between a parent and child replica geodatabase in favor of the parent.
# The parent geodatabase is a SDE enterprise geodatabase. The child is a file geodatabase
# The script can be added as a windows scheduled task to automate replication updates on a weekly basis, for example.
# ---------------------------------------------------------------------------

# Import system modules
import arcpy
import sys
import datetime
import time

# attempt to run code. if an error occurs, break to except statement
try:
    # capture the date the script is being run
    date_today = datetime.date.today()
    # convert date format to month-day-year (1-1-2020)
    formatted_date_today = date_today.strftime("%m-%d-%Y")
    # placeholder for messages for text file
    log_message = ''
    # text file to write messages to
    # TODO: update path
    log_file = r'C:\GIS\Results\Database_Maint_Report_{}.txt'.format(date_today)

    # SDE is parent geodatabase in replication
    # TODO: update path for sde connection
    sde = r"SDE Connection"
    # Child file geodatabase in replication
    # TODO: update path to file geodatabase
    child_gdb = r"\\path\to\file.gdb"

    # Process: Synchronize Changes
    # Replicates data from parent to child geodatabase
    # TODO: update the name of the replication
    result = arcpy.SynchronizeChanges_management(sde, "Name of Replication", child_gdb, "FROM_GEODATABASE1_TO_2", "IN_FAVOR_OF_GDB1", "BY_OBJECT", "DO_NOT_RECONCILE")

    # delay writing results until geoprocessing tool gets the completed code
    while result.status < 4:
        time.sleep(0.2)
    # store tool result message in a variable
    resultValue = result.getMessages()
    # add the tool's message to the log message
    log_message += "completed {}\n".format(str(resultValue))
    # add a more human readable message to log message
    log_message += "\nSuccessfully ran replication from {} to {} on {}\n".format(sde, child_gdb, formatted_date_today)
# If an error occurs running geoprocessing tool(s) capture error and write message
# handle error outside of Python system
except (EnvironmentError, Exception) as e:
    tbE = sys.exc_info()[2]
    # add the line number the error occured to the log message
    log_message += "\nFailed at Line {}\n".format(tbE.tb_lineno)
    # add the error message to the log message
    log_message += "\nError: {}\n".format(str(e))
finally:
    # write message to log file
    try:
        with open(log_file, 'w') as f:
            f.write(str(log_message))
    except:
        pass