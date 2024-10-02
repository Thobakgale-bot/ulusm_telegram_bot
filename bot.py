import telegram.ext
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
GROUP_ID = os.getenv("GROUP_ID")  
GROUP_NAME = os.getenv("GROUP_NAME")  

# A list of South American countries (not eligible)
SOUTH_AMERICAN_COUNTRIES = [
    'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia',
    'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname',
    'Uruguay', 'Venezuela'
]

# To store the user's state (waiting for country input)
user_states = {}

# To track which users have already been given an invite link
user_invite_status = {}

# To track if the user has clicked /start
user_started = {}

# Load valid countries from JSON file (JSON contains dictionaries with "name" key)
def load_valid_countries():
    with open('countries.json', 'r') as f:
        data = json.load(f)
    # Extract the "name" field from each country
    return [country['name'] for country in data]

# Function to get the user's name (either username or first name)
def get_user_name(user):
    return user.username if user.username else user.first_name

# Middleware to check if user has clicked /start before allowing other commands
async def ensure_started(update: telegram.Update, context: telegram.ext.CallbackContext, next_handler):
    user = update.message.from_user
    if user.id not in user_started or not user_started[user.id]:
        await update.message.reply_text("Please use the /start command to initiate the conversation first.")
    else:
        await next_handler(update, context)

# Function to check if the input is a valid country
def is_valid_country(input_country, valid_countries):
    return input_country.title() in valid_countries

