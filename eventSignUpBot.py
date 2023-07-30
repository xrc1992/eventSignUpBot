from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
event_name = ""  # To store the event name
participants = set()

# Command handler for /start command
def start(update: Update, context: CallbackContext):
    # Create an inline keyboard with the sign-up and leave buttons
    keyboard = [
        [InlineKeyboardButton("Sign Up", callback_data='signup')],
        [InlineKeyboardButton("Leave", callback_data='leave')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Quick help text
    help_text = (
        "Hello! I am your Event Signup Bot. The current event is: {event_name}.\n\n"
        "Here are the available commands:\n\n"
        "/start - Start the bot and view the current event.\n"
        "/setevent - Set the event name.\n"
        "/signup - Sign up for the event.\n"
        "/leave - Leave the event.\n"
        "/participants - View the list of participants.\n"
        "/help - Display this help message.\n"
    )

    update.message.reply_text(help_text.format(event_name=event_name), reply_markup=reply_markup)

# Callback function for the sign-up button
def signup_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in participants:
        participants.add(user_id)
        query.answer("You have successfully signed up for the event!")
    else:
        query.answer("You are already signed up for the event.")
    send_participant_count(update.effective_chat.id)

# Callback function for the leave button
def leave_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in participants:
        participants.remove(user_id)
        query.answer("You have left the event.")
    else:
        query.answer("You are not signed up for the event.")
    send_participant_count(query.effective_chat.id)

# Send the participant count to the group chat
def send_participant_count(chat_id):
    num_participants = len(participants)
    if num_participants > 0:
        message = f"Number of participants for {event_name}: {num_participants}"
        # Get participant names
        participant_names = [updater.bot.get_chat_member(chat_id, user_id).user.first_name for user_id in participants]
        participants_list = "\n".join(participant_names)
        message += f"\n\nParticipant Names:\n{participants_list}"
    else:
        message = f"No participants signed up for {event_name} yet."
    
    updater.bot.send_message(chat_id=chat_id, text=message)

# Command handler for /participants command
def view_participants(update: Update, context: CallbackContext):
    send_participant_count(update.message.chat_id)

# Command handler for /signup command
def signup(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in participants:
        participants.add(user_id)
        update.message.reply_text(f"You have successfully signed up for {event_name}!")
    else:
        update.message.reply_text("You are already signed up for the event.")
    send_participant_count(update.message.chat_id)

# Command handler for /leave command
def leave(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in participants:
        participants.remove(user_id)
        update.message.reply_text("You have left the event.")
    else:
        update.message.reply_text("You are not signed up for the event.")
    send_participant_count(update.message.chat_id)

# Command handler for /setevent command
def set_event(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter the event name:")
    return "GET_EVENT_NAME"

# Callback function to handle the entered event name
def get_event_name(update: Update, context: CallbackContext):
    global event_name
    event_name = update.message.text
    update.message.reply_text(f"Event name set to: {event_name}")
    return ConversationHandler.END

# Message handler for non-command messages
def echo(update: Update, context: CallbackContext):
    update.message.reply_text("I'm sorry, I don't understand that command. Use /signup to join the event.")

# Error handler to display error message for invalid commands
def error(update: Update, context: CallbackContext):
    update.message.reply_text("Invalid command. Please use the correct command or format.")

# Command handler for /help command
def help(update: Update, context: CallbackContext):
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Start the bot and view the current event.\n"
        "/setevent - Set the event name.\n"
        "/signup - Sign up for the event.\n"
        "/leave - Leave the event.\n"
        "/participants - View the list of participants.\n"
        "/help - Display this help message.\n"
    )
    update.message.reply_text(help_text)

def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram Bot token
    global updater
    updater = Updater("6590716273:AAHqmnMPP6jUIAU57pbml2ODr_2B1NyQvcs", use_context=True)
    dp = updater.dispatcher

    # Add handlers for commands and messages
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("participants", view_participants))
    dp.add_handler(CommandHandler("signup", signup))
    dp.add_handler(CommandHandler("leave", leave))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler("setevent", set_event))
    dp.add_handler(CommandHandler("help", help))

# Add conversation handler for setting the event name

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('setevent', set_event)],
        states={
            "GET_EVENT_NAME": [MessageHandler(Filters.text & ~Filters.command, get_event_name)]
        },
        fallbacks=[],
    )
    dp.add_handler(conv_handler)

    dp.add_handler(CallbackQueryHandler(signup_button))  # Register the callback function for the sign-up button
    dp.add_handler(CallbackQueryHandler(leave_button))  # Register the callback function for the leave button

    # Add the error handler
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()