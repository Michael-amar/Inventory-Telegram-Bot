# Inventory Bot

## About
A telegram bot that checks if products in its watch list are available in store.

Supported website are: ksp.co.il, ivory.co.il, bug.co.il

## Running the bot
1) Create a telegram bot [(tutorial)](https://sendpulse.com/knowledge-base/chatbot/telegram/create-telegram-chatbot), and write down the bot TOKEN
2) clone this repository
    ```console
    git clone https://github.com/Michael-amar/Inventory-Telegram-Bot.git
    ```
3) Insert your token
   #### **`run.sh`**
   ```console
    export TELEBOT_TOKEN="TOKEN"
   ```

4) Set your bot password
   #### **`run.sh`**
   ```console
   export TELEBOT_PASSWORD="YourPassword"
   ``` 

5) install required library
   ```console
   pip install python-telegram-bot --upgrade
   ```

6) Run the Bot
   ```console
   sh run.sh
   ```



## Adding support for new Website
To add support for new website you need to:

1) Create a function that receives a serial number as input and returns a list of available branches 
   #### **`websites_support.py`**
   ```python
   def check_NEWSITE_availability(serial_number: str) -> list[str]
   ```

2) Create a function that receives a serial number as input and returns the title of the product
   #### **`websites_support.py`**
   ```python
    def NEWSITE_serial_2_title(serial_number : str) -> str
   ```

3) Add the callbacks to the relevant dictionaries
   #### **`telebot.py`**
   ```python
    website2availability_callback = { ...
                                      ...
                                      "NEWSITE": check_NEWSITE_availability
                                    }

    website2title_callback = {  ...
                                ...
                                "NEWSITE": NEWSITE_serial_2_title
                             }
   ```








