import time
import datetime
import json
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from log_cap import start_logging

start_logging(os.path.basename(__file__))

# Configuration
pnconfig = PNConfiguration()
pnconfig.publish_key = 'pub-key-here'
pnconfig.subscribe_key = 'sub-key-here'
pnconfig.user_id = "fleet_master_node"
pubnub = PubNub(pnconfig)

MAIN_CHANNEL = "availability_monitor"
LOG_PREFIX = "incident_logs."
THRESHOLD = 10  # Seconds before considering a node "Dead"

# State Tracking
registry = {} # { "hostname": {"last_seen": timestamp, "is_offline": False} }

class MonitorCallback(SubscribeCallback):
    def message(self, pubnub, event):
        if event.channel == MAIN_CHANNEL:
            msg = event.message
            node_id = msg.get("id")
            if node_id:
                # If node was previously offline, it's back!
                # Give thought to noting when a device returns from offline. Observed race conditions when multiple devices are being monitored.
                registry[node_id] = {
                    "last_seen": time.time(),
                    "is_offline": False
                }

def report_incident(node_id):
    # Using datetime for more flexible 12-hour clock formatting
    now = datetime.datetime.now()
    # Format: 2/10/2026, 4:56:10 PM
    timestamp = now.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
    # For now removing conditional check due to race conditions when multiple devices are running
    print(f"🚨 ALERT: {node_id} is DOWN! Logging: {timestamp}")
    # Currently only want to send events when the device is down
    pubnub.publish().channel(LOG_PREFIX + node_id).message({
        "event": "DISCONNECT",
        "timestamp": timestamp,
        "id": node_id
    }).sync()

# Start Listening
pubnub.add_listener(MonitorCallback())
pubnub.subscribe().channels([MAIN_CHANNEL]).execute()

print("--- PubNub | Availability Monitoring  ---")

try:
    while True:
        now = time.time()
        for node_id, data in registry.items():
            # Check for timeout
            #print(data)
            if not data["is_offline"] and (now - data["last_seen"] > THRESHOLD):
                data["is_offline"] = True
                report_incident(node_id)

        time.sleep(2) # Efficiency sleep
except KeyboardInterrupt:
    print("Monitor shutting down.")
