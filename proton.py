import os
import time
import json
#import paho.mqtt.client as mqtt
from flask import Flask, flash, redirect, render_template, request, session, abort
from jinja2 import StrictUndefined
import sqlite3
from flask_mqtt import Mqtt
from tradfri import tradfriActions
from tradfri import tradfriStatus
import requests

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '192.168.1.6'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

updevices = []

@mqtt.on_connect()
def onconnect(client, userdata, flags, rc):
    mqtt.subscribe('#')

@mqtt.on_message()
def onmessage(client, userdata, msg):
    global updevices
    data = dict(
        topic=msg.topic,
        payload=msg.payload.decode()
    )
    print(data["payload"])
    if data["topic"] == "heartbeat/":
        split = data["payload"].split(":")
        if split[0] not in updevices and split[1] == "1":
            updevices.append(split[0])
            print(updevices)
        elif split[1] == "0":
            updevices.remove(split[0])

title = "JW Systems"

# @app.route('/')
# def index():
#     box0to3 = ["TEST"]
#     return render_template('index.html', box0to3=box0to3)

#def device(data):
#    print(data)

def authenticate(usr, pwd):
    conn = sqlite3.connect('proton.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userdata WHERE username = "'+usr+'"')
    #c.execute('SELECT * FROM userdata WHERE username = %s;') % usr
    data = c.fetchone()
    c.close()
    if data is not None:
        if data[1] == pwd:
            return True
    else:
        return False

def profileget(usr):
    conn = sqlite3.connect('proton.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userdata WHERE username = "'+usr+'"')
    data = c.fetchone()
    c.close()
    print(data)
    return data

def modulesget():
    conn = sqlite3.connect('proton.db')
    c = conn.cursor()
    c.execute('SELECT * FROM modules')
    data = c.fetchall()
    c.close()
    return data

def commercialget():
    time.sleep(0.1)
    devdict = []
    # devs = tradfriStatus.tradfri_get_devices("192.168.0.64", "MjSdr1HQaWBNLs3m")
    # for devid in devs:
    #     tfs1 = tradfriStatus.tradfri_get_lightbulb("192.168.0.64", "MjSdr1HQaWBNLs3m", devid)
    #     if "3311" in tfs1:
    #         dict1 = tfs1["3311"]
    #         name = tfs1["9001"]
    #         for d in dict1:
    #             status = d["5850"]
    #         data = [name, status, devid]
    #         devdict.append(data)
    return devdict

def commercialpost(devid, io):
    tradfriActions.tradfri_power_light("192.168.0.64", "MjSdr1HQaWBNLs3m", devid, io)

def doorpost(value):
    requests.post("http://192.168.2.15/script.php?"+value+"=true")

def sensorsget():
    test = random.randint(0, 100)
    return test

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    elif session.get('username'):
        profile = profileget(session.get('username'))
        print(profile)
        return render_template("panel.html", title=title, profile=profileget(session.get('username')), modules=modulesget(), commercial=commercialget(), updevices=updevices)

@app.route('/login', methods=['POST'])
def do_admin_login():
    # if request.form['password'] == 'password' and request.form['username'] == 'admin':
    if authenticate(request.form['username'], request.form['password']):
        session['logged_in'] = True
        session['username'] = request.form['username']
        return redirect("panel")
    else:
        flash('incorrect')
        return home()

@app.route("/logout")
def logout():
    if session.get('logged_in') != True:
        return redirect("/")
    else:
        session['logged_in'] = False
        session['username'] = ""
        flash("You are now logged out.")
        return home()

# @app.route('/device/<info>', methods=['GET', 'POST'])
# def devices(info):
#     if not session.get('logged_in'):
#         flash("illegal")
#         return render_template("login.html")
#     else:
#         #device(info)
#         return home()

@app.route('/panel')
def panel2():
    if session.get('username') != None:
        profile = profileget(session.get('username'))
        username = session.get('username')
        return render_template("panel.html", title=title, profile=profileget(session.get('username')), modules=modulesget(), commercial=commercialget(), updevices=updevices)
    else:
        return redirect("/")

@app.route('/jsontest', methods = ['POST'])
def jsontest():
    if session.get("username") != "test" or session.get("username") != None:
        profile = profileget(session.get('username'))
        print(profile)
        print(request.json)
        jsondict = json.loads(request.json)
        print("Device: "+jsondict["device"])
        print("Value: "+jsondict["IO"])
        # client.publish("outputdevice/"+jsondict["device"],jsondict["IO"])
        return render_template("panel.html", title=title, profile=profileget(session.get('username')), modules=modulesget(), commercial=commercialget(), updevices=updevices)

@app.route('/commercial', methods = ['POST']) # Philips Hue, Tradfri, etc.
def commercial():
    if session.get("username") != "test" or session.get("username") != None:
        print(request.json)
        jsondict = json.loads(request.json)
        print("Device: "+jsondict["device"])
        print("Value: "+jsondict["IO"])
        commercialpost(jsondict["device"],jsondict["IO"])
        return render_template("panel.html", title=title, profile=profileget(session.get('username')), modules=modulesget(), commercial=commercialget(), updevices=updevices)

@app.route('/door', methods = ['POST']) # Custom door
def door():
    if session.get("username") != "test" or session.get("username") != None:
        print(request.json)
        jsondict = json.loads(request.json)
        print("Door: "+jsondict["value"])
        doorpost(jsondict["value"])
        return render_template("panel.html", title=title, profile=profileget(session.get('username')), modules=modulesget(), commercial=commercialget(), updevices=updevices)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=8080)
    app.jinja_env.undefined = StrictUndefined
