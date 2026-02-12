import sys
import socket
import time
import argparse
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

# The "Final Boss" Wrapper - Nesting the UUID correctly
# I struggled here a bit; open to suggestions
class MemberWrapper:
    def __init__(self, id_val):
        self.id_val = id_val
    def to_payload_dict(self):
        return {
            "uuid": {
                "id": self.id_val
            }
        }

def main():
    parser = argparse.ArgumentParser(description="Device Monitor")
    parser.add_argument('action', choices=['join', 'exit'], help="Action to perform")
    parser.add_argument('--name', help="Override the default hostname")
    args = parser.parse_args()

    hostname = args.name if args.name else socket.gethostname()

    pnconfig = PNConfiguration()
    pnconfig.publish_key = 'pub-key-here'
    pnconfig.subscribe_key = 'sub-key-here'
    pnconfig.user_id = hostname
    pubnub = PubNub(pnconfig)

    channel = "availability_monitor"

    if args.action == 'join':
        print(f"--- Joining Monitor Network as: {hostname} ---")
        try:
            member_wrapper = MemberWrapper(hostname)

            # Device added as channel member
            pubnub.set_channel_members() \
                .channel(channel) \
                .uuids([member_wrapper]) \
                .sync()
            print("Successfully registered as a Channel Member.")
        except Exception as e:
            print(f"Join Error: {e}")

        try:
            while True:
                # Utilizing this way of sending the "heartbeat" to allow for feature expansion
                pubnub.publish().channel(channel).message({
                    "type": "heartbeat", "id": hostname
                }).sync()
                print(f"Heartbeat sent [{time.strftime('%H:%M:%S')}]", end="\r")
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nMonitoring paused.")

    elif args.action == 'exit':
        print(f"--- Removing {hostname} from Monitor Network ---")
        try:
            member_wrapper = MemberWrapper(hostname)
            pubnub.remove_channel_members() \
                .channel(channel) \
                .uuids([member_wrapper]) \
                .sync()
            print("Successfully removed from membership.")
        except Exception as e:
            print(f"Removal Error: {e}")

if __name__ == "__main__":
    main()
