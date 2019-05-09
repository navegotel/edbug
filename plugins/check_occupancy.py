import logging
from edferrors import ErrorMsg, OccupancyError
from edfns import ns 


def room_checkoccupancies(roomnode):
    occupanciesnode = roomnode.find("edf:Occupancies", ns)
    if occupanciesnode is None:
        raise OccupancyError("Occupancies element is mandatory", level=logging.ERROR)
    errormsgs = list()
    occupancynodes = occupanciesnode.findall("edf:Occupancy", ns)
    if len(occupancynodes) > 4:
        errormsgs.append(ErrorMsg("Only a maximum of 4 Occupancy elements are allowed", node=occupanciesnode, level=logging.ERROR))
    for occupancynode in occupancynodes:
        minval = occupancynode.get("Min")
        if minval is None:
            errormsgs.append(ErrorMsg("Min attribute is mandatory", node=occupancynode, level=logging.ERROR))
        elif len(minval) == 0:
            errormsgs.append(ErrorMsg("Min attribute cannot be empty", node=occupancynode, level=logging.ERROR)) 
        else:
            try:
                minvalint = int(minval)
            except ValueError:
                errormsgs.append(ErrorMsg("Min attribute must contain an integer value", node=occupancynode, level=logging.ERROR))
            else:
                if minvalint == 0:
                    errormsgs.append(ErrorMsg("Min attribute cannot be 0", node=occupancynode, level=logging.ERROR))
                    
        maxval = occupancynode.get("Max")
        if maxval is None:
            errormsgs.append(ErrorMsg("Max attribute is mandatory", node=occupancynode, level=logging.ERROR))
        elif len(maxval) == 0:
            errormsgs.append(ErrorMsg("Max attribute cannot be empty", node=occupancynode, level=logging.ERROR))
        else:
            try:
                maxvalint = int(maxval)
            except ValueError:
                errormsgs.append(ErrorMsg("Max attribute must contain an unsigned integer value", node=occupancynode, level=logging.ERROR))
            else:
                if maxvalint == 0:
                    errormsgs.append(ErrorMsg("Max  attribute cannot be 0", node=occupancynode, level=logging.ERROR))
                    
        minadult = occupancynode.get("MinAdult")
        if minadult is None:
            errormsgs.append(ErrorMsg("MinAdult attribute is mandatory", node=occupancynode, level=logging.ERROR))
        elif len(minadult) == 0:
            errormsgs.append(ErrorMsg("MinAdult attribute cannot be empty", node=occupancynode, level=logging.ERROR))
        else:
            try:
                minadultval = int(minadult)
            except ValueError:
                errormsgs.append(ErrorMsg("MinAdult attribute must contain an unsigned integer value", node=occupancynode, level=logging.ERROR))
            else:
                if minadultval == 0:
                    errormsgs.append(ErrorMsg("MinAdult attribute cannot be 0", node=occupancynode, level=logging.ERROR))

        maxadult = occupancynode.get("MaxAdult")
        if maxadult is None:
            errormsgs.append(ErrorMsg("MaxAdult attribute is mandatory", node=occupancynode, level=logging.ERROR))
        elif len(maxadult) == 0:
            errormsgs.append(ErrorMsg("MaxAdult attribute cannot be empty", node=occupancynode, level=logging.ERROR))
        else:
            try:
                maxadultint = int(maxadult)
            except ValueError:
                errormsgs.append(ErrorMsg("MaxAdult attribute must contain an integer value", node=occupancynode, level=logging.ERROR))
            else:
                if maxadultint == 0:
                    errormsgs.append(ErrorMsg("MaxAdult attribute cannot be 0", node=occupancynode, level=logging.ERROR))

        minchild =  occupancynode.get("MinChild")
        if minchild is None:
            errormsgs.append(ErrorMsg("It is recommended to explicitly set MinChild", node=occupancynode, level=logging.INFO))
        elif len(minchild) == 0:
            errormsgs.append(ErrorMsg("MinChild attribute cannot be empty", node=occupancynode, level=logging.ERROR))
        else:
            try:
                int(minchild)
            except ValueError:
                errormsgs.append(ErrorMsg("The value for MinChild must be an unsigned integer", node=occupancynode, level=logging.ERROR))
                
        maxchild =  occupancynode.get("MaxChild")
        if maxchild is None:
            errormsgs.append(ErrorMsg("It is recommended to explicitly set MaxChild", node=occupancynode, level=logging.INFO))
        elif len(maxchild) == 0:
            errormsgs.append(ErrorMsg("MaxChild attribute cannot be empty", node=occupancynode, level=logging.ERROR))
        else:
            try:
                int(maxchild)
            except ValueError:
                errormsgs.append(ErrorMsg("The value for MaxChild must be an unsigned integer", node=occupancynode, level=logging.ERROR))
                
        minchargedpersons = occupancynode.get("MinChargedPersons")
        if minchargedpersons is None:
            errormsgs.append(ErrorMsg("It is recommended to explicitly set MinChargedPersons", node=occupancynode, level=logging.INFO))
        elif len(minchargedpersons) == 0:
            errormsgs.append(ErrorMsg("MinChargedPersons attribute cannot be empty", node=occupancynode, level=logging.ERROR))
        else:
            try:
                int(minchargedpersons)
            except ValueError:
                errormsgs.append(ErrorMsg("The value for MinChargedPersons must be an unsigned integer", node=occupancynode, level=logging.ERROR))
                
        if occupancynode.find("edf:Children", ns) is None:
            errormsgs.append(ErrorMsg("Occupancy must contain a Children element", node=occupancynode, level=logging.ERROR))
            
    if len(errormsgs) > 0:
        raise OccupancyError("There are errors in one or more Occupancy elements", messages = errormsgs)
