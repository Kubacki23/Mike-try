'''
Author: Phil Deierling
Date: 10-28-2024
Description: Example of how to use Streamlit with MQTT and updating widgets using fragments.
Version: 1.0
Log: 10-28-2024 first submission
'''

'''
Run this script by calling the Streamlit module in a terminal, e.g., 
"streamlit run streamlitTest.py"
'''

# Import required modules
import streamlit as st
import time
import numpy as np
from paho.mqtt import client as mqtt_client
import paho.mqtt.subscribe as subscribe

# Function to connect to the MQTT broker
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(broker, port, keepalive=360)
    return client

# The below function will be cached, so it is only called one time
@st.cache_resource
def mqtt_setup():
    # Connect to mqqt and set an on message callback
    client = connect_mqtt()
    return client


if "pico_msg" not in st.session_state:
    st.session_state.pico_msg = "-1"

if "placeholder1" not in st.session_state:
    st.session_state.placeholder1 = None

if "placeholder2" not in st.session_state:
    st.session_state.placeholder2 = None

if "print_status" not in st.session_state:
    st.session_state.print_status = "NA"


# MQTT setup
#broker = '192.168.86.73'
broker = 'localhost'
port = 1883
client_id = 'python-mqtt-{}'.format(np.random.randint(0, 100))
topic_sub = 'mqtt/pico_data'       # topic to subscribe to 
topic_pub = 'mqtt/streamlit_data'  # topic to publish to 


# This will run automatically every 3 seconds without causing an entire app rerun
@st.fragment(run_every=3)
def update_values():
    st.session_state.placeholder1.text("SOME CHANGING VALUE:\n" + str(np.random.rand()))

    # Checking to see if there is a message manually
    msg = subscribe.simple(topic_sub, hostname=broker)
    st.session_state.pico_msg = msg.payload.decode()
    st.session_state.placeholder2.text("Message from the pico:\n" + st.session_state.pico_msg)

# Function to PUBLISH messages on the MQTT broker
def publish(): # This will run on every app interation by default
    # get the value of the slider to send to the PICO
    msg = str(st.session_state.myslider_val)
    result = client.publish(topic_pub, msg)
    status = result[0]
    
    if status == 0:
        print_status = 'Sent the message: {} to topic {}'.format(msg, topic_pub)
    else:
        print_status = 'FAILED to send Slider TO the Pico:'
    
    st.session_state.print_status = print_status



st.title('Example of MQTT publishing and subscribing w/ Streamlit.')
st.error('Publishing occurs whenever the slider value is changed.')
st.warning('Subscribing happens whenever there is a new message available.')
    
# create two columns for the layout
col1, col2 = st.columns(2)
with col1:
    # create a radio widget (this will cause an script rerun when a selection is made which will rerun the app.
    st.radio('System State (does nothing)', ['Off', 'On'], help='This could also be used to push a message to the Pico')
    
    # Placeholders to hold text later
    st.session_state.placeholder1 = st.empty()
    st.session_state.placeholder2 = st.empty()

with col2:    
    st.slider("Update Interval", min_value=1, max_value=10, value=None, step=None, 
              format=None, key="myslider_val", help=None, on_change=publish, args=None, kwargs=None, 
              disabled=False, label_visibility="visible")
    
    st.text(st.session_state.print_status)


# Start running the update value function
client = mqtt_setup()
update_values()