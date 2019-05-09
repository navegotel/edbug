#!/usr/bin/env python3
"""a debugger for Peakwork HotelEDF data deliveries"""
import os
import importlib
import plugins
import sys
import logging
import datetime
import glob
import shutil
import xml.etree.ElementTree as ET
from inspect import getmembers, isfunction
from zipfile import ZipFile, BadZipFile
from edferrors import HotelEdfError, AllotmentEdfError, BasicDataError, SellingDataError, ChargeBlockError, OccupancyError, RoomError
from edfns import ns

__version__ = "1.2.1"

class Progressbar(object):
    def __init__(self, maxval, width=50, show_percent=True, barchar='»'):
        self.maxval = maxval
        self.width = width
        self._value = 0
        self.barchar = barchar
        self.show_percent = show_percent
        self.paint()
        
    def __del__(self):
        print("\n")
        
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self,value):
        self._value = value
        self.paint()
    
    @property
    def percent(self):
        return '{0:5.2f}'.format(self._value/self.maxval*100)
    
    def paint(self):
        try:
            progress = int(self._value/self.maxval*self.width)
        except ZeroDivisionError:
            pass
        else:
            bar = self.barchar * progress
            filler = ' ' * (self.width - progress)
            if self.show_percent is True:
                output = '\r[{0}{1}] {2}% '.format(bar,filler,self.percent)
            else:
                output = '\r[{0}{1}] '.format(bar,filler)
            sys.stdout.write(output)
        
    def inc(self):
        self._value += 1
        self.paint()


def get_workdir(workdir):
    if workdir is None:
        return os.path.join(os.path.split(__file__)[0], 'tmp')
    else:
        return workdir
        
def get_hotelonlydir(workdir):
    return os.path.join(workdir, 'hotels/hotelonly')
    
def get_allotmentdir(workdir):
    return os.path.join(workdir, 'hotels/hotelonly/allotment')
    
def unpackzipfile(zipfilename, workdir=None):
    workdir = get_workdir(workdir)
    try:
        with ZipFile(zipfilename) as zf:
            zf.extractall(path=workdir)
    except BadZipFile as e:
        logging.error("The zip file seems to have some issues. Check the work directory if all EDF files have been successfully unpacked and no folders are missing")
    else:
        if os.path.isdir(os.path.join(workdir, 'hotels/hotelonly')) is False:
            logging.critical("Wrong folder structure. No hotels/hotelonly found. Exiting")
            sys.exit()
        if os.path.isdir(os.path.join(workdir, 'hotels/hotelonly/allotment')) is False:
            logging.critical("Wrong folder structure. No hotels/hotelonly/allotment found. Exiting")
            sys.exit()

def log_exception(e, header, counters, functionname, debug=False):
    highestlevel = logging.DEBUG
    for errormsg in e.messages:
        try:
            counters["{0}, {1}".format(type(e).__name__, logging.getLevelName(errormsg.level))] += 1
        except KeyError:
            counters["{0}, {1}".format(type(e).__name__, logging.getLevelName(errormsg.level))] = 1
        if errormsg.level > highestlevel:
            highestlevel = errormsg.level
    logging.log(highestlevel, header)
    if debug is True:
        logging.log(errormsg.level, "In function {0}:".format(functionname))
    for errormsg in e.messages:
        logging.log(errormsg.level, errormsg.message)
        if errormsg.snippet is not None:
            logging.log(errormsg.level, errormsg.snippet)

