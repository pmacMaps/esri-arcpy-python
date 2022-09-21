# -------------------------------------------------------------------------------
# Name:        Export Layers to File Geodatabase and Microsoft Excel
#
# Purpose:     Creates a new directory using the current date.  A file geodatabase
#              is created in this new directory.  A list of feature classes are exported to this
#              file geodatabase.  The feature classes have field values calculated.
#              After field calculations, the layers in the file geodatabase are exported
#              to Microsoft Excel format in the newly created directory.
#
# Author:      Patrick McKinney
#
# Created:     4/4/2019
#
# Updated:     9/21/2022
# -------------------------------------------------------------------------------

import arcpy
import sys
from os import path
from os import makedirs
from datetime import date

try:
    # Time stamp variables
    date_today = date.today()
    # Date formatted as month-day-year (1-1-2017)
    formatted_date_today = date_today.strftime("%m-%d-%Y")
    # date for file geodatabase name
    date_gdb = date_today.strftime("%m%d%Y")

    # Create text file for logging results of script
    # update this variable
    log_file = path.join(r'[path]\[to]\[location]', f'Report File Name {formatted_date_today}.txt')
    # variable to store messages for log file. Messages written in finally statement at end of script
    log_message = ''

    # enterprise or file geodatabase
    # update this variable
    geodatabase = r''
    # layers
    # update this variable
    # recommended to use underscores in naming convention of second element of sub-list
    layers = [[path.join(geodatabase, r'Name of Layer'), 'Name_of_Layer'], [path.join(
        geodatabase, r'Name of Layer'), 'Name_of_Layer'], [path.join(geodatabase, r'Name of Layer'), 'Name_of_Layer']]

    # 1. create new directory
    # parent directory
    # update this variable
    parent_dir = r'[path]\[to]\[location]'
    # output directory
    out_dir = path.join(parent_dir, date_gdb)
    # create sub-directory with current date
    makedirs(out_dir)
    # add message
    log_message += f'\nCreated directory "{date_gdb}" in {out_dir}\n'

    # 2. create file geodatabase
    # parameters
    # update this variable
    out_gdb_name = f'Name_of_Geodatabase_{date_gdb}'
    out_gdb = path.join(out_dir, f'{out_gdb_name}.gdb')
    # geoprocessing
    arcpy.CreateFileGDB_management(out_dir, out_gdb_name, '10.0')
    # add message
    log_message += f'\nCreated file geodatabase "{out_gdb_name}" in directory "{out_dir}"\n'

    # 3. Export layers to file geodatabase
    for fc in layers:
        # export feature class
        arcpy.FeatureClassToFeatureClass_conversion(fc[0], out_gdb, fc[1])
        # add message
        log_message += f'\nCopied {fc[1]} layer to {out_gdb}\n'
    # end for

    # 4. update Latitude Longitude fields in feature classes
    # export feature class to excel
    # set workspace for listing function
    arcpy.env.workspace = out_gdb
    # create list of feature classes in file geodatabase
    datasets = arcpy.ListFeatureClasses()
    # fields for update
    # update this variable
    # these are examples
    fc_fields = ['SHAPE@XY', 'LON', 'LAT']
    # loop through feature classes
    for fc in datasets:
        # create update cursor
        with arcpy.da.UpdateCursor(fc, fc_fields) as cursor:
            for row in cursor:
                # longitude
                row[1] = row[0][0]
                # latitude
                row[2] = row[0][1]
                # update record
                cursor.updateRow(row)
            # end for
            # update your message
            log_message += f'\nCompleted updating Latitude and Longitude records for "{fc}" layer\n'
        # end cursor
        # convert to Excel
        arcpy.TableToExcel_conversion(fc, path.join(
            out_dir, f'{fc}.xls'), "ALIAS")
        # add message
        log_message += f'\nExported {fc} layer to Microsof Excel format\n'
    # end for
# If an error occurs running geoprocessing tool(s) capture error and write message
except (Exception, EnvironmentError) as e:
    tbE = sys.exc_info()[2]
    # add the line number the error occured to the log message
    log_message += f"\nFailed at Line {tbE.tb_lineno}\n"
    # add the error message to the log message
    log_message += "\nError: {str(e)}\n"
finally:
    try:
        if cursor:
            del cursor
    except:
        pass
    # write message to log file
    try:
        with open(log_file, 'w') as f:
            f.write(str(log_message))
    except:
        pass