import xml.etree.ElementTree as ET
import logging


class ErrorMsg(object):
    def __init__(self, message, level=logging.INFO, node=None):
        self.message = message
        self.level = level
        self.snippet = None
        if node is not None:
            self.snippet = ET.tostring(node, encoding="unicode")


class EdfError(Exception):
    def __init__(self, message, level=logging.INFO, node=None, messages=None):
        """Pass the node which contains the error 
        to the node parameter. Be sure that node can be serialized,
        i.e. all its values are strings."""
        super().__init__(message)
        if messages is  not None:
            self.messages = messages
        else:
            self.messages = list()
            self.messages.append(ErrorMsg(message, level, node))
    
class HotelEdfError(EdfError):
    pass
    
class AllotmentEdfError(EdfError):
    pass

class BasicDataError(EdfError):
    pass

class SellingDataError(EdfError):
    pass
    
class RoomError(EdfError):
    pass
        
class OccupancyError(EdfError):
    pass
    
class ChargeBlockError(EdfError):
    pass

