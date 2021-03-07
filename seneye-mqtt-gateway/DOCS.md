# Home Assistant Add-on: Seneye MQTT Gateway

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Find the "Seneye LDE to MQTT Gateway" add-on and click it.
3. Click on the "INSTALL" button.

## How to use

To utilize this addon you will need to have a mqtt server available on your network. You will need to specify the mqtt server hostname, port and your login credentials for the MQTT server. 

This addon has support for accepting information from multiple SWS/SCA devices, for each device you will need to ensure you add a stanza to the seneye configuration data as shown below.

```
seneye:
  - type: SWS
    serial: SERIAL_NUMBER
    secret: SECRET_KEY
  - type: SCA
    serial: SERIAL_NUMBER
    secret: SECRET_KEY
```

## Enabling the LDE and getting your SWS serial and PIN

A SWS or SCA must first be configured for LDE.

1. Navigate to the **Settings** panel of your SWS GUI or SCA.  
You will need your SWS Pin to access the SWS GUI. Click [here](http://answers.seneye.com/en/Seneye_Products/sws/instructions/TroubleShooting/How_to_find_your_SWS_ID_and_Pin) for help locating your pin.

2. Under **Developer settings** tick the box for **Enable Local Data Exchange**.

3. Make note of the **Secret Key**. You will need this later for verification of the LDE HTTP request body.

4. Enter the IP address/hostanme of your hassio instance port 8080
   Example: ```http://homeassistant.lan:8080/```

3. Click **Ok/Save**.

## Adding sensors in Home Assistant

You can confirm data is being published to the MQTT by using a tool such as MQTT explorer or simply looking at the addon logs. After you have verified data is being pushed, you can add stanzas to your configuration.yml to access the sensor data for ammonia/ph and temperature.

Assuming you were using a SWS device with serial number 12345, the below would be an example of your sensor configuration.

```
sensor:
  - platform: mqtt
    state_topic: "python/seneye/sws_12345/temperature"
    name: "aquarium temperature"
    device_class: temperature
    unit_of_measurement: "°C"
  - platform: mqtt
    state_topic: "python/seneye/sws_12345u/ph"
    name: "aquarium pH"
    unit_of_measurement: "H+"
  - platform: mqtt
    state_topic: "python/seneye/sws_12345/ammonia"
    name: "aquarium ammonia"
    unit_of_measurement: "mg/L"
```
