# main.py

from agentforge.utils.guiutils.discord_client import DiscordClient
import time


def process_message(message):
    print(f"Processing message: {message}")
    # Simulate some time-consuming task
    time.sleep(5)
    return f"Processed: -{message}-"


def main():
    client = DiscordClient()
    client.run()

    while True:
        try:
            print("Getting message")
            for channel_id, messages in client.process_channel_messages():
                for message in messages:
                    print(f"Message received: {message}")
                    response = process_message(message['message'])

                    # Check if the message is a DM
                    if message['channel'].startswith('Direct Message'):
                        # If it's a DM, use the author's ID to send a DM back
                        client.send_dm(message['author_id'].id, response)
                    elif '@TrinityAF' in message['message']:
                        # If it's not a DM, send to the channel as before
                        client.send_message(channel_id, response)
                    else:
                        print('That message was not for me.')
        except KeyboardInterrupt:
            print("Stopping...")
            client.stop()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(5)


if __name__ == "__main__":
    main()
