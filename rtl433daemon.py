#!/usr/bin/python
import json
import urllib2
import os
from sh import tail
import subprocess
from time import sleep
import logging
# change serverip and portnumer in below line to reflect your own installation
servercall = "http://127.0.0.1:8080"
rtl_433_logfile = "/var/log/rtl_433"
rtl_433_logpath = "/var/log"
deamon_configfile = '/etc/checkdevice_config.json'


# Server and portnumber requests have to be send to

###################
class RTL_433_detect_class:  # fills variable data with values from rtl_433
    def __init__(self):
        self.data = {'Info': 'rtl_433 decoded data fields'}

        return

    def winddirection(self, winddata):
        wdata = int(winddata)
        self.data['WD'] = 'N'
        if wdata > 11 and wdata < 34:
            self.data['WD'] = 'NNE'
        elif wdata >= 34 and wdata < 56:
            self.data['WD'] = 'NE'
        elif wdata >= 56 and wdata < 79:
            self.data['WD'] = 'ENE'
        elif wdata >= 79 and wdata < 101:
            self.data['WD'] = 'E'
        elif wdata >= 101 and wdata < 124:
            self.data['WD'] = 'ESE'
        elif wdata >= 124 and wdata < 146:
            self.data['WD'] = 'SE'
        elif wdata >= 146 and wdata < 169:
            self.data['WD'] = 'SSE'
        elif wdata >= 169 and wdata < 191:
            self.data['WD'] = 'S'
        elif wdata >= 191 and wdata < 214:
            self.data['WD'] = 'SSW'
        elif wdata >= 214 and wdata < 236:
            self.data['WD'] = 'SW'
        elif wdata >= 236 and wdata < 259:
            self.data['WD'] = 'WSW'
        elif wdata >= 259 and wdata < 281:
            self.data['WD'] = 'W'
        elif wdata >= 281 and wdata < 304:
            self.data['WD'] = 'WNW'
        elif wdata >= 304 and wdata < 326:
            self.data['WD'] = 'NW'
        elif wdata >= 326 and wdata < 349:
            self.data['WD'] = 'NNW'
        return

    # nothing to do for now...

    #	1 Pressure (Bar) 0.0 	      	     nvalue=BAR (TBC)
    #	80 TEMP          0.0     	     svalue=TEMP
    #	81 HUM           1		     nvalue=HUM svalue=1 to 3
    #	82 TEMP_HUM      0.0;50;1 	     svalue=TEMP;HUM;HUM_STATUS
    #	84 TEMP_HUM_BARO 0.0;50;1;1010;1    svalue=TEMP;HUM;HUM_STATUS;BARO;BARO_FCST
    #	85 RAIN          0;0		     svalue=RAIN;Rain in mm/h
    #	86 WIND          0;N;0;0;0;0  	     svalue=WIN_SPD;WIND_DIR;?;?;?;?
    def proces(self, msg):  # returns 0 of no vallid decode
        # fill data()variables when available
        logger.debug(msg)
        self.data.clear()  # clear data array
        self.data['Battery'] = "255"  # no battery
        # Process devices, each should be checked as there is no defined standard

        # PROLOGUE SENSORS
        if line[20:28] == 'Prologue':  # ID for prologue is protocolname and ID
            # so Prologue09 is a vallid name
            self.data['Battery'] = "255"  # set no battery value
            msgdata = msg.split()
            for idx, member in enumerate(msgdata):
                if member == 'Sensor':
                    self.data['Device_id'] = 'PrologueID' + str(msgdata[idx + 1])
                elif member == 'Temperature':
                    self.data['Temperature'] = str(msgdata[idx + 1])
                elif member == 'Humidity':
                    self.data['Humidity'] = str(msgdata[idx + 1])
                elif member == 'Battery':
                    if msgdata[idx + 1] == 'Ok':
                        self.data['Battery'] = "100"
                    else:
                        self.data['Battery'] = "5"
                        # logger.debug(self.data
            return 1
        # logger.debug(line[20:27])
        # 2015-10-07 17:57:44 LaCrosse TX Sensor 7e: Temperature 19.5 C / 67.1 F
        if line[20:27] == 'LaCross':  # ID for LaCrosse is protocolname and ID+type
            # this is as all messages is send as SEPERATE message, not combined
            # so LaCrosse09H is a vallid name
            self.data['Battery'] = "255"  # set no battery value
            msgdata = msg.split()
            for idx, member in enumerate(msgdata):
                if member == 'Sensor':
                    # correct trailing :
                    msgdata[idx + 1] = msgdata[idx + 1].strip(':')
                    self.data['Device_id'] = 'LaCrosseID' + str(msgdata[idx + 1])

                elif member == 'Temperature':
                    self.data['Temperature'] = str(msgdata[idx + 1])
                    self.data['Device_id'] = self.data['Device_id'] + 'T'
                elif member == 'Humidity':
                    self.data['Humidity'] = str(msgdata[idx + 1])
                    self.data['Device_id'] = self.data['Device_id'] + 'H'
                elif member == 'Battery':
                    if msgdata[idx + 1] == 'Ok':
                        self.data['Battery'] = "100"
                    else:
                        self.data['Battery'] = "5"
            logger.debug(self.data)
            return 1
        # Electo SENSORS
        # 2015-10-07 20:09:31 AlectoV1 Wind Sensor 44: Wind speed 2 units = 0.40 m/s: Wind gust 3 units = 0.60 m/s: Direction 135 degrees: Battery OK
        # WB = Wind bearing (0-359)
        # WD = Wind direction (S, SW, NNW, etc.)
        # WS = Wind speed [km/h]
        # WG = Gust [km/h]
        if line[20:28] == 'AlectoV1':  # ID for prologue is protocolname and ID
            # so AlectoV102 is a vallid name
            self.data['Battery'] = "255"  # set no battery value
            msgdata = msg.split()
            for idx, member in enumerate(msgdata):
                if member == 'Sensor':
                    msgdata[idx + 1] = msgdata[idx + 1].strip(':')
                    self.data['Device_id'] = 'AlectoV1ID' + str(msgdata[idx + 1])

                elif member == 'speed':
                    self.data['WS'] = str(msgdata[idx + 1])
                    self.data['Device_id'] = self.data['Device_id'] + 'W'
                # correct for same device wind and temp but different streams
                elif member == 'gust':
                    self.data['WG'] = str(msgdata[idx + 1])
                elif member == 'Direction':
                    self.data['WB'] = str(msgdata[idx + 1])
                    self.winddirection(msgdata[idx + 1])


                elif member == 'speed':
                    self.data['WS'] = str(msgdata[idx + 1])

                elif member == 'Rain':
                    self.data['Rain'] = str(msgdata[idx + 1])
                elif member == 'Temperature':
                    self.data['Temperature'] = str(msgdata[idx + 1])
                elif member == 'Humidity':
                    self.data['Humidity'] = str(msgdata[idx + 1])
                elif member == 'Battery':
                    if msgdata[idx + 1] == 'Ok' or msgdata[idx + 1] == 'OK':
                        self.data['Battery'] = "100"
                    else:
                        self.data['Battery'] = "5"
            logger.debug(self.data)
            return 1

        # 2015-10-07 20:05:30 AlectoV1 Rain Sensor 133: Rain 86.75 mm/m2: Battery OK

        return 0  # No devices processed


