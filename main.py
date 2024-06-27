from customtkinter import *  # pip install customtkinter
# from CTkMessagebox import CTkMessagebox
from PIL import ImageTk, Image, ImageEnhance  # pip install pillow
import requests
from currency_converter import CurrencyConverter
from dotenv import load_dotenv

from tkinter import messagebox
import json
import time
import os



# API 
opensea_api = "" # enter your opensea API key here

# Load environment variables from .env file (APIs in this case)
load_dotenv()
opensea_api = os.getenv('API_OPENSEA') # uncomment if api added manually 3 lines above
magiceden_bearer = os.getenv('MAGICEDEN_BEARER') # uncomment if api added manually 2 lines above

# global vars
data = 'data.json'
app_data = 'app_data.json'

crypto_prices = {
            'SOL': 0,
            'ETH': 0,
            'MATIC': 0
        }
dollar_huf = 0

# create window
window = CTk()
window.title('NFT Portfolio')
# window.geometry('1920x1080')
window.geometry('1440x900')
#TODO fix screen geometry to start in full screen on every computer
window.minsize(width=300, height=690)
window.grid_columnconfigure(2, weight=1)
window.grid_rowconfigure((1,3,5), weight=1)
window.grid_rowconfigure((2), weight=10)

# create styling
set_appearance_mode('dark')
set_default_color_theme('dark-blue')
title_font = ('Helvetica', 24, 'bold')
title_font2 = ('Helvetica', 18, 'bold')
menu_row_font = ('Helvetica', 20, 'bold')
vol24_font = ('Helvetica', 34, 'bold')

bright_green_color = '#39e75f'
green_color = '#08a045'
red_color = '#ff2c2c'
dark_red_color = '#d1001f'
orange_color = 'orange'
darkblue_color = '#02367b'
lightblue_color = '#5ac4f6'








#|||||||||||||||||||||||||||||||||||||    FRONTEND FUNCTIONS    ||||||||||||||||||||||||||||||||||||||||||||||||||
# open image as CTk object
def ctk_image_open(filename):
    image_path = f'images/{filename}.png'
    pil = Image.open(image_path)
    return CTkImage(light_image=pil, dark_image=pil, size=(80, 80))


# set options menu text color when changes value
def opmenu_text(selected_value): # important to add a kwarg, to enable def to accept arguments
    collection_optionsmenu.configure(variable=my_var1, text_color='black')


# dark image enchancer
def dark(image):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(0.9)

# image process
def compress_image(image_filename):
    '''inputs an image, returns the image as ImageTk PhotoImage'''
    image_pil = Image.open(f'images/{image_filename}.png')
    resized = image_pil.resize((nft_widget_width, nft_widget_height), Image.Resampling.LANCZOS)
    darkened = dark(resized)
    return darkened


def options():
    '''returns a list with the nft names from the json file'''
    opened_data = readjson()
    
    my_list = []
    for item in opened_data:
        my_list.append(item['name'])

    return my_list


def button_pressed(id):
    choosen_set = my_var1.get()
    choosen_quantity = quantity_entry.get()

    if choosen_quantity.isdigit() or is_float(choosen_quantity):
        if choosen_set != 'Choose a set':
            opened_data = readjson()
            for item in opened_data:
                if item['name'] == choosen_set:
                    if id == 'add':
                        item['quantity'] += float(choosen_quantity)
                        messagebox.showinfo("Information", "Item(s) Added!")

                    elif id == 'remove':
                        if float(choosen_quantity) <= item['quantity']:
                            item['quantity'] -= float(choosen_quantity)
                            messagebox.showinfo("Information", "Item(s) Removed!")

                        else:
                            # CTkMessagebox(title="Error", message="NFT quantity can't be minus", icon="cancel")
                            messagebox.showwarning('error', f"You only have {int(item['quantity'])} {item['name']}(s)")

            writejson(opened_data)
            
            when_price_change() # for refreshing the gui and the json file
        else:
            quantity_entry.delete(0, END) # empty the entry box
            # reset options menu
            my_var1.set('Choose a set')
            collection_optionsmenu.configure(text_color='#565b5d')
            print('input error')
            # CTkMessagebox(title="Error", message=f'{choosen_set}!', icon="cancel")
            messagebox.showwarning('error', "Choose a Set!")
    else:
        quantity_entry.delete(0, END) # empty the entry box
        # reset options menu
        my_var1.set('Choose a set')
        collection_optionsmenu.configure(text_color='#565b5d')
        print('input error')
        # CTkMessagebox(title="Error", message=f'{choosen_quantity} is not a number!', icon="cancel")
        messagebox.showwarning('error', f'{choosen_quantity} is not a number!')

