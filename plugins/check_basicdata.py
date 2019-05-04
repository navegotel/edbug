"""This module checks the BasicData section of EDF files.
"""
import logging
from edferrors import BasicDataError, AllotmentEdfError
from edfns import ns
from string import ascii_lowercase, ascii_uppercase

def check_rootattribs(hotelrootnode, allotmentrootnode):
    if allotmentrootnode is not None:
        basicdatanode = hotelrootnode.find("edf:BasicData", ns)
        allotmentbasicdatanode = allotmentrootnode.find("atmt:BasicData", ns)
        if basicdatanode.get("Code") != allotmentbasicdatanode.get("Code"):
            raise BasicDataError("BasicData Code attribute in HotelEDF {0} and AllotmentEDF {1} do not match".format(basicdatanode.get("Code"), allotmentbasicdatanode.get("Code")), level=logging.ERROR)
        if basicdatanode.get("TourOperatorCode") != allotmentbasicdatanode.get("TourOperatorCode"):
            raise BasicDataError("BasicData TourOperatorCode attribute in HotelEDF {0} and AllotmentEDF {1} do not match".format(basicdatanode.get("TourOperatorCode"), allotmentbasicdatanode.get("TourOperatorCode")), level=logging.ERROR)
        if basicdatanode.get("Source") != allotmentbasicdatanode.get("Source"):
            raise BasicDataError("BasicData Source attribute in HotelEDF {0} and AllotmentEDF {1} do not match".format(basicdatanode.get("Source"), allotmentbasicdatanode.get("Source")), level=logging.ERROR)

def check_name(hotelrootnode, allotmentrootnode):
    namenode = hotelrootnode.find("edf:BasicData/edf:Name", ns)
    if namenode is None:
        raise BasicDataError("Missing Name element", node=namenode, level=logging.ERROR)
    elif namenode.text is None:
        raise BasicDataError("Empty Name element", node=namenode, level=logging.ERROR)
    else:
        if namenode.text.find("\n") > -1:
            raise BasicDataError("Name must not contain any line breaks", node=namenode, level=logging.ERROR)
        if len(namenode.text) > 100:
            raise BasicDataError("Hotel name is suspiciasly long (more than 100 chars)", node=namenode, level=logging.WARNING)
    #always check allotmentrootnode for not None, the allotment file is not garanteed to exist
    if allotmentrootnode is not None:
        namenode = allotmentrootnode.find("atmt:BasicData/atmt:Name", ns)
        if namenode is not None:
            raise AllotmentEdfError("Name element not allowed in BasicData section of Allotment file", node=namenode, level=logging.ERROR)
    
    
def check_references(hotelrootnode, allotmentrootnode):
    referencesnode = hotelrootnode.find("edf:BasicData/edf:References", ns)
    if referencesnode is not None:
        if len(list(referencesnode)) == 0:
            raise BasicDataError("Empty References element. Consider removing empty nodes", node=referencesnode, level=logging.INFO)
    
    
def check_giatacode(hotelrootnode, allotmentrootnode):
    giatanode = hotelrootnode.find("edf:BasicData/edf:References/edf:GiataCode", ns)
    if giatanode is not None:
        if giatanode.text is None:
            raise BasicDataError("Empty GiataCode node", node=giatanode, level=logging.ERROR)
  
                
def check_hotelkey(hotelrootnode, allotmentrootnode):
    hotelkeynode = hotelrootnode.find("edf:BasicData/edf:References/edf:HotelKey", ns)
    if hotelkeynode is not None:
        if hotelkeynode.text is None:
            raise BasicDataError("Empty HotelKey node", node=hotelkeynode, level=logging.ERROR)
    
    
def check_street(hotelrootnode, allotmentrootnode):
    streetnode = hotelrootnode.find("edf:BasicData/edf:Address/edf:Street", ns)
    if streetnode is not None:
        if streetnode.text is None:
            raise BasicDataError("Empty Street element. Consider removing empty elements", node=streetnode, level=logging.INFO)
        elif streetnode.text.find("\n") > -1:
            raise BasicDataError("Street element should not contain any line breaks", node=streetnode, level=logging.WARNING)
            
            
def check_zipcode(hotelrootnode, allotmentrootnode):
    zipcodenode = hotelrootnode.find("edf:BasicData/edf:Address/edf:ZipCode", ns)
    if zipcodenode is not None:
        if zipcodenode.text is None:
            raise BasicDataError("Empty ZipCode element. Consider removing empty elements", node=zipcodenode, level=logging.INFO)
        elif zipcodenode.text.find("\n") > -1:
            raise BasicDataError("ZipCode element should not contain any line breaks", node=zipcodenode, level=logging.WARNING)
            
def check_citycode(hotelrootnode, allotmentrootnode):
    citynode = hotelrootnode.find("edf:BasicData/edf:Address/edf:City", ns)
    if citynode is not None:
        if citynode.text is None:
            raise BasicDataError("Empty City element. Consider removing empty elements", node=citynode, level=logging.INFO)
        elif citynode.text.find("\n") > -1:
            raise BasicDataError("City element should not contain any line breaks", node=citynode, level=logging.WARNING)
            
            
