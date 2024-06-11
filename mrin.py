import telebot
import subprocess
import datetime
import os
import time
from datetime import datetime, timedelta 

# Insert your Telegram bot token here
bot = telebot.TeleBot('7072312985:AAHgR5Lc87DxZANKH2cIeXCgd1PuSInMYD0')

# Admin user IDs
admin_id = ["6768273586"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store allowed user access
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
    
    with open(LOG_FILE, "a") as file:
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
    log_entry = f"UserID: {user_id} | Time: {datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Function to check if a user has expired access
def is_access_expired(user_id):
    if user_id in user_access:
        expiry_timestamp = user_access[user_id]["expiry_time"]
        current_timestamp = datetime.utcnow().timestamp()
        return current_timestamp > expiry_timestamp
    return True

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            try:
                time_value = int(command[2])
                time_unit = command[3] if len(command) > 3 else 'days'

                if user_to_add not in allowed_user_ids:
                    allowed_user_ids.append(user_to_add)
                    with open(USER_FILE, "a") as file:
                        file.write(f"{user_to_add}\n")
                    
                    current_time = datetime.utcnow()
                    if time_unit == 'hours':
                        expiry_time = current_time + timedelta(hours=time_value)
                    elif time_unit == 'days':
                        expiry_time = current_time + timedelta(days=time_value)
                    elif time_unit == 'months':
                        expiry_time = current_time + timedelta(days=30 * time_value)
                    else:
                        response = "Invalid time unit. Please use 'hours', 'days', or 'months'."
                        bot.reply_to(message, response)
                        return

                    expiry_timestamp = expiry_time.timestamp()

                    if time_value == 1:
                        time_unit = time_unit[:-1]

                    user_access[user_to_add] = {"expiry_time": expiry_timestamp}
                    save_user_access(user_access)
                    response = f"User {user_to_add} approved for {time_value} {time_unit} by @MrinMoYxCB.\n\n\n BOT here: @ddosv1_bot"
                else:
                    response = "User already exists"
            except ValueError:
                response = "Invalid time value. Please specify a valid number."
        else:
            response = "Please specify a user ID and the time duration. Usage: /add <userid> <value> <unit>"
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

@bot.message_handler(commands=['id'])
def show_user_info(message):
    user_id = str(message.chat.id)
    username = message.from_user.username if message.from_user.username else "No username"
    role = "User"
    
    if user_id in allowed_user_ids:
        if is_access_expired(user_id):
            response = (f"👤 User Info 👤\n\n"
                        f"🔖 Role: {role}\n"
                        f"🆔 User ID: {user_id}\n"
                        f"👤 Username: @{username}\n"
                        f"⚠️ Expiry Date: Access has expired\n"
                        )
        else:
            expiry_timestamp = user_access[user_id]["expiry_time"]
            expiry_date = datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')
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

def start_attack_reply(message, target, port, duration):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"Well {username}, \n\n🚀 Attack Sent Successfully! 🚀.\n\nTarget IP: {target}\n Port: {port}\nTime: {duration} seconds"
    bot.reply_to(message, response)

attack_cooldown = {}

COOLDOWN_TIME = 20

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if is_access_expired(user_id):
            response = "Your access has expired. Please contact the admin to renew it."
            bot.reply_to(message, response)
            return
        
        if user_id not in admin_id:
            if user_id in attack_cooldown and (datetime.now() - attack_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You are on cooldown. Please wait 20 seconds before running the /attack command again."
                bot.reply_to(message, response)
                return
        
        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = command[2]
            duration = command[3]
            
            record_command_logs(user_id, "/attack", target, port, duration)
            
            start_attack_reply(message, target, port, duration)
            
            attack_cooldown[user_id] = datetime.now()
        else:
            response = "Please provide the target, port, and duration. Usage: /attack <target> <port> <duration>"
            bot.reply_to(message, response)
    else:
        response = "You are not authorized to use this command. Please contact the admin."
        bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def send_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r") as file:
                logs = file.read()
                if logs:
                    bot.reply_to(message, logs)
                else:
                    bot.reply_to(message, "No logs found.")
        except FileNotFoundError:
            bot.reply_to(message, "No logs found.")
    else:
        bot.reply_to(message, "Only admin can run this command.")

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

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = (
        f"{user_name}, Please follow these rules:\n\n"
        "1. Attack starts from commands /attack <ip> <port> <time> no need of threads.\n"
        "2. Don't run 2 attacks at the same time, as it will result in a ban from the bot.\n"
        "3. In-game freeze also supported.\n"
        "4. Click on /plan from menu to check expiry details.\n"
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_handler(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = clear_logs()
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Only admin can run this command.")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "❌❌ ATTENTION EVERYONE ❌❌\n MESSAGE FROM @MrinMoYxCB:\n\n" + command[1]
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

@bot.message_handler(func=lambda message: True)
def handle_invalid_commands(message):
    response = "Invalid command. Please use a valid command."
    bot.reply_to(message, response)

if __name__ == "__main__":
    # Load user access data on startup
    try:
        with open(USER_ACCESS_FILE, "r") as file:
            for line in file:
                user_id, expiry_time = line.strip().split(":")
                user_access[user_id] = {"expiry_time": float(expiry_time)}
    except FileNotFoundError:
        pass

    bot.polling()
