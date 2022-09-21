# Performs 'Analyze Datasets' > 'Rebuild Indexes' > 'Compress'
# > 'Analyze Datasets' > 'Rebuild Indexes' geoprocessing tools
# on an enterprise (sde) geodatabase
# connections to the database are closed, and all users are disconnected
# before running tools.  database connections are opened at the end
# Updated: 9/21/2022

# import modules
import arcpy
import sys
import time
from datetime import date
from os import path

# capture the date the script is being run
date_today = date.today()
# convert date format to month-day-year (1-1-2020)
formatted_date_today = date_today.strftime("%m-%d-%Y")
# placeholder for messages for text file
log_message = ''
# text file to write messages to
# TODO: update path
log_file = path.join(r'C:\GIS\Results', f'Database_Maint_Report_{date_today}.txt')

try:
    # database connection
    # TODO: update path for sde connection
    dbase = r"SDE Connection"
    # set workspace to geodatabase
    arcpy.env.workspace = dbase
    # get list of all:
    # > feature classes
    feature_classes = arcpy.ListFeatureClasses()
    # > tables
    tables = arcpy.ListTables()
    # list of data to run tools on
    data_list = feature_classes + tables
    # Next, for feature datasets get all of the datasets and featureclasses
    # from the list and add them to the master list.
    for dataset in arcpy.ListDatasets("", "Feature"):
        arcpy.env.workspace = path.join(dbase, dataset)
        data_list += arcpy.ListFeatureClasses() + arcpy.ListDatasets()
    # add message
    log_message += f"{time.strftime('%I:%M%p')} : Created list of feature classes and tables in geodatabase\n"

    # close database from accepting connections
    arcpy.AcceptConnections(dbase, False)
    # remove existing users
    arcpy.DisconnectUser(dbase, 'ALL')
    # add message
    log_message += f"\n{time.strftime('%I:%M%p')} : Disconnected users and closed connections to the geodatabase\n"

    # run analyze datasets
    arcpy.AnalyzeDatasets_management(dbase, 'SYSTEM', data_list, 'ANALYZE_BASE', 'ANALYZE_DELTA', 'ANALYZE_ARCHIVE')
    # add message
    log_message += f"\n{time.strftime('%I:%M%p')} : Ran 'Analyze Datasets' tool\n"
    # run rebuild indexes
    arcpy.RebuildIndexes_management(dbase, 'SYSTEM', data_list, 'ALL')
    # add message
    log_message += f"\n{time.strftime('%I:%M%p')} : Ran 'Rebuild Indexes' tool\n"

    # run compress
    arcpy.Compress_management(dbase)
     # add message
    log_message += f"\n{time.strftime('%I:%M%p')} : Ran 'Compress' tool\n"

    # run analyze datasets
    arcpy.AnalyzeDatasets_management(dbase, 'SYSTEM', data_list, 'ANALYZE_BASE', 'ANALYZE_DELTA', 'ANALYZE_ARCHIVE')
    # add message
    log_message += f"\n{time.strftime('%I:%M%p')} : Ran 'Analyze Datasets' tool\n"

    # run rebuild indexes
    arcpy.RebuildIndexes_management(dbase, 'SYSTEM', data_list, 'ALL')
     # add message
    log_message += f"\n{time.strftime('%I:%M%p')} : Ran 'Rebuild Indexes' tool\n"

    # allow database to accept connections
    arcpy.AcceptConnections(dbase, True)
# If an error occurs running geoprocessing tool(s) capture error and write message
except (Exception, EnvironmentError) as e:
    tbE = sys.exc_info()[2]
    # Write the line number the error occured to the log file
    log_message += f"\nFailed at Line {tbE.tb_lineno}\n"
    # Write the error message to the log file
    log_message += f"Error: {str(e)}"
finally:
    # write message to log file
    try:
        # allow database to accept connections
        arcpy.AcceptConnections(dbase, True)
         # add message
        log_message += f"\n{time.strftime('%I:%M%p')} : Opened connections to the geodatabase\n"
        # write messages to text file
        with open(log_file, 'w') as f:
            f.write(str(log_message))
    except:
        pass