def check_country(hotelrootnode, allotmentrootnode):
    countrynode = hotelrootnode.find("edf:BasicData/edf:Address/edf:Country", ns)
    if countrynode is not None:
        if countrynode.text is None:
            raise BasicDataError("Empty Country element. Consider removing empty elements", node=countrynode, level=logging.INFO)
        elif len(countrynode.text) != 2:
            raise BasicDataError("The Country element is expected to contain a 2 letter ISO 3166 country code, not the verbose name of the country", node=countrynode, level=logging.INFO)

        
def check_phone(hotelrootnode, allotmentrootnode):
    phonenode = hotelrootnode.find("edf:BasicData/edf:Address/edf:Phone", ns)
    if phonenode is not None:
        if phonenode.text is None:
            raise BasicDataError("Empty Phone element. Consider removing empty elements", node=phonenode, level=logging.INFO)
        elif phonenode.text.find("\n") > -1:
                raise BasicDataError("Phone element should not contain any line breaks", node=phonenode, level=logging.WARNING)
        else:
            for c in phonenode.text:
                if c in ascii_lowercase or c in ascii_uppercase:
                    raise BasicDataError("Phone element should only contain phone numbers but no text.", node=phonenode, level=logging.WARNING)
                    break
                    
                    
def check_fax(hotelrootnode, allotmentrootnode):
    faxnode = hotelrootnode.find("edf:BasicData/edf:Address/edf:Fax", ns)
    if faxnode is not None:
        if faxnode.text is None:
            raise BasicDataError("Empty Fax element. Consider removing empty elements", node=faxnode, level=logging.INFO)
        elif faxnode.text.find("\n") > -1:
                raise BasicDataError("Fax element should not contain any line breaks", node=faxnode, level=logging.WARNING)
        else:
            for c in faxnode.text:
                if c in ascii_lowercase or c in ascii_uppercase:
                    raise BasicDataError("Fax element should only contain phone numbers but no text.", node=faxnode, level=logging.WARNING)
                    break
                    
                    
def check_email(hotelrootnode, allotmentrootnode):
    emailnode = hotelrootnode.find("edf:BasicData/edf:Address/edf:Email", ns)
    if emailnode is not None:
        if emailnode.text is None:
            raise BasicDataError("Empty Email element. Consider removing empty elements", node=emailnode, level=logging.INFO)
        elif emailnode.text.find("\n") > -1:
            raise BasicDataError("Email element should not contain any line breaks", node=emailnode, level=logging.WARNING)
            
def check_website(hotelrootnode, allotmentrootnode):
    wwwnode = hotelrootnode.find("edf:BasicData/edf:Address/edf:Website", ns)
    if wwwnode is not None:
        if wwwnode.text is None:
            raise BasicDataError("Empty Website element. Consider removing empty elements", node=wwwnode, level=logging.INFO)
        elif wwwnode.text.find("\n") > -1:
            raise BasicDataError("Website element should not contain any line breaks", node=wwwnode, level=logging.WARNING)

def check_geocodes(hotelrootnode, allotmentrootnode):
    geoinfosnode = hotelrootnode.find("edf:BasicData/edf:GeoInfos", ns)
    if geoinfosnode is None:
        return
    if len(list(geoinfosnode)) == 0:
        raise BasicDataError("Empty GeoInfos element. Consider removing empty elements", node=geoinfosnode, level=logging.INFO)
    geocodenode = hotelrootnode.find("edf:BasicData/edf:GeoInfos/edf:Geocode", ns)
    if geocodenode is None:
        return
    lon = geocodenode.get("Longitude")
    lat = geocodenode.get("Latitude")
    if lon is None or lat is None:
        raise BasicDataError("Longitude or Latitude is not set. Consider removing empty elements", node=geocodenode, level=logging.WARNING)
        
def check_category(hotelrootnode, allotmentrootnode):
    attributenode = hotelrootnode.find("edf:BasicData/edf:Attributes/edf:Attribute[@Name='Category']", ns)
    if attributenode is None:
        raise BasicDataError("Missing Attribute element for hotel category", level=logging.ERROR)
    try:
        float(attributenode.get("Value"))
    except ValueError:
        raise BasicDataError('Attribute element with Name="Category" must have a numeric value', node=attributenode, level=logging.ERROR)
        
def check_airports(hotelrootnode, allotmentrootnode):
    airportnodes = hotelrootnode.findall("edf:BasicData/edf:ArrivalAirports/edf:Airport", ns)
    if len(airportnodes) == 0:
        raise BasicDataError("No arrival airports defined. Without airports the EDF cannot be used for packaging", level=logging.ERROR)
    for airportnode in airportnodes:
        iatacode = airportnode.get("IataCode")
        if iatacode is None: 
            raise BasicDataError("No IataCode set", node=airportnode, level=logging.ERROR)
        if iatacode == '':
            raise BasicDataError("IataCode attribute cannot be empty", node=airportnode, level=logging.ERROR)
        
    
