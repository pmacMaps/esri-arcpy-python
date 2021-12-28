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
# Updated:     12/28/2021
# -------------------------------------------------------------------------------

import arcpy
import datetime
import sys
import os

try:
    # Time stamp variables
    date_today = datetime.date.today()
    # Date formatted as month-day-year (1-1-2017)
    formatted_date_today = date_today.strftime("%m-%d-%Y")
    # date for file geodatabase name
    date_gdb = date_today.strftime("%m%d%Y")

    # Create text file for logging results of script
    # update this variable
    log_file = r'[path]\[to]\[location]\Report File Name {}.txt'.format(
        formatted_date_today)
    # variable to store messages for log file. Messages written in finally statement at end of script
    log_message = ''

    # sde database connection
    # update this variable
    sde = r'Database Connections\[SDE Database Name].sde'
    # layers
    # update this variable
    layers = [[os.path.join(sde, r'Name of Layer'), 'Name of Layer'], [os.path.join(
        sde, r'Name of Layer'), 'Name of Layer'], [os.path.join(sde, r'Name of Layer'), 'Name of Layer']]

    # 1. create new directory
    # parent directory
    # update this variable
    parent_dir = r'[path]\[to]\[location]'
    # output directory
    out_dir = r'{}\{}'.format(parent_dir, date_gdb)
    # create sub-directory with current date
    os.mkdir(out_dir)
    # add message
    log_message += '\nCreated directory "{}" in {}\n'.format(date_gdb, out_dir)

    # 2. create file geodatabase
    # parameters
    # update this variable
    out_gdb_name = r'Name_of_Geodatabase_{}'.format(date_gdb)
    out_gdb = os.path.join(out_dir, '{}.gdb'.format(out_gdb_name))
    # geoprocessing
    arcpy.CreateFileGDB_management(out_dir, out_gdb_name, '10.0')
    # add message
    log_message += '\nCreated file geodatabase "{}" in directory "{}"\n'.format(
        out_gdb_name, out_dir)

    # 3. Export layers to file geodatabase
    for fc in layers:
        # export feature class
        arcpy.FeatureClassToFeatureClass_conversion(fc[0], out_gdb, fc[1])
        # add message
        log_message += '\nCopied {} layer to {}\n'.format(fc[1], out_gdb)
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
            log_message += '\nCompleted updating Latitude and Longitude records for "{}" layer\n'.format(
                fc)
        # end cursor
        # convert to Excel
        arcpy.TableToExcel_conversion(fc, os.path.join(
            out_dir, '{}.xls'.format(fc)), "ALIAS")
        # add message
        log_message += '\nExported {} layer to Microsof Excel format\n'.format(
            fc)
    # end for
# If an error occurs running geoprocessing tool(s) capture error and write message
except (Exception, EnvironmentError) as e:
    tbE = sys.exc_info()[2]
    # add the line number the error occured to the log message
    log_message += "\nFailed at Line {}\n".format(tbE.tb_lineno)
    # add the error message to the log message
    log_message += "\nError: {}\n".format(str(e))
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