# TO DO: read devices domotics and check if they all exist in config of this script
class RTL_433_Domoticz_class:
    def __init__(self, pass_servercall):
        self.hardwareid = 9999
        self.servercall = pass_servercall
        # self.jsontablefilename=os.path.dirname(os.path.realpath(__file__)) + os.sep+deamon_configfile
        self.jsontablefilename = deamon_configfile

        try:
            with open(self.jsontablefilename) as data_file:
                self.devicelist = json.load(data_file)
        except:
            logger.error("Failed loading " + self.jsontablefilename)
            pass
        if not self.check_existance_RTL_433_in_DOMOTICZ():
            self.create_hardware_RTL_433()  # after create check again!
            if not self.check_existance_RTL_433_in_DOMOTICZ():  # Check once more
                logger.debug(
                    "Halting application as hardware RTL_433 cannot be created. Please check server parameters")
                raise SystemExit(0)  # Exit app as device cannot be created, logging to it would make no sense

    def write_jsontable(self):
        with open(self.jsontablefilename, 'w') as fp:
            json.dump(self.devicelist, fp)

    def add_newdevice(self, device_id, domoticz_id):
        # d['mynewkey'] = 'mynewvalue'
        self.devicelist[str(device_id)] = str(domoticz_id)
        logger.debug(self.devicelist)
        self.write_jsontable()

    def create_device_domoticz(self, device_id, typeid):

        #	1 Pressure (Bar) 0.0 	      	     nvalue=BAR (TBC)
        #	80 TEMP          0.0     	     svalue=TEMP
        #	81 HUM           1		     nvalue=HUM svalue=1 to 3
        #	82 TEMP_HUM      0.0;50;1 	     svalue=TEMP;HUM;HUM_STATUS
        #	84 TEMP_HUM_BARO 0.0;50;1;1010;1    svalue=TEMP;HUM;HUM_STATUS;BARO;BARO_FCST
        #	85 RAIN          0;0		     svalue=RAIN;Rain in mm/h
        #	86 WIND          0;N;0;0;0;0  	     svalue=WIN_SPD;WIND_DIR;?;?;?;?
        #	87 UV            0;0		     svalue= (TBC)
        #	249 TypeAirQuality    0	     nvalue=PPM

        logger.debug('Creating Device RTL_433 on Domotics server ' + servercall)
        request = self.servercall + "/json.htm?type=createvirtualsensor&idx=" + self.hardwareid + '&sensortype=' + str(
            typeid)

        try:
            search_response = urllib2.urlopen(request)
            search_results = search_response.read()
            results = json.loads(search_results)
            if results.get(u'status') == 'OK':
                createid = self.get_latest_deviceid()

                if createid:
                    logger.debug('Successful creating device ', createid)
                    ################## Write index
                    # self.add_newdevice(self,device_id,createid)
                    self.devicelist[device_id] = str(createid)
                    logger.debug(self.devicelist)
                    self.write_jsontable()
                    return 1  # Result OK
                else:
                    logger.debug('ERROR creating device. skipping for now!')
                    return 0
        except:
            logger.error("Time Out URL (1)")
            pass
        logger.debug('ERROR creating device. Skipping for now!')
        return 0  # Result NOK

    def get_latest_deviceid(self):  # FALSE = does not exist TRUE = exists
        deviceid = 0
        request = self.servercall + "/json.htm?type=devices&used=false"
        try:
            search_response = urllib2.urlopen(request)
            search_results = search_response.read()
        except:
            logger.error("Time Out URL (2)")
            # return 0
            pass
        results = json.loads(search_results)
        for item in results.get(u'result', []):
            if item.get(u'HardwareName') == 'RTL_433':
                if int(item.get(u'idx')) > deviceid:
                    deviceid = int(item.get(u'idx'))
        return deviceid

    def check_existance_RTL_433_in_DOMOTICZ(self):  # FALSE = does not exist TRUE = exists

        request = self.servercall + "/json.htm?type=hardware"
        try:
            search_response = urllib2.urlopen(request, timeout=4)
        except urllib2.URLError, e:
            logger.error("Time Out URL (3)")
            pass
            return 0
        search_results = search_response.read()
        results = json.loads(search_results)
        for item in results.get(u'result', []):
            if item.get(u'Name') == 'RTL_433':
                self.hardwareid = item.get(u'idx')
                return 1  # Does exist
        logger.debug('No hardware RTL_433 found in Domoticz')
        return 0  # Does not exist!

    def create_hardware_RTL_433(self):
        logger.debug('Creating Hardware RTL_433 on Domotics server ' + servercall)
        request = self.servercall + "/json.htm?type=command&param=addhardware&htype=15&port=1&name=RTL_433&enabled=true"
        logger.debug(request)
        try:
            search_response = urllib2.urlopen(request, timeout=4)
            search_results = search_response.read()
            results = json.loads(search_results)
            if results.get(u'status') == 'OK':
                logger.debug('Successful')
            return 1  # Result OK
        except:
            logger.error("Time Out URL (4)")
            pass

        logger.debug('ERROR creating hardware RTL_433')
        return 0  # Result NOK

    # def read_conversion_Table(self)
    def GetWorkingPath(self):
        return os.path.dirname(os.path.realpath(__file__)) + os.sep

    # Detect what device the data is in domotics language
    def what_domotics_device(self, data):
        #	1 Pressure (Bar) 0.0 	      	     nvalue=BAR (TBC)
        #	80 TEMP          0.0     	     svalue=TEMP
        #	81 HUM           1		     nvalue=HUM svalue=1 to 3
        # Humidity_status can be one of:
        # 0=Normal 60-25
        # 1=Comfortable 45-55%
        # 2=Dry <25
        # 3=Wet >60
        # /json.htm?type=command&param=udevice&idx=IDX&nvalue=45&svalue=HUM;HUM_STAT
        #	82 TEMP_HUM      0.0;50;1 	     svalue=TEMP;HUM;HUM_STATUS
        #	84 TEMP_HUM_BARO 0.0;50;1;1010;1    svalue=TEMP;HUM;HUM_STATUS;BARO;BARO_FCST
        #	85 RAIN          0;0		     svalue=RAIN;Rain in mm/h
        #	86 WIND          0;N;0;0;0;0  	     svalue=WIN_SPD;WIND_DIR;?;?;?;?
        # first try all multiple devices, than ending with single devices


        device_id = 0
        if 'Temperature' in data and 'Humidity' in data and 'Pressure' in data:
            device_id = "84"  # if entry does not exist this step wil not execute
            return device_id
        elif 'Temperature' in data and 'Humidity' in data:
            device_id = "82"  # if entry does not exist this step wil not execute
            return device_id

        elif 'Temperature' in data and not 'Humidity' in data:
            # 80 TEMP
            device_id = "80"  # if entry does not exist this step wil not execute
            return device_id

        elif 'Humidity' in data and not 'Temperature' in data:
            device_id = "81"  # if entry does not exist this step wil not execute
            return device_id

        elif 'Rain' in data:
            # 85 RAIN
            device_id = "85"  # if entry does not exist this step wil not execute
            return device_id
        elif 'WB' in data:  # 86 WIND
            device_id = "86"  # if entry does not exist this step wil not execute
            return device_id
        return device_id  # should not come here!

    def push_data(self, data):
        # self.devicelist[Device_id]="123"
        try:
            domoticzid = self.devicelist[data['Device_id']]
        except:
            domoticzid = None

        if domoticzid == None:
            # createdevice
            domoticzdevice = self.what_domotics_device(data)
            logger.debug("CREATE NEW DEVICE", data)

            if domoticzdevice:
                self.create_device_domoticz(data['Device_id'], domoticzdevice)
            try:
                domoticzid = self.devicelist[data['Device_id']]
            except:
                logger.error("Could not read device_id from dictionary")
                domoticzid = 0  # just set false
        if domoticzid:
            logger.debug("pushing data")  # Watch that Battery =0-100 or 255 of no value
            # check what device it is see domoticzdevice
            # based on what device set updatestring
            # also check if battery info is supplied
            # watch for errors
            domoticzdevice = rtl433.what_domotics_device(data)
            if domoticzdevice == "82":  # Temp Hum
                # Humidity_status can be one of:
                # 0=Normal 60-25
                # 1=Comfortable 45-55%
                # 2=Dry <25
                # 3=Wet >60
                if data['Humidity'] > 60:
                    data['Comfort'] = '3'
                elif data['Humidity'] < 25:
                    data['Comfort'] = '2'
                elif data['Humidity'] > 45 and data['Humidity'] < 55:
                    data['Comfort'] = '1'
                else:
                    data['Humidity'] = '0'
                # /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=TEMP;HUM;HUM_STAT
                request = self.servercall + "/json.htm?type=command&param=udevice&idx=" + str(
                    domoticzid) + "&nvalue=0&svalue=" + data['Temperature'] + ";" + data['Humidity'] + ";" + data[
                              'Comfort'] + "&battery=" + data['Battery']
            elif domoticzdevice == "80":
                request = self.servercall + "/json.htm?type=command&param=udevice&idx=" + str(
                    domoticzid) + "&nvalue=0&svalue=" + data['Temperature'] + "&battery=" + data['Battery']
            elif domoticzdevice == "81":
                if data['Humidity'] > 60:
                    data['Comfort'] = '3'
                elif data['Humidity'] < 25:
                    data['Comfort'] = '2'
                elif data['Humidity'] > 45 and data['Humidity'] < 55:
                    data['Comfort'] = '1'
                else:
                    data['Humidity'] = '0'
                # http://192.168.99.212:8080/json.htm?type=command&param=udevice&idx=8&nvalue=45&svalue=45;0
                request = self.servercall + "/json.htm?type=command&param=udevice&idx=" + str(domoticzid) + "&nvalue=" + \
                          data['Humidity'] + "&svalue=" + data['Humidity'] + ";" + data['Comfort'] + "&battery=" + data[
                              'Battery']
            elif domoticzdevice == "86":  # WIND
                # /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=WB;WD;WS;WG;22;24
                request = self.servercall + "/json.htm?type=command&param=udevice&idx=" + str(
                    domoticzid) + "&nvalue=0&svalue=" + data['WB'] + ";" + data['WD'] + ";" + data['WS'] + ";" + data[
                              'WG'] + ";0;0&battery=" + data['Battery']
                logger.debug(request)

            elif domoticzdevice == "85":  # Rain
                request = self.servercall + "/json.htm?type=command&param=udevice&idx=" + str(
                    domoticzid) + "&nvalue=0&svalue=0;" + data['Rain'] + "&battery=" + data['Battery']

            logger.debug(request)
            try:
                search_response = urllib2.urlopen(request, timeout=4)
                search_results = search_response.read()
                results = json.loads(search_results)
                if results.get(u'status') == 'OK':
                    # logger.debug('Successful')
                    return 1  # Result OK
            except:
                logger.error("Time Out URL (5)")
                pass

        else:
            logger.debug("push skipped. No device can be created")


#######################################################################

# object initcode checks if server is listening, otherwise exits
# also sets device RTL_433 to be virtual hardware in Domoticz
logger = logging.getLogger('rtl433daemon')
hdlr = logging.FileHandler(rtl_433_logpath + "/rtl433daemon.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

logger.debug("looking for " + '/etc' + os.sep + deamon_configfile)

logger.debug("Starting connection with Domoticz")
rtl433 = RTL_433_Domoticz_class(servercall)  # See top document for servercall
rtlwrapper = RTL_433_detect_class()
# Now run main app
logger.debug("Init OK. Hardware ID RTL_433 device in Domoticz =" + str(rtl433.hardwareid))
logger.debug("Running app")

subprocess.Popen(["/usr/bin/startrtl.sh"])
sleep(3)

logger.debug("processing")

for line in tail("-f", rtl_433_logfile, _iter=True):
    # logger.debug(line),
    if rtlwrapper.proces(line):  # fill rtlwrapper.data structure
        rtl433.push_data(rtlwrapper.data)
logger.debug("Stopped program")
