from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from aiogram.filters import Command

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/help"), KeyboardButton(text="/Premium")]
], 
    resize_keyboard=True,
    input_field_placeholder="Choose one option..."
)