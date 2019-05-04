import datetime
import logging
from edferrors import ErrorMsg, RoomError
from edfns import ns 


def room_checkroomcode(roomnode):
    code = roomnode.get("Code")
    if code is None:
        raise RoomError("Room has no room code", level=logging.ERROR)
        
        
def room_checkdescriptions(roomnode):
    errormsgs = list()
    descriptionnodes = roomnode.findall("edf:Descriptions/edf:Description", ns)
    hasdefaultlang = False
    for descriptionnode in descriptionnodes:
        lang = descriptionnode.get("Language")
        if lang is None:
            errormsgs.append(ErrorMsg("Language attribute should be set", level=Logging.WARNING, node=descriptionnode))
        elif not (len(lang) == 2 or len(lang) == 5):
            errormsgs.append(ErrorMsg("Language attribute must be an uppercase 2-letter language code (eg. FR or DE) or a 5 letter languag_region code (eg. pt_BR or en_GB)", level=logging.ERROR, node=descriptionnode))
        elif lang == "**":
            hasdefaultlang = True
    if hasdefaultlang is False:
        errormsgs.append(ErrorMsg("At least on Language attribute in Descriptions should be set to ** to be marked as fallback language", level=logging.WARNING, node=descriptionnode))
    if len(errormsgs) > 0:
        raise RoomError("{0} errors in Descriptions".format(len(errormsgs)), messages=errormsgs)

# TODO Board, GobalTypes, find a way to check Restrictions on SellingData and Room level
