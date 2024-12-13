# UI.py

from agentforge.utils.Logger import Logger


class UI:
    def __init__(self, client):
        self.client = client
        self.channel_id_layer_0 = None
        self.current_thread_id = None
        self.logger = Logger('DiscordClient')

    def send_message(self, layer, message, response):
        self.logger.log(f"send_message called with layer: {layer}", 'debug', 'DiscordClient')
        self.logger.log(f"Message: {message}", 'debug', 'DiscordClient')
        self.logger.log(f"Response: {response[:100]}...", 'debug', 'DiscordClient')

        if layer == 0:
            self._send_layer_0_message(message, response)
        elif layer == 1:
            self._send_layer_1_message(message, response)
        else:
            self.logger.log(f"Invalid layer: {layer}", 'error', 'DiscordClient')

    def _send_layer_0_message(self, message, response):
        try:
            if message['channel'].startswith('Direct Message'):
                self.client.send_dm(message['author_id'], response)
            else:
                channel_id = self.channel_id_layer_0
                self.logger.log(f"Sending message to channel: {channel_id}", 'debug', 'DiscordClient')
                sent_message = self.client.send_message(channel_id, response)
                if sent_message:
                    self.logger.log(f"Message sent successfully. ID: {sent_message.id}", 'info', 'DiscordClient')
                    return sent_message.id
                else:
                    self.logger.log("Failed to send message", 'error', 'DiscordClient')
                    return None
        except Exception as e:
            self.logger.log(f"Error in send_message (layer 0): {str(e)}", 'error', 'DiscordClient')
            return None

    def _send_layer_1_message(self, message, response):
        try:
            self.logger.log(f"Layer 1: Current thread ID: {self.current_thread_id}", 'debug', 'DiscordClient')
            if not self.current_thread_id:
                thread_name = f"Brain - {message['author'][:20]}"
                self.logger.log(f"Attempting to create new thread: {thread_name}", 'info', 'DiscordClient')
                self.logger.log(
                    f"Using channel_id: {self.channel_id_layer_0}, message_id: {message['message_id']}",
                    'debug',
                    'DiscordClient'
                )

                self.current_thread_id = self.client.create_thread(
                    channel_id=int(self.channel_id_layer_0),
                    message_id=int(message['message_id']),
                    name=thread_name
                )

                if self.current_thread_id is None:
                    self.logger.log("Failed to create thread: current_thread_id is None", 'error', 'DiscordClient')
                    return
                self.logger.log(f"Thread created with ID: {self.current_thread_id}", 'info', 'DiscordClient')

            if self.current_thread_id:
                self.logger.log(f"Replying to thread: {self.current_thread_id}", 'info', 'DiscordClient')
                success = self.client.reply_to_thread(int(self.current_thread_id), response)
                if success:
                    self.logger.log("Reply sent successfully", 'info', 'DiscordClient')
                else:
                    self.logger.log("Failed to send reply to thread", 'error', 'DiscordClient')
            else:
                self.logger.log("Failed to create or find thread for layer 1 message", 'error', 'DiscordClient')
        except Exception as e:
            self.client.send_message(self.channel_id_layer_0, response)
            self.logger.log(f"Error in send_message for layer 1: {str(e)}", 'error', 'DiscordClient')
