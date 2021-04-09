import time
import signal
import sqlite3
import Adafruit_DHT
dbname= 'sensorData.db'
#Get data from DHT sensor
# Delay in-between sensor readings, in seconds.
DHT_READ_TIMEOUT = 1
#Lib for light sensor
import time
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
#For soil moisture
sys.path.append('./SDL_Adafruit_ADS1x15')
import SDL_Adafruit_ADS1x15


import logging
from waveshare_TSL2591 import TSL2591
sensor = TSL2591.TSL2591()

def getSoilMoisture():
    ADS1115 = 0x01  # 16-bit ADC
    gain = 4096  # +/- 4.096V
    sps = 250  # 250 samples per second
    adc = SDL_Adafruit_ADS1x15.ADS1x15(ic=ADS1115)

    voltsCh0 = adc.readADCSingleEnded(0, gain, sps) / 1000
    rawCh0 = adc.readRaw(0, gain, sps) 
    #print ("Channel 0 =%.6fV raw=0x%4X dec=%d" % (voltsCh0, rawCh0, rawCh0))
    soil=int(rawCh0)
    #print(soil)
    return soil

def getlux():
    lux = sensor.Lux
    return lux

def getDHTdata():
    dht11_sensor = Adafruit_DHT.DHT11
    #get lux
    #lux = sensor.Lux
    # Initial the dht device, with data pin connected to:
    DHT_DATA_PIN = 4
    humidity, temperature = Adafruit_DHT.read_retry(dht11_sensor, DHT_DATA_PIN)
    if humidity is not None and temperature is not None:
        humidity = round(humidity)
        temperature = round(temperature, 1)
        #logData (temperature, humidity, lux)
    return temperature, humidity
# log sensor data on database
def logData (temperature, humidity, lux, soilm):    
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?), (?), (?))", (temperature, humidity, lux, soilm))
    conn.commit()
    conn.close()
    
# display database data (testing only)
def displayData():
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    print ("\nEntire database contents:\n")
    for row in curs.execute("SELECT * FROM DHT_data"):
        print (row)
    conn.close()
# main function
def main():
    while True:
        temp, hum = getDHTdata()
        lux = getlux()
        soilm = getSoilMoisture()
        logData (temp, hum, lux, soilm)
        time.sleep(DHT_READ_TIMEOUT)
    #displayData()
        
    #isplayData()
# Execute program 
main()