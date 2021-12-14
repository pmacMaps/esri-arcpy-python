# ---------------------------------------------------------------------------------------------------------------
# Name:        Rebuild Cached Map Service Tiles in Updated Areas
#
# Purpose:     Rebuilds tiles for a cached map service in areas that have been updated in a reference layer within a time period specified relative to the day the script runs.
#
# Author:      Patrick McKinney
#
# Created:     9/2/2020
#
# Updated:     12/14/2021
# -------------------------------------------------------------------------------------------------------------------

# Import system modules
import arcpy
import sys
import time
import datetime
import os

try:
    # get timestamp for starting processing
    start_time = time.perf_counter()

    # Name of service
    service_name = 'Name of Service'

    # date for the day the script is run on
    date_today = datetime.date.today()
    # Date formatted as month-day-year (1-1-2017)
    formatted_date_today = date_today.strftime('%m-%d-%Y')
    # date for how many days back you want to check for changes in a dataset
    # change 8 to how many days back you want to check for changes
    date_ago = date_today - datetime.timedelta(days=8)

    # variable to store messages for log file. Messages written in finally statement at end of script
    log_message = ''
    # Create text file for logging results of script
    log_file = r'C:\GIS\Logs\Rebuild Map Tiles Report {}.txt'.format(
        formatted_date_today)

    # layer you want to check for changes in
    # there needs to be a Date field that captures when edits occur
    # ideally this would be an Editor Tracking field
    # see https://pro.arcgis.com/en/pro-app/tool-reference/data-management/enable-editor-tracking.htm
    reference_layer = r'C:\GIS\Data\reference_layer.shp'
    # make feature layer so you can use the select by attributes function
    ref_lyr_file = arcpy.MakeFeatureLayer_management(
        reference_layer, 'My_Layer')

    # SQL query clause
    # the format for queries using date fields changes based upon your data's format
    # read the docs > https://pro.arcgis.com/en/pro-app/help/mapping/navigation/sql-reference-for-elements-used-in-query-expressions.htm
    # replace "last_edited_date" with whatever field represents the date last modiefied
    where_clause = """last_edited_date >= date '{}' AND last_edited_date <= date '{}'""".format(
        date_ago, date_today)

    # select features from reference layer that have been modified within your specified date range (i.e., within last week)
    arcpy.SelectLayerByAttribute_management(
        ref_lyr_file, 'NEW_SELECTION', where_clause)

    # get count of features
    count_selected_reference = arcpy.GetCount_management(tax_parcels_lyr)[0]
    # verify records have been selected; if not, add message and exit script
    if count_selected_reference == 0:
        # add message
        log_message += 'No "Reference Layer" records have been modified between {} and {}\n'.format(
            date_ago, date_today)
        # exit
        sys.exit()

    # grid layer that covers your area of interest (city, county, state, etc)
    cache_grid_tiles = r'C:\GIS\Data\grids_layer.shp'
    # make feature layer so you can select by location
    cache_grid_tiles_lyr = arcpy.MakeFeatureLayer_management(
        cache_grid_tiles, 'Grid_Tiles')

    # select tile grids that intersect selected records from reference layer
    arcpy.SelectLayerByLocation_management(
        cache_grid_tiles_lyr, 'INTERSECT', ref_lyr_file)

    # get count of features
    count_selected_grids = arcpy.GetCount_management(cache_grid_tiles_lyr)[0]
    # verify records have been selected; if not, add message and exit script
    if count_selected_grids == 0:
        # add message
        log_message += 'No "Grid" features intersect "Reference Layer" records that have been modified between {} and {}\n'.format(
            date_ago, date_today)
        # exit
        sys.exit()

    # use selected records from grid tiles as area of interest for rebuilding cached map service tiles
    area_of_interest_lyr = r'memory\selected_grids'
    # copy selected features from grid layer to in memory
    arcpy.CopyFeatures_management(cache_grid_tiles_lyr, area_of_interest_lyr)

    # add message
    log_message += 'Added selected "Grid" features to {}\n'.format(
        area_of_interest_lyr)
    log_message += '\nSelected grids:\n\n'

    # loop through Grid layer and list what records have been selected
    # you can then use these as areas to check to verify your tiles have rebuilt the data
    # replace 'LabelField' with a field in your Grid layer
    with arcpy.da.SearchCursor(area_of_interest_lyr, 'LabelField') as cursor:
        for row in cursor:
            log_message += '\t{}\n'.format(row[0])

    # create feature set object
    # see https://pro.arcgis.com/en/pro-app/arcpy/classes/featureset.htm
    feature_set = arcpy.FeatureSet()
    # load selected records from Grid layer into feature set
    feature_set.load(area_of_interest_lyr)

    # ArcGIS Online or Portal URL
    portal = ""
    # user name of owner of item (admin users may be able to overwrite)
    # create environment variable to store username; pass that variable name into get() method
    user = os.environ.get('user_name_environment_variable')
    # password of owner of item (admin users may be able to overwrite)
    # create environment variable to store pasword; pass that variable name into get() method
    password = os.environ.get('password_environment_variable')

    # sign-in to Portal or ArcGIS Online
    arcpy.SignInToPortal(portal, user, password)

    # geoprocessing - rebuild map service cache tiles
    # see https://pro.arcgis.com/en/pro-app/tool-reference/server/manage-map-server-cache-tiles.htm
    # manually rebuilding the tiles for the service and copying the geoprocessing tool as a Python snippet
    # can be used to get set this function
    arcpy.server.ManageMapServerCacheTiles('service url', [
                                           'scales to rebuild'], 'RECREATE_ALL_TILES', -1, feature_set, wait_for_job_completion='WAIT')

    # get time stamp for end of processing
    finish_time = time.perf_counter()
    # time of processing in seconds
    elapsed_time = finish_time - start_time
    # time in minutes
    elapsed_time_minutes = round((elapsed_time / 60), 2)
    # time in hours
    elapsed_time_hours = round((elapsed_time_minutes / 60), 2)

    log_message += '\n\nRebuilt cached tiles for {} in {}-hours on {}\n'.format(
        service_name, elapsed_time_hours, formatted_date_today)
# If an error occurs running geoprocessing tool(s) capture error and write message
# handle error outside of Python system
except EnvironmentError as e:
    tbE = sys.exc_info()[2]
    # Write the line number the error occured to the log file
    log_message += '\nFailed at Line {}\n'.format(tbE.tb_lineno)
    # Write the error message to the log file
    log_message += 'Error: {}'.format(str(e))
# handle exception error
except Exception as e:
    # Store information about the error
    tbE = sys.exc_info()[2]
    # Write the line number the error occured to the log file
    log_message += '\nFailed at Line {}\n'.format(tbE.tb_lineno)
    # Write the error message to the log file
    log_message += 'Error: {}'.format(e)
finally:
    # write message to log file
    try:
        with open(log_file, 'w') as f:
            f.write(str(log_message))
    except:
        pass
