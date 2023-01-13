
from telegram.ext import (Application,CallbackQueryHandler,CommandHandler,ContextTypes,ConversationHandler,MessageHandler,filters)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from websites_support import *
from db_controller import DB
from time import sleep
import threading
import telegram
import warnings
import asyncio
import json
import os

warnings.filterwarnings("ignore")

TOKEN = os.getenv("TELEBOT_TOKEN")

MINUTE = 60 # minute in seconds

# constants for dictionary keys
WEBSITE = "WEBSITE"; SERIAL_NUMBER="SERIAL_NUMBER"; START_OVER="START_OVER"; ACTION="ACTION"

# State definitions for top level conversation
SELECTED_MAIN_MENU = "SELECTED_MAIN_MENU"
VIEW = "VIEW"
ADD = "ADD" 
REMOVE = "REMOVE"
SELECTED_WEBSITE = "SELECTED_WEBSITE"
ASK_FOR_SERIAL = "ASK_FOR_SERIAL"
READ_SERIAL = "READ_SERIAL"
CHMOD = "MODE"
OBSESSIVE = "OBSESSIVE"
ON_DEMAND = "ON_DEMAND"
GET_UPDATE = "GET_UPDATE"
SELECTED_MODE = "SELECTED_MODE"
SELECTED_ITEM_TO_REMOVE = "SELECTED_ITEM_TO_REMOVE"
READ_PASSWORD = "READ_PASSWORD"
BACKTO_MAIN_MENU = "BACKTO_MAIN_MENU"

db = DB()




website2availability_callback = {"ksp" : check_ksp_availability,
                                 "ivory": check_ivory_availability, 
                                 "bug": check_bug_availability}

website2title_callback = {"ksp": ksp_serial_2_title, 
                                "ivory":ivory_serial_2_title, 
                                "bug":bug_serial_2_title}

async def send_message(text, chat_id, reply_markup=None):
    return await telegram.Bot(TOKEN).send_message(chat_id, text, reply_markup=reply_markup)

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    if str(user_id) in db.get_users():
        return await main_menu(update,context)
    
    await send_message(text="Enter Password:", chat_id=update.effective_user.id)
    return READ_PASSWORD

async def authenticate(update: Update, context:ContextTypes.DEFAULT_TYPE) -> str:
    password = update.message.text
    if password == os.getenv("TELEBOT_PASSWORD"):
        db.set_mode(ON_DEMAND, update.effective_user.id)
        return await main_menu(update, context)
    else:
        await send_message(text="Wrong, Enter Password:", chat_id=update.effective_user.id)
    return READ_PASSWORD
    

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data[ACTION] = None
    context.user_data[WEBSITE] = None
    
    buttons = [
            [InlineKeyboardButton(text="View watch list", callback_data=VIEW)],
            [InlineKeyboardButton(text="Add to watch list", callback_data=ADD)],
            [InlineKeyboardButton(text="Remove from watch list", callback_data=REMOVE)],
            [InlineKeyboardButton(text="Change mode", callback_data=CHMOD)],
            [InlineKeyboardButton(text="Get Update", callback_data=GET_UPDATE)],
        ]
    keyboard = InlineKeyboardMarkup(buttons)

    text = "Choose Action:"
    if context.user_data.get(START_OVER):
        try:
            #await update.callback_query.answer()
            await send_message(text=text, chat_id=update.effective_user.id ,reply_markup=keyboard)
        except Exception as e:
            context.user_data[START_OVER] = False
    elif not context.user_data.get(START_OVER):

        await update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = True
    return SELECTED_MAIN_MENU


async def backto_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data[START_OVER] = True
    await update.callback_query.answer()
    await update.callback_query.edit_message_reply_markup(None)
    await context.bot.deleteMessage(message_id = update.callback_query.message.id, chat_id = update.effective_user.id)
    return await main_menu(update, context)

################## ADD ITEM ############################