# Function to check eligibility based on country
async def check_country_and_continue(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    country = update.message.text  # User's country input

    # Load the list of valid countries
    valid_countries = load_valid_countries()

    # Check if the input is a valid country
    if not is_valid_country(country, valid_countries):
        await update.message.reply_text(f"'{country}' is not a valid country, {user_name}. Please enter a valid country.")
        return

    # Check if the user is from a South American country
    if country.title() in SOUTH_AMERICAN_COUNTRIES:
        sorry_message = f"We are sorry, {user_name}, You are not eligible."
        await update.message.reply_text(sorry_message)
    else:
        # Eligible user, show the poll
        await poll_to_check_interest(update, context, user_name)

    # Clear the user state after processing the country
    user_states.pop(user.id, None)

# Command to initiate the process of joining the group
async def join_group(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    user_states[user.id] = "awaiting_country"  # Set the user state to wait for country input
    await update.message.reply_text(f"Hello {user_name}, please enter your country:")

# Function to show a poll asking if the user is interested in joining the group
async def poll_to_check_interest(update: telegram.Update, context: telegram.ext.CallbackContext, user_name):
    # Simple question and options in English
    question = f"{user_name}, are you interested in joining the private group?"
    options = ["Yes", "No"]

    # Send a poll to the user
    await context.bot.send_poll(
        chat_id=update.message.chat_id,
        question=question,
        options=options,
        is_anonymous=False
    )

# Callback for when a user answers the poll
async def handle_poll_answer(update: telegram.Update, context: telegram.ext.CallbackContext):
    poll_answer = update.poll_answer
    user_id = poll_answer.user.id
    user = await context.bot.get_chat(user_id)
    user_name = get_user_name(user)
    selected_option = poll_answer.option_ids[0]

    # Check if the user has already received an invite link
    if user_id in user_invite_status and user_invite_status[user_id]:
        # If the user has already been given an invite link, send a message
        await context.bot.send_message(
            chat_id=user_id,
            text=f"{user_name}, you were already given a one-time invite link. You cannot receive another invite."
        )
        return  # Exit early

    # If the user selected "Yes", process the addition to the group using a single-use invite link
    if selected_option == 0:  # "Yes" option
        try:
            # Show "Processing" message
            processing_message = f"Processing for {user_name}..."
            await context.bot.send_message(chat_id=user_id, text=f"{processing_message}...")

            # Create a single-use invite link to the group
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                member_limit=1,  # Single-use link
                expire_date=None  # You can set expiration if needed
            )

            # Track that the user has been given an invite link
            user_invite_status[user_id] = True

            # Display only the last 4 letters of the group name
            last_4_letters = GROUP_NAME[-4:]
            await context.bot.send_message(
                chat_id=user_id,
                text=f"{user_name}, you are invited to {last_4_letters}. Here is your invite link: {invite_link.invite_link}"
            )
        except telegram.error.TelegramError as e:
            # Handle invite link creation error
            await context.bot.send_message(
                chat_id=user_id,
                text=f"There was an issue creating an invite link for you, {user_name}. Please try again later."
            )
            print(f"Error creating invite link: {e}")
    else:
        # If the user selected "No", just acknowledge their response
        no_message = f"Sad to see you declining, {user_name}..."
        await context.bot.send_message(chat_id=user_id, text=no_message)

# Define the command handlers
async def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    await update.message.reply_text(f"Hello {user_name}, welcome to Ulusm Bot!")

async def help_command(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    await update.message.reply_text(
        f"""
        Hi {user_name}! I'm a Telegram Bot created by Thobakgale. Follow these commands:

        /start - to start the conversation
        /content - Info about Ulsm Skills
        /contact - Info about how to contact Thobakgale
        /gateways - List of supported payment gateways
        /rules - Our rules and policies
        /help - to get this help menu
        /join_group - To request joining the private group by providing your country
        """
    )

async def contact_command(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    await update.message.reply_text(
        f"""
        You can contact Thobakgale (Payment Processing Agent) via the following:

        📧 Email: thobakgale@example.com
        📞 Phone: +1234567890
        🌍 Website: www.thobakgale-payments.com

        Feel free to reach out for any inquiries or services, {user_name}!
        """
    )

async def content_command(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    await update.message.reply_text(
        f"""
        Ulusm Bot offers the following services as a payment processing agent:

        💳 Payment Gateway Setup
        🔐 Secure Transaction Management
        💼 Business Payment Consulting
        📊 Transaction Analytics and Reporting
        🏦 Bank Integration for Automated Payments
        🤝 Customer Support and Payment Issue Resolution

        Let me know if you need more details about any of these services, {user_name}!
        """
    )

async def gateways_command(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    await update.message.reply_text(
        f"""
        Ulusm Bot supports the following payment gateways, {user_name}:

        🏦 Venmo
        💵 CashApp
        💳 Stripe
        🍏 ApplePay
        🛒 Alipay
        💰 PayPal
        ₿ Bitcoin
        🔒 Monero

        Feel free to ask for more details on how to use any of these payment methods!
        """
    )

async def rules_command(update: telegram.Update, context: telegram.ext.CallbackContext):
    user = update.message.from_user
    user_name = get_user_name(user)
    await update.message.reply_text(
        f"""
        Ulusm Bot Rules, {user_name}:

        🚫 We do not condone carding, fraud, or any illegal activities.
        🛡️ Integrity is highly appreciated in all transactions.
        ✅ We value honest business and secure payments.

        Please adhere to these rules for a smooth and professional experience.
        """
    )

# Handle any other text messages
async def handle_message(update: telegram.Update, context: telegram.ext.CallbackContext):
    user_id = update.message.from_user.id
    user = update.message.from_user
    user_name = get_user_name(user)

    if user_id in user_states and user_states[user_id] == "awaiting_country":
        # If the bot is expecting a country input, process it
        await check_country_and_continue(update, context)
    else:
        await update.message.reply_text(f"Please use one of the commands to interact with the bot, {user_name}. Use /help to see available commands.")

# Main function to start the bot
def main():
    # Create an Application object
    application = telegram.ext.Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(telegram.ext.CommandHandler('start', start))
    application.add_handler(telegram.ext.CommandHandler('help', help_command))
    application.add_handler(telegram.ext.CommandHandler('contact', contact_command))
    application.add_handler(telegram.ext.CommandHandler('content', content_command))
    application.add_handler(telegram.ext.CommandHandler('gateways', gateways_command))
    application.add_handler(telegram.ext.CommandHandler('rules', rules_command))
    application.add_handler(telegram.ext.CommandHandler('join_group', join_group))

    # Add a handler for the poll answer
    application.add_handler(telegram.ext.PollAnswerHandler(handle_poll_answer))

    # Add handler for other text messages
    application.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.TEXT, handle_message))

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    main()
