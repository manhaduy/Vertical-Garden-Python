from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import os
import threading
import time
import datetime
import board
from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)
import sqlite3
import RPi. GPIO as GPIO

#Relay setup
GPIO.setwarnings(False)
Relaypin = 17    #Relay pin
RelaySts = 0 #Relay Status
#Set up relay pin
GPIO.setup(Relaypin, GPIO.OUT)
GPIO.output(Relaypin, GPIO.LOW)#Init the state by turn off relay

# Retrieve data from database
def getData():
    conn=sqlite3.connect('../sensorData.db')
    curs=conn.cursor()
    for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
        time = str(row[0])
        temp = row[1]
        hum = row[2]
        lux = row[3]
        soilm = row[4]
    #conn.close()
    return time, temp, hum, lux, soilm

def getHistData (numSamples):
    conn=sqlite3.connect('../sensorData.db')
    curs=conn.cursor()
    curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
    data = curs.fetchall()
    dates = []
    temps = []
    hums = []
    luxs = []
    soilms = []
    for row in reversed(data):
        dates.append(row[0])
        temps.append(row[1])
        hums.append(row[2])
        luxs.append(row[3])
        soilms.append(row[4])
        
    return dates, temps, hums, luxs, soilms

def maxRowsTable():
    conn=sqlite3.connect('../sensorData.db')
    curs=conn.cursor()
    for row in curs.execute("select COUNT(temp) from  DHT_data"):
        maxNumberRows=row[0]
    return maxNumberRows

#initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
    numSamples = 100

# main route 
@app.route("/")
def index():    
    time, temp, hum, lux, soilm = getData()
    actuator = Relaypin
    RelaySts = GPIO.input(Relaypin)
    WaterSts = 0
    #Lux combine with relay
#    if lux < 5:
#        GPIO.output(actuator, GPIO.HIGH)
#        RelaySts = "Watering"
#    elif lux > 5:
#        GPIO.output(actuator, GPIO.LOW)
#        RelaySts = "Not Watering"
    #Soil moisture combine with relay
#    if soilm > 19000:
#        GPIO.output(actuator, GPIO.HIGH)
#        RelaySts = "Watering"
 #   elif soilm < 16000:
 #       GPIO.output(actuator, GPIO.LOW)
 #       RelaySts = "Not Watering"
    
    
    #Lux and Soil moisture combine with relay
    if  soilm < 16000 or lux < 5:
        GPIO.output(actuator, GPIO.HIGH)
        RelaySts = 1
        WaterSts = "Watering"
        
    elif soilm > 19000 or lux > 5:
        GPIO.output(actuator, GPIO.LOW)
        RelaySts = 0
        WaterSts = "Not Watering"
        
    templateData = {
        'time': time,
        'temp': temp,
        'hum': hum,
        'lux': lux,
        'soilm': soilm,
        'WaterSts' : WaterSts,
        'RelaySts' : RelaySts
    }
    return render_template('index.html', **templateData)

@app.route("/<deviceName>/<action>")
def action(deviceName, action):

    WaterSts = 0
    #if deviceName == 'RelayBtn':
    actuator = Relaypin
    if action == "on":
        GPIO.output(actuator, GPIO.HIGH)
        RelaySts = 1
        WaterSts = "Watering"
    if action == "off":
        GPIO.output(actuator, GPIO.LOW)
        RelaySts = 0
        WaterSts = "Not Watering"
    time, temp, hum, lux, soilm = getData()

        
    #RelaySts = GPIO.input(Relaypin)

    templateData = {
      'title' : 'GPIO input Status!',
        'time': time,
        'temp': temp,
        'hum': hum,
        'lux': lux,
        'soilm': soilm,
      'WaterSts' : WaterSts,
      'RelaySts' : RelaySts
      }
    return render_template('index.html', **templateData)

@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples 
    numSamples = int(request.form['numSamples'])
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    
    time, temp, hum, lux, soilm = getData()
    
    templateData = {
      'time' : time,
      'temp': temp,
      'hum': hum,
      'lux': lux,
      'soilm': soilm,
      'numSamples'  : numSamples
    }
    return render_template('index.html', **templateData)

@app.route('/plot/temp')
def plot_temp():
    times, temps, hums, lux, soilm = getHistData(numSamples)
    ys = temps
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Temperature [°C]")
    axis.set_xlabel("Samples")
    axis.grid(True)
    xs = range(numSamples)
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/hum')
def plot_hum():
    times, temps, hums, lux, soilm = getHistData(numSamples)
    ys = hums
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Humidity [%]")
    axis.set_xlabel("Samples")
    axis.grid(True)
    xs = range(numSamples)
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
