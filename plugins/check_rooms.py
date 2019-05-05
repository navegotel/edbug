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
    if len(descriptionnodes) == 0:
        raise RoomError("Consider including room descriptions in the Room node", level=logging.INFO)
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
        
def room_checkboard(roomnode):
    errormsgs = list()
    boardnodes = roomnode.findall("edf:Boards/edf:Board", ns)
    if len(boardnodes) == 0:
        raise RoomError("You must define at least one Boards/Board element", level=logging.ERROR)
    for boardnode in boardnodes:
        if boardnode.get("Code") is None:
            errormsgs.append("No Code attribute in Board node", node=boardnode, level=logging.INFO)
        if boardnode.get("GlobalType") is None:
            errormsgs.append("GlobalType attribute in Board node is mandatory", node=boardnode, level=logging.ERROR)
        elif boardnode.get("GlobalType") not in ['AO', 'BB', 'HB', 'HB+', 'FB', 'FB+', 'SC', 'AI', 'AI+', 'XX']:
            errormsgs.append(ErrorMsg("GlobalType attribute value must be one of 'AO', 'BB', 'HB', 'HB+', 'FB', 'FB+', 'SC', 'AI', 'AI+', 'XX'", node=boardnode, level=logging.ERROR))
        if len(errormsgs) > 0:
            raise RoomError("{0} errors in Boards node".format(len(errormsgs)), messages=errormsgs)
        
def room_checkglobaltypes(roomnode):
    errormsgs = list()
    gtnodes = roomnode.findall("edf:GlobalTypes/edf:GlobalType", ns)
    if len(gtnodes) == 0:
        raise RoomError("GlobalTypes element should contain at least one GlobalType element", level=logging.WARNING)
    for gtnode in gtnodes:
        code = gtnode.get("Code")
        if code is None:
            errormsgs.append("Empty Code attribute in GlobalType element", node=gtnode, level=logging.ERROR)
        elif code not in ['AP', 'BU', 'CA', 'CH', 'CT', 'DP', 'DR', 'DL', 'ER', 'FC', 'FR', 'HA', 'HB', 'JS', 'MA', 'MB', 'MH', 'PH', 'SP', 'SR', 'ST', 'SU', 'TR', 'VF', 'VH', 'VI', 'WB', 'XX']:
            errormsgs.append(ErrorMsg("Code attribute value in GlobalType element must be one of 'AP', 'BU', 'CA', 'CH', 'CT', 'DP', 'DR', 'DL', 'ER', 'FC', 'FR', 'HA', 'HB', 'JS', 'MA', 'MB', 'MH', 'PH', 'SP', 'SR', 'ST', 'SU', 'TR', 'VF', 'VH', 'VI', 'WB', 'XX'", node=gtnode, level=logging.ERROR))
