"""This module checks the SellingData section in HotelEDF outside
the room elements.
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
        raise SellingDataError("Value for Start must be a date in ISO format", node=allotmentnode, level=logging.ERROR)
    if enddate < datetime.date.today():
        raise SellingDataError("End date is in the past, the EDF is outdated", node=seasondefsnode, level=logging.ERROR)
    try:
        startdate = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise SellingDataError("Value for End must be a date in ISO format", node=allotmentnode, level=logging.ERROR)
    if startdate < datetime.date.today():
        raise SellingDataError("Start date is in the past. You should only include data with date >= today", node=seasondefsnode, level=logging.WARNING)

def check_rooms(hotelrootnode, allotmentrootnode):
    roomnodes = hotelrootnode.findall("edf:SellingData/edf:Rooms/edf:Room", ns)
    if len(roomnodes) == 0:
        raise SellingDataError("There are no Room elements in the EDF", level=logging.WARNING)
