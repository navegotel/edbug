import logging 
import datetime
from edferrors import ErrorMsg, AllotmentEdfError 
from edfns import ns 

def check_allotments(hotelrootnode, allotmentrootnode):
    if allotmentrootnode is not None:
        allotmentnodes = allotmentrootnode.findall("atmt:SellingData/atmt:Allotments/atmt:Allotment", ns)
        if len(allotmentnodes) == 0:
            raise AllotmentEdfError("The AllotmentEDF does not contain any Allotment elements", level=logging.ERROR)
        errormsgs = list()
        for allotmentnode in allotmentnodes:
            start = allotmentnode.get("Start")
            end = allotmentnode.get("End")
            if start is None:
                errormsgs.append(ErrorMsg("Start attribute is missing in Allotment element", node=allotmentnode, level=logging.ERROR))
            if end is None:
                errormsgs.append(ErrorMsg("End attribute is missing in Allotment element", node=allotmentnode, level=logging.ERROR))
            patternlength = allotmentnode.get("PatternLength")
            pattern = allotmentnode.get("Pattern")
            if pattern is None:
                errormsgs.append(ErrorMsg("Pattern attribute is missing in Allotment element", node=allotmentnode, level=logging.ERROR))
            if patternlength is None:
                patternlength = 1
            else:
                try:
                    patternlength = int(patternlength)
                except (ValueError, TypeError):
                    errormsgs.append(ErrorMsg("PatternLength must have a numeric value", node=allotmentnode, level=logging.ERROR))
            try:
                startdate = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                errormsgs.append(ErrorMsg("Value for Start must be a date in ISO format", node=allotmentnode, level=logging.ERROR))
            try:
                enddate = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                errormsgs.append(ErrorMsg("Value for End must be a date in ISO format", node=allotmentnode, level=logging.ERROR))
            try:
                if enddate < startdate:
                    errormsgs.append(ErrorMsg("Value for End cannot be smaller than value for Start", node=allotmentnode, level=logging.ERROR))
                expectedlength = ((enddate - startdate).days + 1) * patternlength
                if expectedlength != len(pattern):
                    errormsgs.append(ErrorMsg("The length of the string in pattern is {0}. Expected is {1}".format(len(pattern), expectedlength), node=allotmentnode, level=logging.ERROR))
                if enddate < datetime.date.today():
                    errormsgs.append(ErrorMsg("End date is in the past, the EDF is outdated", node=allotmentnode, level=logging.ERROR))
                if startdate < datetime.date.today():
                    errormsgs.append(ErrorMsg("Start date is in the past. You should only include data with date >= today", node=allotmentnode, level=logging.ERROR))
            except NameError:
                pass
        if len(errormsgs) > 0:
            raise AllotmentEdfError("{0} errors in AllotmentEDF".format(len(errormsgs)), messages=errormsgs)
    