async def selected_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    action = update.callback_query.data
    context.user_data[ACTION] = action
    await update.callback_query.answer()
    # hide the inline keyboard
    await update.callback_query.edit_message_reply_markup(None)

    buttons = [ [InlineKeyboardButton(text=site_name,callback_data=f'{site_name}')]   for site_name in website2availability_callback.keys() ]
    buttons.append([InlineKeyboardButton(text="\u00ab Main menu", callback_data=BACKTO_MAIN_MENU)])
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_reply_markup(keyboard)

    return SELECTED_WEBSITE

async def ask_for_serial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    website = update.callback_query.data
    context.user_data[WEBSITE] = website
    action = context.user_data[ACTION]

    await update.callback_query.edit_message_reply_markup(None)
    await update.callback_query.answer()

    text = f"Insert serial for: {website}"
    await update.callback_query.edit_message_text(text=text)
    return READ_SERIAL

async def read_serial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data[SERIAL_NUMBER] = update.message.text
    return await add_item(update, context)

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    website = context.user_data[WEBSITE]
    serial = context.user_data[SERIAL_NUMBER]
    context.user_data[START_OVER] = False
    
    item_description = website2title_callback[website](serial)
    if (item_description != None):
        db.add_to_watchlist(website, serial, item_description, update.effective_user.id)
        await send_message(text=f'Added {item_description} to {website}', chat_id=update.effective_user.id)
    else:
        await send_message(text=f'{serial} not found in {website}', chat_id=update.effective_user.id)
    return await main_menu(update, context)



################## REMOVE ITEM ############################
async def selected_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    action = update.callback_query.data
    context.user_data[ACTION] = action
    await update.callback_query.answer()
    # hide the inline keyboard
    await update.callback_query.edit_message_reply_markup(None)

    return await select_item_to_remove(update, context)

async def select_item_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    website = update.callback_query.data

    buttons = []
    for website in website2availability_callback.keys():
        items = db.get_watchlist(website, update.effective_user.id)
        if items:
            buttons.extend([InlineKeyboardButton(text=f"{website}: {description}",callback_data=json.dumps({"serial":serial, "website":website}))] for (serial,description) in items)
    
    if buttons:
        buttons.append([InlineKeyboardButton(text="\u00ab Main menu", callback_data=BACKTO_MAIN_MENU)])
        keyboard = InlineKeyboardMarkup(buttons)
        await update.callback_query.edit_message_text( "Choose item to remove:", reply_markup=keyboard)
        return SELECTED_ITEM_TO_REMOVE
    else:
        await update.callback_query.edit_message_text(f"No items in watch list")
        return await main_menu(update, context)

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    dict = json.loads(update.callback_query.data)
    website = dict['website']
    serial = dict['serial']

    # hide the inline keyboard
    await update.callback_query.edit_message_reply_markup(None)
    
    context.user_data[START_OVER] = True

    db.remove_from_watchlist(website, serial, update.effective_user.id)
    await send_message(text=f'{serial} removed from {website} watchlist', chat_id=update.effective_user.id)
    return await main_menu(update, context)

################# VIEW WATCHLIST #############################
async def selected_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    action = update.callback_query.data
    context.user_data[ACTION] = action
    await update.callback_query.answer()
    # hide the inline keyboard
    await update.callback_query.edit_message_reply_markup(None)
    return await view_watchlist(update, context)


async def view_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    return_string = ""
    for website in website2availability_callback.keys():
        items = db.get_watchlist(website, update.effective_user.id)
        return_string += f"\nWatchlist for {website}:"
        if items:
            for (serial,description) in items:
                if description != None:
                    return_string += f"\n{serial} : {description}\n"
        else:
            return_string += " Empty\n"

    await update.callback_query.edit_message_text(text=return_string)
    context.user_data[START_OVER] = True
    return await main_menu(update, context)

