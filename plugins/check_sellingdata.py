"""This module checks the SellingData section in HotelEDF outside
the room elements

It's the reference implementation for edbug plugins. For this reason
it is verbosely commented.

Consider writing your own modules. They will be discovered and executed 
if they
   a) are placed in the plugins folder
   b) the module names start with 'check'

There is is no naming convention for functions. All functions
will be executed if they are visible to module inspection. 
This means that also functions which start with an underscore or
double underscore will be executed.

Every function must accept two parameters. The main programm will
call all functions and pass ElementTree instances, the first one 
for HotelEDF and the second one for AllotmentEDF.

IMPORTANT: The second parameter, i.e. allotmentrootnode may be None!

If you find something in the EDF that you want to report, you raise
one of the following exceptions:

HotelEdfError:     Any errors which are neither in BasicData 
                   nor in SellingData
AllotmentEdfError: All errors in AllotmentEDf, no matter where exactly 
                   the error occurs
BasicDataError:    All errors in HotelEDF/BasicData
SellingDataError:  All errors in HotelEDF/SellingData but outside Rooms
RoomError:         All errors in a Rooms/Room element but outside
                   Occupancies or ChargeBlock which have their own
                   specialised Exceptions
OccupancyError:    Any errors within an occupancy node
ChargeBlockError:  Anny errors within a ChargeBlock

HotelEdfError, AllotmentEdfError, BasicDataError and SellingDataError
take have three optional arguments. node takes a reference to the node
which is causing the error and level, which sets the loglevel (see
logging module documentation for details) and messages is a list of
ErrorMsg instances.

RoomError, OccupancyError and ChargeblockError additionally take the 
room code.

Be aware that execution of a function will stop if an exception is
raised. If you put multiple tests into one function you may want to
collect the error messages first as a list of ErrorMsg instances and
at the end of the function check the length of the list and raise
an exception passing the the list to the messages (not message) 
paramater.

See the check_allotments.py module for reference on how to do this.

Do not raise any other Exceptions apart from the above mentioned ones! 

PLEASE: The messages passed to exceptions should be concise and follow 
the DRY principle.

PLEASE: when raising an exception use the loglevel smartly and 
according to the following criteria:

   - logging.CRITICAL: Don't use this. This is only set during the
     initial checks when unpacking the data and the folder structure
     is wrong or zip file is corrupted. Critical errors are usually 
     followed by sys.exit() because further execution of the debugger
     does not make sense. You must not call sys.exit() in your plugins!

   - logging.ERROR: Anything which may lead to the EDF not showing up,
     missing required elements or attributes or any value which is so
     incredibly wrong that it deserves more than a warning.

   - logging.WARNING: Anything which is not strictly wrong but which 
     goes against good practice in EDF or just does not make much sense.
     These are usually frowned upon by Peakwork in acceptance testing
     and may lead to rejection of certification, depending on the
     project manager.
     Example: if there is no Language="**" in none of the room 
     descriptions ("**" marks a description a fallback)

   - logging.INFO: Anything which is formally correct but may be done
     in a better way. Can also be applied for elements which are 
     in the XSD but currently not implemented or to just throw useful
     information at anyone who will read the report file. Do not 
     abuse!

   - logging.DEBUG: Only information be relevant during
     plugin development but which is not useful for debugging EDF
   
Style guide: Please follow Pep 8. The only exception is line length.
Surround top-level function definitions with two blank lines. 
NEVER! use print statements in your plug-ins. Use logging.debug instead
and set -LL DEBUG when running edbug.

For any remaining questions: Look at the code, dude.
"""

import logging #needed for loglevel constants used to passed to exceptions
from edferrors import SellingDataError #only SellingDataError will be raised in this module
from edfns import ns #namespaces used in node.find() and node.findall(). edf for HotelEDF and atmt for AllotmentEDF
from string import ascii_uppercase
import datetime


def check_currency(hotelrootnode, allotmentrootnode):
    #first find the node you want to check
    sellingdatanode = hotelrootnode.find("edf:SellingData", ns) # Don't forget to use edf namespace in xpath expression and pass ns as second parameter
    if sellingdatanode is None:
        raise SellingDataError("Missing SellingData section", level=logging.ERROR) # A HotelEDF without SellingData is like a horse without legs. This is an error and therefore level is set to ERROR.
    currency = sellingdatanode.get("Currency")
    if currency is None:
        raise SellingDataError("Missing Currency", level=logging.ERROR) #Without the currency attribute the Hotel will not show up, therefore this is an error.
    if len(currency) != 3:
        raise SellingDataError("Currency must be a valid 3 letter ISO 4217 currency code", level=logging.ERROR)
    for c in currency:
        if c not in ascii_uppercase:
            raise SellingDataError("Currency must be a valid 3 letter ISO 4217 currency code", level=logging.ERROR)


def check_rounding(hotelrootnode, allotmentrootnode):
    roundingnode = hotelrootnode.find("edf:SellingData/edf:Rounding", ns)
    if roundingnode is None:
        raise SellingDataError("Missing Rounding element. You may want to include Rounding if the used currency has decimal places (e.g. USD, EUR, GBP)", level=logging.WARNING) #This is not strictly an error but including Rounding is highly recommended, mainly for setting DecimalPlace. Therefore level is set to WARNING
    mode = roundingnode.get("Mode")
    if mode is not None:
        if mode not in ['Up', 'Down', 'Commercial', 'No']:
            raise SellingDataError("Rounding Mode must be one of the following: Up, Down, Commercial, No", node=roundingnode, level=logging.ERROR)
    scope = roundingnode.get("Scope")
    if scope is not None:
        if scope not in ['Person', 'Room', 'Day']:
            raise SellingDataError("Rounding Scope must be one of the following: Person, Room, Day", node=roundingnode, level=logging.ERROR)
    if roundingnode.get("DecimalPlace") is None:
        raise SellingDataError("if your currency has decimal places (e.g. USD, EUR, GBP), you should set this to avoid rounding errors", node=roundingnode, level=logging.WARNING)
    

def check_seasondefinition(hotelrootnode, allotmentrootnode):
    seasondefsnode = hotelrootnode.find("edf:SellingData/edf:SeasonDefinitions", ns)
    if seasondefsnode is None:
        raise SellingDataError("You should include the SeasonDefinitions element and set Start and End dates", level=logging.WARNING)
    start = seasondefsnode.get("Start")
    end = seasondefsnode.get("End")
    if start is None or end is None:
        raise SellingDataError("Both Start and End attributes are mandatory in SeasonDefinitions element", node=seasondefsnode, level=logging.ERROR)
    try:
        enddate = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise SellingDataError("Value for Start must be a date in ISO format", node=allotmentnode, level=logging.ERROR))
    if enddate < datetime.date.today():
        raise SellingDataError("End date is in the past, the EDF is outdated", node=seasondefsnode, level=logging.ERROR)
    try:
        startdate = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise SellingDataError("Value for End must be a date in ISO format", node=allotmentnode, level=logging.ERROR))
    if startdate < datetime.date.today():
        raise SellingDataError("Start date is in the past. You should only include data with date >= today", node=seasondefsnode, level=logging.WARNING)
    
    

def check_rooms(hotelrootnode, allotmentrootnode):
    roomnodes = hotelrootnode.findall("edf:SellingData/edf:Rooms/edf:Room", ns)
    if len(roomnodes) == 0:
        raise SellingDataError("There are no Room elements in the EDF", level=logging.WARNING)