def when_price_change():
    '''write json file total$, changes portfolio labels'''
    calculate_dolla()  # re calculate the $, for the total portfolio worth
    portfolio_value_title2.configure(text=calc_portfolio_worth_usd())
    portfolio_value_title3.configure(text=calc_portfolio_worth_huf())

    quantity_entry.delete(0, END) # empty the entry box after pressing a button
    # reset options menu
    my_var1.set('Choose a set')
    collection_optionsmenu.configure(text_color='#565b5d')

    # FUTURE ToDo: refresh all nft cards value too

#|||||||||||||||||||||||||||||||||||||    BACKEND FUNCTIONS    ||||||||||||||||||||||||||||||||||||||||||||||||||
def readjson():
    '''read the fresh data from data json file'''
    with open(data, 'r') as datajson:
        opened_data = json.load(datajson)
    return opened_data

def writejson(json_list):
    '''include the modified list of the json file'''
    with open(data, 'w') as datajson:
        json.dump(json_list, datajson, indent=4)

def dollar_to_huf():
    '''refresh global INT variable (dollar_huf) to 1$ worth of huf'''
    global dollar_huf
    c = CurrencyConverter()
    dollar_huf_object = c.convert(1, "USD", "HUF")
    dollar_huf_converted = "{:,.0f}".format(dollar_huf_object)
    dollar_huf = int(dollar_huf_converted)


def calc_portfolio_worth_usd():
    '''returns the sum of $ the NFT-s worth in str format'''
    total_usd = 0
    opened_data = readjson()

    for item in opened_data:
        total_usd += item["total$"]

    usd_message = f'{str(total_usd)}$'
    return usd_message


def calc_portfolio_worth_huf():
    '''returns the sum of HUF the NFT-s worth in str format'''
    total_usd = 0
    opened_data = readjson()

    for item in opened_data:
        total_usd += item["total$"]

    total_huf_str = str(total_usd * dollar_huf)
    length = len(total_huf_str)
    if length == 5:
        formatted_total_huf = total_huf_str[:2] + ',' + total_huf_str[2:]

    elif length == 6:
        formatted_total_huf = total_huf_str[:3] + ',' + total_huf_str[3:]

    elif length == 7:
        formatted_total_huf = total_huf_str[:1] + ',' + total_huf_str[1:4] + ',' + total_huf_str[4:]
    else:
        return f'{total_huf_str} Ft.'
    return f'{formatted_total_huf} Ft.'

def fetch_crypto_prices():
    '''refreshes the global dictionary of crypto live prices'''
    # GPT
    global crypto_prices
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'solana,ethereum,matic-network',  # Coin IDs for SOL, ETH, and MATIC
        'vs_currencies': 'usd'             # Currency to fetch prices in
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        prices = response.json()
        sol_price = prices['solana']['usd']
        eth_price = prices['ethereum']['usd']
        matic_price = prices['matic-network']['usd']
        
        crypto_prices = {
            'SOL': sol_price,
            'ETH': eth_price,
            'MATIC': matic_price
        }
        return
    
    else:
        return {
            'error': 'Failed to fetch prices',
            'status_code': response.status_code
        }

def calculate_dolla():
    '''read floor price from json file, than convert it to $ + sums it to a total$ key value pair, writes the json file'''
    opened_data = readjson()

    for item in opened_data:
        quantity = item["quantity"] # this is a float already
        floor_token = float(item["token_floor_price"])
        total_worth_token = quantity*floor_token

        if item["token"] == 'ETH':
            item["total$"] = int(total_worth_token * crypto_prices["ETH"]) # i change to INT here, to leave decimals out later

        elif item["token"] == 'SOL':
            item["total$"] = int(total_worth_token * crypto_prices["SOL"])

        elif item["token"] == 'MATIC':
            item["total$"] = int(total_worth_token * crypto_prices["MATIC"])
        
        else:
            item["total$"] = 0

    writejson(opened_data)


