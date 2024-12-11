import os
import time
import pyautogui
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from threading import Thread

# Global variables
screenshot_frequency = 5  # default frequency (seconds)
screenshot_thread = None
is_screenshotting = False

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the remote screenshot tool!\n"
                              "/start - Introduction\n"
                              "/screenshot - Take a screenshot\n"
                              "/setfrequency {value in seconds} - Set screenshot frequency\n"
                              "/autoscreenshot {duration in minutes} - Take screenshots at regular intervals\n"
                              "/stop - Stop taking screenshots")

def screenshot(update: Update, context: CallbackContext):
    screenshot = pyautogui.screenshot()
    screenshot_path = "screenshot.png"
    screenshot.save(screenshot_path)
    update.message.reply_photo(photo=open(screenshot_path, 'rb'))
    os.remove(screenshot_path)

def set_frequency(update: Update, context: CallbackContext):
    global screenshot_frequency
    try:
        new_frequency = int(context.args[0])
        screenshot_frequency = new_frequency
        update.message.reply_text(f"Screenshot frequency set to {new_frequency} seconds.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /setfrequency {value in seconds}")

def autoscreenshot(update: Update, context: CallbackContext):
    global is_screenshotting, screenshot_thread
    if is_screenshotting:
        update.message.reply_text("Autoscreenshot is already running.")
        return

    try:
        duration = int(context.args[0]) * 60  # convert minutes to seconds
        is_screenshotting = True

        def take_screenshots():
            start_time = time.time()
            while is_screenshotting and time.time() - start_time < duration:
                screenshot(update, context)
                time.sleep(screenshot_frequency)

        screenshot_thread = Thread(target=take_screenshots)
        screenshot_thread.start()

        update.message.reply_text(f"Autoscreenshot started. Screenshots will be taken every {screenshot_frequency} seconds for {context.args[0]} minutes.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /autoscreenshot {duration in minutes}")

def stop(update: Update, context: CallbackContext):
    global is_screenshotting
    is_screenshotting = False
    if screenshot_thread:
        screenshot_thread.join()
    update.message.reply_text("Stopped taking screenshots.")

def main():
    # Replace with your bot's API token
    TOKEN = "7576774302:AAFtHrzsAOmI58FM9kMgravElfXbOznwYzA"
    
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("screenshot", screenshot))
    dispatcher.add_handler(CommandHandler("setfrequency", set_frequency))
    dispatcher.add_handler(CommandHandler("autoscreenshot", autoscreenshot))
    dispatcher.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