def iterate(workdir=None, debug=False):
    workdir = get_workdir(workdir)
    hotelonlydir = get_hotelonlydir(workdir)
    allotmentdir = get_allotmentdir(workdir)
    edfnames = glob.glob(os.path.join(hotelonlydir, "*.xml"))
    progressbar = Progressbar(len(edfnames))
    logging.info('{0} files found in {1}'.format(len(edfnames), hotelonlydir))
    allotmentnames = glob.glob(os.path.join(allotmentdir, "*.xml"))
    logging.info('{0} files found in {1}'.format(len(allotmentnames), allotmentdir))
    if len(edfnames) != len(allotmentnames):
        logging.warning('There are different numbers of HotelEDF and AllotmentEDF')
    functions = list()
    for l in plugins.__all__:
        m = importlib.import_module("plugins.{0}".format(l))
        functions += [o for o in getmembers(m) if isfunction(o[1])]
    counters = dict()
    for fqn in edfnames:
        progressbar.inc()
        base, filename = os.path.split(fqn)
        try:
            hotelroot = ET.parse(fqn)
            allotmentfilename = os.path.join(allotmentdir, filename)
            allotmentroot = None
            if os.path.exists(allotmentfilename):
                try:
                    allotmentroot = ET.parse(allotmentfilename)
                except ET.ParseError:
                    logging.error("AllotmentEDF {0} could not be parsed. May be file is empty or xml is not valid".format(allotmentfilename))
            else:
                logging.error('Missing AllotmentEDF for {0}'.format(filename))
        except ET.ParseError:
            logging.error("HotelEDF {0} could not be parsed. Either the file is empty or xml is not valid".format(fqn))
        else: 
            basicdatanode = hotelroot.find("edf:BasicData", ns)
            if basicdatanode is None:
                logging.error("Missing BasicData section in HotelEDF {0}".format(fqn))
            else:
                code = basicdatanode.get("Code")
                tocode = basicdatanode.get("TourOperatorCode")
                filekey = basicdatanode.get("FileKey")
                separator = ""
                if filekey is not None:
                    separator = "_"
                else:
                    filekey = ""
                tmpl = "EDF----{0}-{1}{2}{3}.xml"
                correctfilename = tmpl.format(tocode, code, separator, filekey)
                if correctfilename != filename:
                    logging.warning("Filename {0} does not match naming convention. Should be {1}".format(filename, correctfilename))
            for function in functions:
                try:
                    if function[0].startswith("hotel"):
                        function[1](hotelroot)
                    elif function[0].startswith("allotment"):
                        function[1](allotmentroot)
                    elif function[0].startswith("room"):
                        for roomnode in hotelroot.findall("edf:SellingData/edf:Rooms/edf:Room", ns):
                            roomcode = roomnode.get("Code")
                            try:
                                function[1](roomnode)
                            except RoomError as e:
                                log_exception(e, "in room {0} of HotelEDF {1}:".format(roomcode, fqn), counters, function[0], debug=debug)
                            except ChargeBlockError as e:
                                log_exception(e, "in ChargeBlock in Room {0} of HotelEDF {1}:".format(roomcode, fqn), counters, function[0], debug=debug)
                            except OccupancyError as e:
                                log_exception(e, "in Occupancy in Room {0} of HotelEDF {1}:".format(roomcode, fqn), counters, function[0], debug=debug)
                            except (HotelEdfError, AllotmentEdfError, SellingDataError):
                                pass
                    else:
                        function[1](hotelroot, allotmentroot)
                except HotelEdfError as e:
                    log_exception(e, "in HotelEDF {0}:".format(fqn), counters, function[0], debug=debug)
                except AllotmentEdfError as e:
                    log_exception(e, "in AllotmentEDF {0}:".format(allotmentfilename), counters, function[0], debug=debug)
                except BasicDataError as e:
                    log_exception(e, "in BasicData section of HotelEDF {0}:".format(fqn), counters, function[0], debug=debug)
                except SellingDataError as e:
                    log_exception(e, "in SellingData section of HotelEDF {0}:".format(fqn), counters, function[0], debug=debug)
                except RoomError as e:
                    log_exception(e, "in the rooms of HotelEDF {0}:".format(fqn), counters, function[0], debug=debug)
                except ChargeBlockError as e:
                    log_exception(e, "in ChargeBlock in Room {0} of HotelEDF {1}:".format(e.room, fqn), counters, function[0], debug=debug)
                except OccupancyError as e:
                    log_exception(e, "in Occupancy in Room {0} of HotelEDF {1}:".format(e.room, fqn).format(e.room, fqn), counters, function[0], debug=debug)
    for key, value in counters.items():
        logging.info("{0}: {1}".format(key, value))
                        
def cleanup(workdir):
    workdir = get_workdir(workdir)
    try:
        shutil.rmtree(workdir)
    except FileNotFoundError:
        pass

if __name__ == '__main__':
    for prefix, uri in ns.items():
        ET.register_namespace(prefix, uri)
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-Z', '--zipfile', help='Name of the EDF zip file')
    ap.add_argument('-F', '--folder', help='Folder with EDF files. if -Z option is used the file is unpacked into this folder. If the folder exists it will be removed with all its contents previously')
    ap.add_argument('-L', '--logfile', default=datetime.date.today().strftime('report_%Y-%m-%d.txt'), help='Name of the Log file debug messages are written to')
    ap.add_argument('-LL', '--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default="INFO", help='Only messages with this level or higher are logged to the report.')
    ap.add_argument('-LM', '--logmode', choices=['a', 'w'], default='a', help='a for appending to existing file, w for overriding an existing file.')
    ap.add_argument('-CU', '--cleanup', action='store_true', help="delete work directory at the end.")
    ap.add_argument('-DG', '--debug', action='store_true', help="Log additional debug information. This currently only logs the the name of the function that raised the error.")
    args = ap.parse_args()
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    logformat = '%(asctime)s %(levelname)-8s %(message)s'
    if not isinstance(numeric_level, int):
        numeric_level = getattr(logging, 'INFO', None)
    logging.basicConfig(filename=args.logfile, filemode=args.logmode, level=numeric_level, format=logformat)
    if args.zipfile is not None:
        cleanup(args.folder)
        unpackzipfile(args.zipfile, workdir=args.folder)
    iterate(workdir=args.folder, debug=args.debug)
    if args.cleanup is True:
        cleanup(args.folder)
    