################# CHMOD #############################
async def selected_chmod(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    action = update.callback_query.data
    context.user_data[ACTION] = action
    await update.callback_query.answer()
    # hide the inline keyboard
    await update.callback_query.edit_message_reply_markup(None)

    buttons = [ 
        [InlineKeyboardButton(text="Obsessive (periodic updates)",callback_data=OBSESSIVE)], 
        [InlineKeyboardButton(text="On demand",callback_data=ON_DEMAND)]
    ]
    buttons.append([InlineKeyboardButton(text="\u00ab Main menu", callback_data=BACKTO_MAIN_MENU)])
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text( "Choose Mode:", reply_markup=keyboard)
    return SELECTED_MODE


async def chmod(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.callback_query.edit_message_reply_markup(None)
    new_mode = update.callback_query.data
    await update.callback_query.edit_message_text(text=f"Changed mode to {new_mode}")
    db.set_mode(new_mode, update.effective_user.id)
    return await main_menu(update, context)


################# GET UPDATE #############################
async def selected_get_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.callback_query.edit_message_reply_markup(None)

    update_strings = get_update(update.effective_user.id)
    for i,update_string in enumerate(update_strings):
        if i==0:
            await update.callback_query.edit_message_text(text=update_string)
        else:
            await send_message(text=update_string, chat_id=update.effective_user.id)
    return await main_menu(update, context)

def get_update(user_id):
    update_strings = []
    for website in website2availability_callback.keys():
        update_string = f'\n{website}:'
        items = db.get_watchlist(website, user_id)
        if items:
            for (serial, description) in items:
                try:
                    available_branches = website2availability_callback[website](serial)
                    if available_branches != []:
                        update_string += f'\n{description} available in:\n {available_branches}\n'
                    else:
                        update_string += f'\n{description} not available\n'
                except Exception as e:
                    print("In Get update:",e)
        else:
            update_string += " No items in watchlist\n"
        update_strings.append(update_string)

    
    return update_strings

async def obsessive_updates(user_id):
    update_strings = get_update(user_id)
    for update_string in update_strings:
        await send_message(text=update_string, chat_id=user_id)

def thread_entry():
    async def thread_main():
        while True:
            obsessive_users = db.get_users_in_mode(OBSESSIVE)
            async_funcs = []
            for user_id in obsessive_users:
                f = loop.create_task(obsessive_updates(user_id))
                async_funcs.append(f)
            if async_funcs:
                await asyncio.wait(async_funcs)
            sleep(int(10 * MINUTE))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(thread_main())
    loop.close()
    


def main() -> None:
    """Run the bot."""

    # thread that updates the users in obsessive mode
    thread = threading.Thread(target=thread_entry)
    thread.start()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            READ_PASSWORD:          [   MessageHandler(filters.TEXT & ~filters.COMMAND, authenticate),
                                    ], 
            SELECTED_MAIN_MENU:     [   CallbackQueryHandler(selected_add, pattern=f'^({ADD})$'),
                                        CallbackQueryHandler(selected_remove, pattern=f'^({REMOVE})$'),
                                        CallbackQueryHandler(selected_view, pattern=f'^({VIEW})$'),
                                        CallbackQueryHandler(selected_chmod, pattern=f'{CHMOD}'),
                                        CallbackQueryHandler(selected_get_update, pattern=f'{GET_UPDATE}'),
                                    ],
            SELECTED_MODE:          [   CallbackQueryHandler(backto_main_menu, pattern=f'^({BACKTO_MAIN_MENU})$'),
                                        CallbackQueryHandler(chmod),
                                    ], 
            SELECTED_ITEM_TO_REMOVE:[  CallbackQueryHandler(backto_main_menu, pattern=f'^({BACKTO_MAIN_MENU})$'),
                                        CallbackQueryHandler(remove_item),
                                    ],
            SELECTED_WEBSITE:       [   CallbackQueryHandler(backto_main_menu, pattern=f'^({BACKTO_MAIN_MENU})$'),
                                        CallbackQueryHandler(ask_for_serial), 
                                    ],
            READ_SERIAL:            [   MessageHandler(filters.TEXT & ~filters.COMMAND, read_serial)
                                    ],
        },
        fallbacks=[CommandHandler("start", start)],

    )

    application.add_handler(conv_handler)
    
    print("Bot is online")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