def refresh_price():
    '''refreshes floor prices in the json file'''
    opened_data = readjson()

    for item in opened_data:
        time.sleep(1)
        if item["platform"] == "opensea":
            opensea_dict = get_opensea_price(item["api_name_format"])
            item["token_floor_price"] = opensea_dict['floor']
            item["vol_24"] = opensea_dict['vol24']

        if item["platform"] == "coingecko":
            # item["token_floor_price"] = get_coingecko_price(item["api_name_format"])
            pass

        if item["platform"] == "magiceden":
            item["token_floor_price"] = get_magiceden_price(item["api_name_format"])
            #
            # time.sleep(1)
            item["vol_24"] = "0.00"
            
    writejson(opened_data)
    
    dollar_to_huf() # refresh HUF-USD price too
    fetch_crypto_prices() # refresh ETH, SOL, etc.....
    when_price_change() # for refreshing the gui and the json file
    vol_24h_percent.configure(text=f'{find_mvp()['vol_change']}%') # refresh MVP
    mvp_title.configure(text=f'MVP set: {find_mvp()['name']}') # refresh MVP
    messagebox.showinfo("Information", "Prices Refreshed!")


def export_csv():
    messagebox.showinfo("Information", "CSV Exported!")


def get_opensea_price(required_format_name):
    """enter nft collection name, returns dictionary floor price formatted to str, vol24 str"""
    opensea_url = f"https://api.opensea.io/api/v2/collections/{required_format_name}/stats"
    opensea_headers = {
        "accept": "application/json",
        "x-api-key": opensea_api
    }

    response = requests.get(opensea_url, headers=opensea_headers)
    data = response.json()

    floor_price = data["total"]["floor_price"]
    volume_change = data['intervals'][0]['volume_change']

    formatted_volume_change = format(volume_change, ".2f")
    formatted_floor = format(floor_price, ".2f")

    my_dict = {
        'floor': formatted_floor,
        'vol24': formatted_volume_change
    }

    return my_dict


def get_magiceden_price(required_format_name):
    """enter nft collection name, returns floor price formatted to comma"""
    magiceden_url = f"https://api-mainnet.magiceden.dev/v2/collections/{required_format_name}/stats"
    magiceden_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {magiceden_bearer}"
    }
    response = requests.get(magiceden_url, headers=magiceden_headers)
    data = json.loads(response.text)
    floor_price = data["floorPrice"]
    formatted_number = "{:,.2f}".format(floor_price / 1000000000)
    return formatted_number


def find_mvp():
    '''only opensea nft play, check json file for the MVP set name and volume%, returns them in a dictionary'''
    current_biggest = 0.00
    mvp = ''
    opened_data = readjson()

    for item in opened_data:
        set_vol = float(item["vol_24"]) 
        if set_vol > current_biggest:
            current_biggest = set_vol
            mvp = item["name"]

    mvp = {
        'name': mvp,
        'vol_change': current_biggest
    }

    return mvp


def is_float(str):
    '''check if str is a float or no, return True or False'''
    if str.isdigit() == False:
        try:
            float(str)
            return True
        except ValueError:
            return False


# program start
dollar_to_huf()
fetch_crypto_prices()
# refresh_price() dont do it in the start, app opens only after prices fetched
calculate_dolla()

#|||||||||||||||||||||||||||||||||||||    FRONTEND    ||||||||||||||||||||||||||||||||||||||||||||||||||

# create mvp frame and contents
mvp = CTkFrame(window, fg_color=orange_color, corner_radius=20)
mvp.grid(row=0, column=0, pady=20, sticky='nsew', padx=20, ipady=8)

mvp_title = CTkLabel(mvp, text=f'MVP set: {find_mvp()['name']}', font=title_font, width=350, anchor='w', padx=20)
mvp_title.pack(pady=20)

tropy_icon = ctk_image_open('trophy')
tropy_icon_label = CTkLabel(mvp, text='', image=tropy_icon)
tropy_icon_label.pack()

vol_24h_percent = CTkLabel(mvp, text=f'{find_mvp()['vol_change']}%', text_color=bright_green_color, font=vol24_font, width=350, anchor='e', padx=10)
vol_24h_percent.pack()

mvp_help_info = CTkLabel(mvp, text='(volume in last 24h)', text_color='black', width=350, anchor='e', padx=10)
mvp_help_info.pack()

