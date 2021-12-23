# -------------------------------------------------------------------------------------------------------------------------------------------
# Name:        Overwrite Feature Service Hosted in ArcGIS Online or Portal from
#              an ArcGIS Pro Document
#
# Purpose:     This script can be used when you want to automate updating the data in
#              a hosted feature service in ArcGIS Online or Portal with data from a
#              local source.
#
#              This is accomplished by using an ArcGIS Pro document that has the datasource
#              in a map frame.  A service definition file is created from the Pro document.
#              Then, the service definition associated with the feature service is overwritten
#              using the definition file.
#
#              By using scheduled tasks, you can push regular updates of a dataset to ArcGIS
#              Online or Portal hosted feature services.
#
# Created:     9/11/2020
#
# Updated:     12/23/2021
#
# Author:      Patrick McKinney
# --------------------------------------------------------------------------------------------------------------------------------------------

# import modules
import arcpy
import os
import sys
import datetime
import time
from arcgis.gis import GIS

# attempt to run code; if an error occurs, error messages will be logged in a text file
try:
    # get time stamp for start of processing
    start_time = time.perf_counter()

    # Date the script is being run
    date_today = datetime.date.today()
    # Date formatted as month-day-year (1-1-2020)
    formatted_date_today = date_today.strftime("%m-%d-%Y")

    # variable to store messages for log file. Messages written in finally statement at end of script
    log_message = ''
    # Create text file for logging messages of script progress and/or errors
    log_file = r'Path\To\Directory\Report File {}.txt'.format(
        formatted_date_today)

    # Set the path to the ArcGIS Pro project
    # this project contains the local dataset the feature service is being updated for
    projPath = r'Path\To\Directory\ArcGIS_Pro_Project.aprx'

    # Feature service/SD name
    sd_fs_name = ""
    # service definition item ID
    sd_id = ""
    # ArcGIS Online or Portal URL
    portal = ""
    # user name of owner of item (admin users may be able to overwrite)
    # create environment variable to store username; pass that variable name into get() method
    user = os.environ.get('user_name_environment_variable')
    # password of owner of item (admin users may be able to overwrite)
    # create environment variable to store pasword; pass that variable name into get() method
    password = os.environ.get('password_environment_variable')

    # sign-in to ArcGIS Online or Portal within ArcGIS Pro project
    arcpy.SignInToPortal(portal, user, password)

    # Set sharing options for feature service
    # sharing with organization
    shrOrg = True  # or False
    # sharing with everyone
    shrEveryone = True  # or False
    # sharing with groups
    shrGroups = ""  # name of group(s), i.e, 'Public Safety'

    # Local paths to create temporary content
    relPath = os.path.dirname(projPath)
    # service definition draft file
    sddraft = os.path.join(relPath, "WebUpdate.sddraft")
    # service defition
    # this is what is being overwritten to ArcGIS Online
    # this is how you push your new data to ArcGIS Online from the local source
    sd = os.path.join(relPath, "WebUpdate.sd")

    # Create a new SDDraft and stage to SD
    log_message += "Creating Service Defintion file\n"
    # allow content to be ovewritten
    arcpy.env.overwriteOutput = True
    # reference to ArcGIS Pro project
    prj = arcpy.mp.ArcGISProject(projPath)
    # reference to first map in ArcGIS Pro project
    # assumes data/layer is in first map within ArcGIS Pro project
    mp = prj.listMaps()[0]

    # Converts a map, layer, or list of layers in an ArcGIS Project to a Service Definition Draft (.sddraft) file.
    # see https://pro.arcgis.com/en/pro-app/arcpy/mapping/createweblayersddraft.htm
    arcpy.mp.CreateWebLayerSDDraft(
        mp, sddraft, sd_fs_name, "MY_HOSTED_SERVICES", "FEATURE_ACCESS", "", True, True, False, True, True)

    # Stages a service definition. A staged service definition file (.sd) contains all the necessary information to share a web layer, web tool, or service.
    # see https://pro.arcgis.com/en/pro-app/tool-reference/server/stage-service.htm
    arcpy.StageService_server(sddraft, sd)

    # add message
    log_message += "\nConnecting to {}\n".format(portal)
    # Connect to ArcGIS Online or Portal
    # may need to add 'verify_cert=False' argument at end of function call
    gis = GIS(portal, user, password)

    # Find the SD, update it, publish /w overwrite and set sharing and metadata
    log_message += "\nSearching for original Service Definition on portal\n"

    # get access to service definition file that is being overwritten in ArcGIS Online or Portal
    sdItem = gis.content.get(sd_id)

    # add message
    log_message += "\nFound SD: {}, ID: {}\n".format(sdItem.title, sdItem.id)
    # update data for service definition ArcGIS Online/Portal item using the service definition file created in ArcGIS Pro
    sdItem.update(data=sd)

    # add message
    log_message += "\nOverwriting existing feature service\n"
    # overwrite feature service so it will now reference updated data pushed from a local source
    fs = sdItem.publish(publish_parameters=pub_params, overwrite=True)

    # set sharing options for feature service
    if shrOrg or shrEveryone or shrGroups:
        log_message += "\nSetting sharing options\n"
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)

    # add message
    log_message += "\nFinished updating: {}; ID: {}\n".format(fs.title, fs.id)

    # get time stamp for end of processing
    finish_time = time.perf_counter()
    # total time in seconds
    elapsed_time = finish_time - start_time
    # time in minutes
    elapsed_time_minutes = round((elapsed_time / 60), 2)

    # add message
    log_message += "\nOverwrote 'Some Dataset' feature service to ArcGIS Online in {}-minutes on {}\n".format(
        elapsed_time_minutes, formatted_date_today)
# If an error occurs running geoprocessing tool(s) capture error and write message
except (Exception, EnvironmentError) as e:
    tbE = sys.exc_info()[2]
    # Write the line number the error occured to the log file
    log_message += "\nFailed at Line {}\n".format(tbE.tb_lineno)
    # Write the error message to the log file
    log_message += "Error: {}".format(str(e))
finally:
    # write message to log file
    try:
        with open(log_file, 'w') as f:
            f.write(str(log_message))
    except:
        pass
