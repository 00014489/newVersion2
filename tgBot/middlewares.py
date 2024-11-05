from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from aiogram.exceptions import TelegramAPIError
# from aiogram.dispatcher.middlewares.base import CancelHandler

class MessageHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        """
        This method is called automatically for each update.
        """
        # Check if the event is a message
        if event.message:
            message = event.message  # Extract the Message object
            
            try:
                # Log message content and user information
                user_id = message.from_user.id
                username = message.from_user.username
                
                print(f"Received message from {username} (ID: {user_id}): {message.text or 'Non-text message'}")

                if message.text:
                    await self.handle_text_message(message)
                elif message.audio:
                    await self.handle_audio_message(message)
                else:
                    print(f"Unhandled message type from {username} (ID: {user_id})")
                    await message.reply("Please send aduio of link of youtube")

                # Pass the event to the handler
                return await handler(event, data)

            except Exception as e:
                print(f"Error processing message: {e}")
        else:
            # If the event is not a message, simply pass it along
            return await handler(event, data)
        
    async def handle_text_message(self, message: Message):
        """
        Process text messages.
        """
        text = message.text
        # Perform any actions you need with the text, like command handling, etc.
        await message.reply(f"Received your text message: {text}")

    async def handle_audio_message(self, message: Message):
        """
        Process audio files sent as audio (music).
        """
        audio = message.audio
        # Download and process the audio file if needed
        print(f"Received audio file: {audio.file_id} - {audio.file_name}")
        await message.reply("Received your audio file!")