# create sidebar frame and contents
sidebar = CTkFrame(window, fg_color=darkblue_color, corner_radius=20)
sidebar.grid(row=2, column=0, padx=20, sticky='nsew', ipady=15)
sidebar.grid_columnconfigure((0,1), uniform='a')

sidebar_title = CTkLabel(sidebar, text='Edit Wallet', font=title_font, anchor='w', padx=20)
sidebar_title.grid(row=0, column=0, columnspan=2, pady=20, sticky='wens')
    # create the options menu
options_list = options()
my_var1 = StringVar()
my_var1.set('Choose a set')

collection_optionsmenu = CTkOptionMenu(sidebar, width=220, button_color='grey', button_hover_color='white', fg_color='white', values=options_list, variable=my_var1, command=opmenu_text, text_color='#565b5d')
collection_optionsmenu.grid(row=1, column=0, pady=0, sticky='w', padx=20, columnspan=2)

quantity_entry = CTkEntry(sidebar, placeholder_text='Quantity (for example: 1 or 0.5)', fg_color='white', text_color='black', width=220, border_width=2)
quantity_entry.grid(row=2, column=0, pady=10, sticky='w', padx=20, columnspan=2)

submit_button = CTkButton(sidebar, text='ADD', width=100, fg_color=green_color, hover_color='#0b6e4f', command=lambda: button_pressed('add'))
submit_button.grid(row=3, column=0, pady=0, sticky='w', padx=20, columnspan=1)

remove_button = CTkButton(sidebar, text='REMOVE', width=100, fg_color=red_color, hover_color=dark_red_color, command=lambda: button_pressed('remove'))
remove_button.grid(row=3, column=1, pady=0, sticky='w', padx=0, columnspan=1)

refresh_button = CTkButton(sidebar, text='REFRESH', width=100, fg_color='grey', hover_color='#0b6e4f', command=refresh_price)
refresh_button.grid(row=4, column=0, pady=10, sticky='w', padx=20, columnspan=1)

export_button = CTkButton(sidebar, text='EXPORT CSV', width=100, fg_color='grey', hover_color='#0b6e4f', command=export_csv, state=DISABLED)  # 
export_button.grid(row=5, column=0, pady=0, sticky='w', padx=20, columnspan=1)

# create portfolio_value frame and contents
portfolio_value = CTkFrame(window, fg_color='#1d2951', corner_radius=20)
portfolio_value.grid(row=4, column=0, padx=20, ipady=0, pady=20, sticky='nsew')
portfolio_value.grid_columnconfigure((1,2), weight=1)

portfolio_value_title = CTkLabel(portfolio_value, text='Portfolio Value:', font=title_font)
portfolio_value_title.grid(row=0, column=0, padx=20, pady=20, sticky='wens')

portfolio_value_title2 = CTkLabel(portfolio_value, text=calc_portfolio_worth_usd(), font=title_font, text_color=green_color)
portfolio_value_title2.grid(row=0, column=1, padx=0, pady=20, sticky='wns')

portfolio_value_title3 = CTkLabel(portfolio_value, text=calc_portfolio_worth_huf(), font=title_font, text_color=green_color)
portfolio_value_title3.grid(row=1, column=0, padx=0, pady=10, sticky='ens', columnspan=2)

# create the nft grid frame and contents
nft_grid = CTkFrame(window, corner_radius=20, fg_color=lightblue_color)
nft_grid.grid(rowspan=6, row=0, column=1, sticky='wens', pady=20, padx=20, ipadx=200)

#TODO add nft set append panel

# TODO add opensea api key window if api not defined












# create an NFT card with image
#TODO complete the when_price_change() with changing all values in these cards

    # opening and compressing images
nft_widget_width = 200
nft_widget_height = 110

card = CTkFrame(nft_grid, corner_radius=20, fg_color='#808080')
card.pack(padx=10, pady=20)

pil = compress_image('Lil Pudgy')
my_image = CTkImage(light_image=pil, dark_image=pil, size=(nft_widget_width,nft_widget_height))

card_image = CTkLabel(card, text='', image=my_image)
card_image.grid(row=0, column=0, columnspan=2, pady=20, padx=8)

title = CTkLabel(card, text='Lil Pudgy', font=title_font2, fg_color='red', corner_radius=0)
title.grid(row=1, column=0, sticky='w', padx=8, pady=2)

title2 = CTkLabel(card, text='')
title2.grid(row=2, column=0, pady=15)



# create mainloop
window.mainloop()
