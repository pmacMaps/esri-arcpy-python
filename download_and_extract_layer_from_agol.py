# -------------------------------------------------------------------------------
# Name:       Download and Extract Layer from ArcGIS Online or Portal
#
# Purpose:     Sample script for downloading an item from ArcGIS Online or Portal,
#              extracting zipped download, and updating an existing layer by ovewriting
#              it with the downloaded item.
#
#              This sample assumes a file geodatabase is the format you are exporting the item,
#              and that the feature class name in the downloaded geodatabase and geodatabase
#              you are importing feature class into have the same name.
#
# Author:      Patrick McKinney
#
# Created:     7/9/2020
#
# Updated:     12/23/2021
# -------------------------------------------------------------------------------

# import modules
import arcpy
import datetime
import sys
import os
import zipfile
from arcgis.gis import GIS

try:
    # allow content to be overwritten
    arcpy.env.overwriteOutput = True

    # Time stamp variables
    date_today = datetime.date.today()
    # Date formatted as month-day-year (1-1-2017)
    formatted_date_today = date_today.strftime("%m-%d-%Y")
    # date for sub-directory name
    date_dir = date_today.strftime("%m%d%Y")

    # Create text file for logging results of script
    log_file = r'Path\To\Directory\Report File {}.txt'.format(date_today)
    # variable to store messages for log file. Messages written in finally statement at end of script
    log_message = ''

    # 1. create new sub-directory using current date within parent directory
    # new directories are created within this directory
    parent_dir = r'Path\To\Directory'
    # output directory
    out_dir = r'{}\{}'.format(parent_dir, date_dir)
    # create sub-directory with current date
    os.mkdir(out_dir)
    # add message
    log_message += '\nCreated directory "{}" in "{}"\n'.format(
        date_dir, out_dir)

    # reference to ArcGIS Online (AGOL) or Portal
    # URL to AGOL organization or Portal
    portal = ''
    # username
    # create environment variable to store username; pass that variable name into get() method
    user = os.environ.get('user_name_environment_variable')
    # password
    # create environment variable to store pasword; pass that variable name into get() method
    password = os.environ.get('password_environment_variable')
    # create AGOL/Portal object
    # adding parameter "verify_cert=False" may resolve connection issues
    gis = GIS(portal, user, password)
    log_message += '\nConnected to {}\n'.format(portal)

    # 1. Download an item (i.e., feature service) from ArcGIS Online/Portal
    # name of item for use in script
    item_name = 'My_Layer'
    # reference item by item id
    item_id = ''
    # get item
    item = gis.content.get(item_id)
    # export result
    # see https://developers.arcgis.com/rest/users-groups-and-items/export-item.htm for possible export formats
    result = item.export(item_name, 'File Geodatabase')
    # download item from ArcGIS Online/Portal
    result.download(out_dir)
    # Delete the item after it downloads to save space (optional step)
    result.delete()
    # add message
    log_message += '\nDownloaded "{}"\n'.format(item_name)

    # 2. Unzip item
    # zipped file downloaded
    # you will need to export and download the item to learn what it's filename will be
    # enhancement to make to script > set "download_path" to join between out_dir and a file in that directory that ends with ".zip"
    download_file = 'SomeFileName.zip'
    # directory where zipped file is located
    download_path = os.path.join(out_dir, download_file)
    # unzip file
    with zipfile.ZipFile(download_path, "r") as z:
        z.extractall(out_dir)
    # add message
    log_message += '\nUnzipped file(s)\n'

    # 3. Copy item into a persistent file geodatabase, overwriting existing dataset
    # file geodatabase storing dataset being overwritten
    out_gdb = r'Path\To\Persistant_Database.gdb'
    # name of feature class
    # this example assumes a file geodatabase is downloaded from AGOL/Portal
    feature_class = 'Some_GIS_Layer'

    # This next section assumes you exported item as a file geodatabase
    # If not, you'll need to update the following to work with your download format

    # get list of contents in "out_dir" directory
    dir_contents = os.listdir(out_dir)
    # placeholder for extracted file geodatabase
    in_gdb = ''

    # loop through directory and create object for file geodatabase
    # assumed only one file geodatabase exists in this location
    for content in dir_contents:
        if content.endswith('.gdb'):
            in_gdb = os.path.join(out_dir, content)

    # copy feature class to persistant geodatatbase
    arcpy.Copy_management(os.path.join(in_gdb, feature_class),
                          os.path.join(out_gdb, feature_class))

    # add message
    log_message += '\nCopied data from "{}" to "{}"\n'.format(in_gdb, out_gdb)
# If an error occurs running geoprocessing tool(s) capture error and write message
except (Exception, EnvironmentError) as e:
    tbE = sys.exc_info()[2]
    # add the line number the error occured to the log message
    log_message += "\nFailed at Line {}\n".format(tbE.tb_lineno)
    # add the error message to the log message
    log_message += "\nError: {}\n".format(e)
finally:
    # write message to log file
    try:
        with open(log_file, 'w') as f:
            f.write(str(log_message))
    except:
        pass
