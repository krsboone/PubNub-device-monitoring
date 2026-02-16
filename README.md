# PubNub-device-monitoring


## Details

Set of tools that are used to monitor the availability of a device. This is the initial draft for what I hope will be toolset capable of providing more robust device monitoring.

`heartbeat.py` 
* Runs on the device to be monitored
* When started, must specify `join` (creates channel membership) or `exit` (removes channel membership) to begin or end monitoring of the device
* Optional arguement `--name` to override the hostname
* Example: `python3 heartbeat.py --name runtime101-us-east-1 join`

`log_cap.py`
* Optional
* A simple logging wrapper used by the monitoring agent
* Writes logs to `log/`
* If not needed, then remove `from log_cap import start_logging` and the `start_logging` function from `monitor.py`

`monitor.py`
* Subscribes to PubNub channel that devices send the hearbeat messages to
* Builds a dict of the hostname from each device sending the hearbeat message, and the heartbeat time
* If time threshold is exceeded, device is deemed offline
* When device is offline a message is sent to the channel including the hostname and time, and that same information is logged

`dasbboard.html`
* Visual display of devices being monitored and current status
* Channel memberships are used to determine details of the devices being monitored; quantity & hostname
* Listens for hearbeat messages
* Will also send a message when a device is determined to be offline. If both `dashboard.html` and `monitor.py` are running, each will send this message resulting in two offline messages for the single event. This is noted for future improvement.
* The card for each device can be expanded to show a history of offline events


## Config

Replace
```
publishKey: "pub-key-here"
subscribeKey: "sub-key-here"
```

with your pub/sub keys

Install PubNub Python SDK
`pip install 'pubnub>=10.6.1'`
https://www.pubnub.com/docs/sdks/python


## Recording

https://youtu.be/TOBEw8KR8wY


## Todo

1. Add ability to turn the monitoring functionality on/off on the dashboard (default should be off). Currently, if both the dashboard and monitor.py are running, there will be 2 offline events create for a single occurrence of a device going offline.
2. Add functionality to track additional device status metrics.
3. Add ability to purge outage history data from dashboard.
4. ~~Strict userIDs vs randomly generated~~
