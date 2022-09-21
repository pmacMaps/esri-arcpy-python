#-------------------------------------------------------------------------------
# Name:        Print Errors Helper Module
#
# Purpose:     Writes error messages that are returned from function.
#              Messages can be written to log file or printed in the console.
#
# Author:      Patrick McKinney
#
# Created:     08/22/2019
#
# Updated:     9/21/2022
#-------------------------------------------------------------------------------

import sys
import linecache

# Function to handle errors
def print_exception(error):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    # add message
    message = f'\nError: {error}\nFILE: {filename}, LINE: {lineno}\n\n\t "{line.strip()}": {exc_obj}'
    # return to variable
    return message
# end PrintException