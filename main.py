from customtkinter import *
from PIL import ImageTk, Image, ImageEnhance
import requests
from currency_converter import CurrencyConverter

from tkinter import messagebox
import json
import time

# global vars
widget_list = []
data = 'data.json'
app_data = 'app_data.json'

crypto_prices = {
            'SOL': 0,
            'ETH': 0,
            'MATIC': 0
        }
dollar_huf = 0

# create styling
# TODO organize coloring variables and apperance.json

    # fonts
main_title_font = ('Helvetica', 40, 'bold')
title_font = ('Helvetica', 24, 'bold')
title_font2 = ('Helvetica', 18, 'bold')
title_font3 = ('Helvetica', 14, 'bold')
vol24_font = ('Helvetica', 34, 'bold')
default_font = ('Helvetica', 13)
default_font_bold = ('Helvetica', 13, 'bold')

    # colors
window_color = ('#C5C6C7', '#1F2833')
message_color = ('black', 'white')

default_text_color = 'black' # mvp message, watchlist message, (BUY, SELL, REFRESH, EXPORT, SUBMIT, CONFIRM)-button text, (quantity, set, url)-entry, op menu 1,2 on refresh function
vol24_percent = '#39e75f' # bright green
green_color = ('black', '#08a045') # portfolio value text, buy button
dark_green_color = '#077b37' # buy button hover
red_color = ('black','#ff2c2c') # remove button, watchlist frame background color
dark_red_color = '#d1001f'  # remove button hover
greyed_out_color = '#565b5d' # options menu default text
opmenu_color = 'white'
opmenu_button_color = 'grey'
opmenu_button_hover_color = 'white'
orange_color = 'orange' # mvp frame background color
blue_green_color = '#45A29E' # nft grid frame background color
nigh_blue_color = '#1F2833'

# create main window
window = CTk(fg_color=window_color)
window.withdraw()  # auto switch to this window from terminal, vscode, etc....

window.title('NFT Portfolio')
window.geometry('1440x900')
window.state('zoomed')
window.minsize(width=1400, height=690)

window.grid_columnconfigure((2,4), weight=1)
window.grid_columnconfigure((0,6), weight=9)
window.grid_rowconfigure((1,3,5), weight=1)
window.grid_rowconfigure((2), weight=10)


set_default_color_theme("apperance.json")
set_appearance_mode('system')
# set_appearance_mode('dark')
# TODO apperance mode selector button


#|||||||||||||||||||||||||||||||||||||    FRONTEND FUNCTIONS    ||||||||||||||||||||||||||||||||||||||||||||||||||
# open image as CTk object
def ctk_image_open(filename):
    image_path = f'images/{filename}.png'
    pil = Image.open(image_path)
    return CTkImage(light_image=pil, dark_image=pil, size=(80, 80))


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
                        writejson(opened_data)
                        refresh_gui('wallet')
                        return

                    elif id == 'remove':
                        if float(choosen_quantity) <= item['quantity']:
                            item['quantity'] -= float(choosen_quantity)
                            messagebox.showinfo("Information", "Item(s) Removed!")
                            writejson(opened_data)
                            refresh_gui('wallet')
                            return

                        else:
                            # CTkMessagebox(title="Error", message="NFT quantity can't be minus", icon="cancel")
                            messagebox.showwarning('error', f"You only have {int(item['quantity'])} {item['name']}(s)")
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




#|||||||||||||||||||||||||||||||||||||    FRONTEND REFRESH FUNCTIONS    ||||||||||||||||||||||||||||||||||||||||||

# refresh options menu color when option is selected
def opmenu_text(selected_value): # important to add a kwarg, to enable def to accept arguments
    collection_optionsmenu.configure(variable=my_var1, text_color=default_text_color)

def opmenu_text2(selected_value): # important to add a kwarg, to enable def to accept arguments
    collection_optionsmenu2.configure(variable=my_var2, text_color=default_text_color)    


def refresh_mvp():
    vol_24h_percent.configure(text=f'{find_mvp()['vol_change']}%') # refresh MVP
    mvp_title.configure(text=f'MVP set: {find_mvp()['name']}') # refresh MVP


def refresh_gui(source):
    ''''''
    convert_floor() # updates floor price in $
    total_usd()  # updates the total portfolio worth

    portfolio_value_title2.configure(text=format_currencies(portfolio_total(), 'USD'))  # re calculate total portfolio and refresh label
    portfolio_value_title3.configure(text=format_currencies(portfolio_total(), 'HUF'))  # re calculate total portfolio and refresh label
    find_mvp()  # re calculate MVP
    vol_24h_percent.configure(text=f'{find_mvp()['vol_change']}%')  # refresh mvp title
    mvp_title.configure(text=f'MVP set: {find_mvp()['name']}')  # refresh mvp percent
    destroy_nftgrid()
    build_nftgrid()

    # if buy / sell button pressed
    if source == 'wallet':
        quantity_entry.delete(0, END) # empty the entry box after pressing buy / sell button
        my_var1.set('Choose a set')  # reset options menu
        collection_optionsmenu.configure(text_color='#565b5d')  # reset options menu color

    # if submit / confirm button pressed
    elif source == 'watchlist':
        collection_optionsmenu.configure(values=options())  # refresh option list options to add / remove a set
        collection_optionsmenu2.configure(values=options())  # refresh option list options to add / remove a set
        my_var1.set('Choose a set')  # set default option
        my_var2.set('Choose a set')  # set default option
        set_name_entry.delete(0, END)
        url_entry.delete(0, END)


def remove_watchlist():
    '''input nftset name, removes that nft set from the app_data.json file and rearranges the higher index elements id in the json file'''
    app_data_list = readjson()
    if len(app_data_list) == 1:
        messagebox.showwarning('error', "You can't delete the last item!")
        return

    target = my_var2.get()
    if target == 'Choose a set':
        messagebox.showwarning('error', 'Choose a set first!')
        return

    # find id of target set
    target_id = 0
    for item in app_data_list:
        if item['name'] == target:
            target_id = item["watchlist_id"]
            if item['quantity'] > 0.0:
                messagebox.showwarning('error', f"You hold one {item['name']}, can't delete it!")
                return

    # create new list with changing id and ignoring the target set
    new_list_without_target = []
    for item in app_data_list:
        if not item['name'] == target: # add {} item to the new list if not the target set
            if item["watchlist_id"] > target_id: # change the id by substracting 1 if bigger than the removed id
                item["watchlist_id"] -= 1
            new_list_without_target.append(item)
    #
    writejson(new_list_without_target)
    messagebox.showinfo('error', f'{target} deleted!')
    refresh_gui('watchlist')


def build_nftgrid():
    '''build the widgets from the json file'''
    app_data_list = readjson()
    start_row = 1
    for item in app_data_list:
        if item["watchlist_id"] % 2 == 0:  # if id is even (paros), column=1
            column = 1
            row = start_row
            start_row += 1

        else:
            column = 0
            row = start_row
  
        # create the widget and store it in a list
        w_frame = CTkFrame(nft_grid, width=200, height=150, corner_radius=15, fg_color=(blue_green_color,blue_green_color), border_color=('black','#66FCF1'), border_width=3)
        w_frame.grid_columnconfigure((0,1), weight=1)
        
        # styling
        titles_color = nigh_blue_color
        labels_color = 'white'

        # different styling for non holding sets
        if item["quantity"] == 0:
            w_frame.configure(fg_color = ('#ffffff', '#0B0C10'))
            titles_color = ('black','#C5C6C7')
            labels_color = (blue_green_color,'#66FCF1')

        # title
        set_title = CTkLabel(w_frame, text=item["name"], font=title_font2, width=220, text_color=titles_color, anchor='w')
        set_title.grid(row=0, column=0, padx=10, pady=10, sticky='wens', columnspan=2)
        
        # attribute labels
        width = 220
        heigh = 10

        if item["quantity"].is_integer():
            q = int(item['quantity'])

        else:
            q = item["quantity"]

        title_line = CTkFrame(w_frame, fg_color=titles_color, height=2)
        title_line.grid(row=1, column=0, padx=10, sticky='ew', columnspan=2)

        #
        set_floor_title = CTkLabel(w_frame, text=f'Floor price:', anchor='sw', font=title_font3, text_color=titles_color, wraplength=80)
        set_floor_title.grid(row=2, column=0, padx=10, pady=0, sticky='wens')
        
        set_floor_label = CTkLabel(w_frame, text=f'{item["token_floor_price"]} {item['token']}', anchor='nw', font=default_font, text_color=labels_color, wraplength=80)
        set_floor_label.grid(row=3, column=0, padx=10, pady=0, sticky='wens')

        #
        set_floor_usd_title = CTkLabel(w_frame, text=f'Floor price ($):', anchor='sw', font=title_font3, text_color=titles_color, wraplength=100)
        set_floor_usd_title.grid(row=2, column=1, padx=10, pady=0, sticky='wens')
        
        set_floor_usd_label = CTkLabel(w_frame, text=f'{format_currencies(item['usd_floor_price'], 'USD')}', anchor='nw', font=default_font, text_color=labels_color, wraplength=80)
        set_floor_usd_label.grid(row=3, column=1, padx=10, pady=0, sticky='wens')

        #
        set_holdings_title = CTkLabel(w_frame, text=f'Holdings:', anchor='sw', font=title_font3, text_color=titles_color)
        set_holdings_title.grid(row=4, column=0, padx=10, pady=0, sticky='wens')


        set_holdings_label = CTkLabel(w_frame, text=f'{format_currencies(item['total$'], 'USD')}', anchor='nw', font=default_font, text_color=labels_color)
        set_holdings_label.grid(row=5, column=0, padx=10, pady=0, sticky='wens', columnspan=2)

        #
        set_quantity_title = CTkLabel(w_frame, text=f'Quantity:', anchor='sw', font=title_font3, text_color=titles_color)
        set_quantity_title.grid(row=4, column=1, padx=10, pady=0, sticky='wens')

        set_quantity_label = CTkLabel(w_frame, text=f'{q}', anchor='nw', font=default_font, text_color=labels_color)
        set_quantity_label.grid(row=5, column=1, padx=10, pady=0, sticky='wens')

        #
        set_total_huf_title = CTkLabel(w_frame, text=f'Holdings (HUF):', anchor='sw', font=title_font3, text_color=titles_color)
        set_total_huf_title.grid(row=6, column=0, padx=10, pady=0, sticky='wens', columnspan=2)

        set_total_huf_label = CTkLabel(w_frame, text=f'{format_currencies(item['total$'], 'HUF')}', anchor='nw', font=default_font, text_color=labels_color)
        set_total_huf_label.grid(row=7, column=0, padx=10, pady=0, sticky='wens', columnspan=2)

        # hide it for now
        # set_vol24_title = CTkLabel(w_frame, text=f'VOL (24h):', anchor='sw', font=title_font3, text_color=nigh_blue_color)
        # set_vol24_title.grid(row=4, column=1, padx=10, pady=0, sticky='wens')

        # set_vol24_label = CTkLabel(w_frame, text=f'{item['vol_24']}%', anchor='nw', font=default_font, text_color='white')
        # set_vol24_label.grid(row=5, column=1, padx=10, pady=0, sticky='wens')

        #
        empty_label = CTkLabel(w_frame, text='')
        empty_label.grid(row=8, column=0, padx=10, pady=3, sticky='wens', columnspan=2)

        widget_list.append(w_frame)
        w_frame.grid(column=column, row=row, pady=15, padx=30, ipadx=0)


def destroy_nftgrid():
    for item in widget_list:
        item.destroy()


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


def export_csv():
    messagebox.showinfo("Information", "CSV Exported!")


def find_mvp():
    '''only opensea nft play, check json file for the MVP set name and volume%, returns them in a dictionary'''
    current_biggest = 0.00
    current_minus = -1.00
    mvp = ''
    mvp2 = ''
    opened_data = readjson()

    for item in opened_data:
        set_vol = float(item["vol_24"]) 
        if set_vol > current_biggest:
            current_biggest = set_vol
            mvp = item["name"]

        elif set_vol < 0.00 and set_vol > current_minus:
            current_minus = set_vol
            mvp2 = item["name"]

    if mvp == '':
        mvp = mvp2
        current_biggest = current_minus
        # TODO change text color to red on mvp frame

    mvp_dict = {
        'name': mvp,
        'vol_change': current_biggest
    }

    return mvp_dict


def is_float(str):
    '''check if str is a float or no, return True or False'''
    if str.isdigit() == False:
        try:
            float(str)
            return True
        except ValueError:
            return False
        

def refresh_price():
    '''refreshes floor prices in the json file'''
    opened_data = readjson()

    for item in opened_data:
        time.sleep(1)
        if item["platform"] == "opensea":
            opensea_dict = get_opensea_price(item["api_name_format"])
            item["token_floor_price"] = opensea_dict['floor']
            item["vol_24"] = opensea_dict['vol24']

        elif item["platform"] == "magiceden":
            magiceden_dict = get_magiceden_price(item["api_name_format"])
            item["token_floor_price"] = magiceden_dict['floor']
            item["vol_24"] = magiceden_dict['vol24']
            
    writejson(opened_data)
    
    dollar_to_huf() # refresh HUF-USD price too
    fetch_crypto_prices() # refresh ETH, SOL, etc.....
    messagebox.showinfo("Information", "Prices Refreshed!")
    refresh_gui('refresh_function')


#|||||||||||||||||||||||||||||||||||||    CURRENCY CALCULATING / SUM FUNCTIONS    |||||||||||||||||||||||||||||||
def convert_floor():
    '''write json with floor prices converted to usd'''
    my_list = readjson()
    #
    for item in my_list:
        item['usd_floor_price'] = convert_token_usd(item['token_floor_price'], item['token'])
    #
    writejson(my_list)


def total_usd():
    my_list = readjson()
    #
    for item in my_list:
        item['total$'] = int(item['usd_floor_price'] * item['quantity'])
    #
    writejson(my_list)


def portfolio_total():
    '''returns portfolio value in int, $'''
    total_usd = 0
    opened_data = readjson()

    for item in opened_data:
        total_usd += item["total$"]

    return total_usd


def convert_token_usd(token_quantity, currency):
    '''input token quantity and currency, return int usd'''
    usd_floor = int(token_quantity * crypto_prices[currency])
    return usd_floor


def format_currencies(num, currency):
    # input a $ number, and 'USD' or 'HUF'. Return readable format (also converts curreny to huf, when 'HUF' given)
    if currency == 'HUF':
        total_currency_str = str(num * dollar_huf) # converts here also
        cur = ' Ft.'
    else:
        total_currency_str = str(num)
        cur = ' $'

    length = len(total_currency_str)
    if length == 5:
        formatted_currency = total_currency_str[:2] + ',' + total_currency_str[2:]

    elif length == 6:
        formatted_currency = total_currency_str[:3] + ',' + total_currency_str[3:]

    elif length == 7:
        formatted_currency = total_currency_str[:1] + ',' + total_currency_str[1:4] + ',' + total_currency_str[4:]
    
    elif length == 8:
        formatted_currency = total_currency_str[:2] + ',' + total_currency_str[2:5] + ',' + total_currency_str[5:]

    elif length == 9:
        formatted_currency = total_currency_str[:3] + ',' + total_currency_str[3:6] + ',' + total_currency_str[6:]

    elif length == 10:
        formatted_currency = total_currency_str[:1] + ',' + total_currency_str[1:4] + ',' + total_currency_str[4:7] + ',' + total_currency_str[7:]
    else:
        return f'{total_currency_str}{cur}'
    
    return f'{formatted_currency}{cur}'


#|||||||||||||||||||||||||||||||||||||    API / ONLINE FUNCTIONS    |||||||||||||||||||||||||||||||||||||||||||||
def dollar_to_huf():
    '''refresh global INT variable (dollar_huf) to 1$ worth of huf'''
    global dollar_huf
    c = CurrencyConverter()
    dollar_huf_object = c.convert(1, "USD", "HUF")
    dollar_huf_converted = "{:,.0f}".format(dollar_huf_object)
    dollar_huf = int(dollar_huf_converted)


def get_opensea_price(required_format_name):
    """enter nft collection name, returns dictionary floor price formatted to str, vol24 str"""

    opensea_url = f"https://api.opensea.io/api/v2/collections/{required_format_name}/stats"
    opensea_headers = {
        "accept": "application/json",
        "x-api-key": opensea_api
    }
    response = requests.get(opensea_url, headers=opensea_headers)

    if str(response) == '<Response [200]>':
        data = response.json()
        floor_price = data["total"]["floor_price"]
        volume_change = data['intervals'][0]['volume_change']

        formatted_volume_change = format(volume_change, ".2f")
        formatted_floor = format(floor_price, ".2f")

        my_dict = {
            'floor': float(formatted_floor),
            'vol24': float(formatted_volume_change)
        }
        return my_dict

    else:
        return 'api error'


def get_magiceden_price(required_format_name):
    """enter nft collection name, returns floor price and value 0 volume change as a dict"""
    magiceden_url = f"https://api-mainnet.magiceden.dev/v2/collections/{required_format_name}/stats"
    magiceden_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {magiceden_bearer}"
    }
    response = requests.get(magiceden_url, headers=magiceden_headers)
    if str(response) == '<Response [200]>':
        data = json.loads(response.text)
        if data['listedCount'] == 0:
            return 'api error'

        floor_price = data["floorPrice"]
        formatted_floor = "{:,.2f}".format(floor_price / 1000000000)

        my_dict = {
                'floor': float(formatted_floor),
                'vol24': 0.0
            }
        return my_dict
    
    else:
        return 'api error'

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


def opensea_url_validator():
    '''validates the opensea url and add set to wallet for tracking, writes the data.json file'''
    opensea_prefix = 'https://opensea.io/collection/'
    magiceden_prefix = 'https://magiceden.io/marketplace/'
    this_prefix = ''

    test_this_url = url_entry.get()

    if test_this_url.startswith(opensea_prefix):
        this_prefix = opensea_prefix
    elif test_this_url.startswith(magiceden_prefix):
        this_prefix = magiceden_prefix

    #
    if this_prefix != '':
        set_name = test_this_url.removeprefix(this_prefix)
        #
        if this_prefix == opensea_prefix:
            api_response = get_opensea_price(set_name)
            token = 'ETH'

        elif this_prefix == magiceden_prefix:
            api_response = get_magiceden_price(set_name)
            token = 'SOL'
        #
        if not api_response == 'api error':
            wallet_list = readjson()
            for item in wallet_list:
                if item['api_name_format'] == set_name:
                    messagebox.showwarning('error', f'{item['name']} already in Watchlist!')
                    return
                last_watchlist_id = item['watchlist_id']
            wallet_id = last_watchlist_id + 1
            #
            wallet_list.append({
                "name": set_name_entry.get(),
                "quantity": 0.0,
                "platform": "opensea",
                "api_name_format": set_name,
                "token": token,
                "token_floor_price": api_response['floor'],
                "usd_floor_price": 0,
                "total$": 0,
                "vol_24": api_response['vol24'],
                "watchlist_id": wallet_id
            })
            #
            writejson(wallet_list)
            messagebox.showinfo('noerror', f'{set_name_entry.get()} added to Watchlist!')
            # TODO append and sort alphabetically the options list
            refresh_gui('watchlist')
            

        else:
            messagebox.showwarning('error', 'API error, double check the URL!')

    else:
        messagebox.showwarning('error', 'Not an opensea URL!')


def validate_api_window():
    if opensea_api == "":
        window.withdraw()  # call again to hide main window
        popup_api_window.deiconify()


def validate_api():
    '''validates the api key entered by the user, and if valid, stores the api key in the app_data json file'''
    global opensea_api
    global magiceden_bearer

    opensea_api = api_entry.get()
    bearer = bearer_entry.get()

    api_response = get_opensea_price('boredapeyachtclub')
    if api_response == 'api error':
        opensea_api = ""
        messagebox.showwarning('error', f'Key is invalid, try again!')
    else:
        popup_api_window.destroy()
        window.deiconify()

        with open(app_data, 'r') as appdata:
            appdata_dict = json.load(appdata)

        appdata_dict['opensea_api'] = opensea_api

        # check magiceden bearer token
        if bearer != 'magiceden bearer (optional)...':
            appdata_dict['magiceden_bearer'] = bearer

        with open(app_data, 'w') as appdata:
            json.dump(appdata_dict, appdata, indent=4)


def read_api():
    '''reads the api from the json file, update the global opensea api variable'''
    global opensea_api
    with open(app_data, 'r') as appdata:
        appdata_dict = json.load(appdata)

    opensea_api = appdata_dict["opensea_api"]


def read_bearer():
    '''reads the magiceden bearer from the json file, update the global magiceden bearer variable'''
    global magiceden_bearer
    with open(app_data, 'r') as appdata:
        appdata_dict = json.load(appdata)

    magiceden_bearer = appdata_dict["magiceden_bearer"]    

# create api checker window and hide it instantly
popup_api_window = CTkToplevel()
popup_api_window.withdraw()
popup_api_window.geometry('500x250')
popup_api_window.title('API KEY VALIDATOR')
popup_api_window.columnconfigure(0, weight=1)
popup_api_window.rowconfigure(0, weight=1)

popup_frame = CTkFrame(popup_api_window)
popup_frame.grid(row=0, column=0, sticky='wens')

api_title = CTkLabel(popup_frame, text='Enter your Opensea API key below:', font=title_font2)
api_title.pack()

api_message1 = CTkLabel(popup_frame, text="if you don't have one, get it for free on https://docs.opensea.io/reference/api-keys", wraplength=300)
api_message1.pack(pady=2)

emptyframe1 = CTkFrame(popup_frame, width=300, fg_color=('black', '#66FCF1'), height=3)
emptyframe1.pack(pady=5)

api_message2 = CTkLabel(popup_frame, text="You can use a Magiceden bearer token for solana NFT sets, but it's optional. Contact creators@magiceden.io for a bearer token.", wraplength=300)
api_message2.pack(pady=2)

emptyframe2 = CTkFrame(popup_frame, width=300, fg_color=('black', '#66FCF1'), height=3)
emptyframe2.pack(pady=5)

api_entry = CTkEntry(popup_frame, placeholder_text='Opensea api key...', width=250)
api_entry.pack()

bearer_entry = CTkEntry(popup_frame, placeholder_text='Magiceden bearer (optional)...', width=250)
bearer_entry.pack(pady=5)

api_button = CTkButton(popup_frame, text='ENTER', command=validate_api)
api_button.pack()

# program start
dollar_to_huf()  # catch live prices
fetch_crypto_prices()  # catch live prices
convert_floor() # updates floor price in $
total_usd()  # updates the total portfolio worth
read_api() # create api variable from json file
read_bearer()  # create magiceden bearer variable from json file
validate_api_window()  # open api window if api don't given in the json file
#|||||||||||||||||||||||||||||||||||||    FRONTEND    ||||||||||||||||||||||||||||||||||||||||||||||||||

# create mvp frame and contents
mvp = CTkFrame(window, corner_radius=20)
mvp.grid(row=0, column=1, pady=20, sticky='nsew', padx=20, ipady=8)

mvp_title = CTkLabel(mvp, text=f'MVP set: {find_mvp()['name']}', font=title_font, width=350, anchor='w', padx=20)
mvp_title.pack(pady=20)

tropy_icon = ctk_image_open('trophy')
tropy_icon_label = CTkLabel(mvp, text='', image=tropy_icon)
tropy_icon_label.pack()

vol_24h_percent = CTkLabel(mvp, text=f'{find_mvp()['vol_change']}%', font=vol24_font, text_color=vol24_percent, width=350, anchor='e', padx=10)
vol_24h_percent.pack()

mvp_help_info = CTkLabel(mvp, text='(volume in last 24h)', width=350, anchor='e', padx=10, text_color=message_color)
mvp_help_info.pack()

# create sidebar frame and contents
sidebar = CTkFrame(window, corner_radius=20)
sidebar.grid(row=2, column=1, padx=20, sticky='nsew', ipady=15)
sidebar.grid_columnconfigure((0,1), uniform='a')

sidebar_title = CTkLabel(sidebar, text='Edit Wallet', font=title_font, anchor='w', padx=20)
sidebar_title.grid(row=0, column=0, columnspan=2, pady=20, sticky='wens')

    # create the options menu
my_var1 = StringVar()
my_var1.set('Choose a set')
collection_optionsmenu = CTkOptionMenu(sidebar, width=220, fg_color=opmenu_color, values=options(), variable=my_var1, command=opmenu_text, text_color=greyed_out_color)
collection_optionsmenu.grid(row=1, column=0, pady=0, sticky='w', padx=20, columnspan=2)

quantity_entry = CTkEntry(sidebar, placeholder_text='Quantity (for example: 1 or 0.5)', fg_color='white', width=220, border_width=2, text_color=default_text_color)
quantity_entry.grid(row=2, column=0, pady=10, sticky='w', padx=20, columnspan=2)

add_button = CTkButton(sidebar, text='BUY', width=100, command=lambda: button_pressed('add'), border_color=green_color, text_color=green_color, fg_color=('#08a045','#0B0C10'), hover_color = (dark_green_color, "#1F2833"))
add_button.grid(row=3, column=0, pady=0, sticky='w', padx=20, columnspan=1, ipady=5)

remove_button = CTkButton(sidebar, text='SELL', width=100, command=lambda: button_pressed('remove'), border_color=red_color, text_color=red_color, fg_color=('#ff2c2c','#0B0C10'), hover_color = (dark_red_color, "#1F2833"))
remove_button.grid(row=3, column=1, pady=0, sticky='w', padx=0, columnspan=1, ipady=5)

# refresh_button = CTkButton(sidebar, text='REFRESH PRICES', width=220, command=refresh_price)
refresh_button = CTkButton(sidebar, text='REFRESH', width=100, command=refresh_price)
refresh_button.grid(row=4, column=0, pady=10, sticky='w', padx=20, columnspan=1, ipady=5)

# export_button = CTkButton(sidebar, text='EXPORT CSV', width=100, command=export_csv, state=DISABLED)
# export_button.grid(row=5, column=0, pady=0, sticky='w', padx=20, columnspan=1, ipady=5)

# create portfolio_value frame and contents
portfolio_value = CTkFrame(window, corner_radius=20)
portfolio_value.grid(row=4, column=1, padx=20, ipady=0, pady=20, sticky='nsew')
portfolio_value.grid_columnconfigure((1,2), weight=1)

portfolio_value_title = CTkLabel(portfolio_value, text='Portfolio Value:', font=title_font)
portfolio_value_title.grid(row=0, column=0, padx=20, pady=20, sticky='wens')

portfolio_value_title2 = CTkLabel(portfolio_value, text=format_currencies(portfolio_total(), 'USD'), font=title_font, text_color=('#45A29E','white'))
portfolio_value_title2.grid(row=0, column=1, padx=0, pady=20, sticky='wns')

portfolio_value_title3 = CTkLabel(portfolio_value, text=format_currencies(portfolio_total(), 'HUF'), font=title_font, text_color=('#45A29E','white'))
portfolio_value_title3.grid(row=1, column=0, padx=0, pady=10, sticky='ens', columnspan=2)

# create the nft grid frame and contents
nft_grid = CTkScrollableFrame(window, corner_radius=20)
nft_grid.grid(rowspan=6, row=0, column=3, sticky='wens', pady=20, padx=0, ipadx=200)

nft_grid_maintitle = CTkLabel(nft_grid, text='Watchlist items', font=main_title_font, text_color=('black', 'white'))
nft_grid_maintitle.grid(row=0, column=0, columnspan=2, pady=10)

# create watchlist editor frame and contents
watchlist = CTkFrame(window, corner_radius=20)
watchlist.grid(row=0, column=5, padx=20, pady=20, sticky='wen', rowspan=3)

padding_label1 = CTkLabel(watchlist, text='')
padding_label1.grid(row=0, column=0, columnspan=2, pady=0, padx=20)

watchlist_title = CTkLabel(watchlist, text='Add to Watchlist', font=title_font)
watchlist_title.grid(row=1, column=0, columnspan=2, pady=0, padx=20, sticky='w')

watching_list_message = CTkLabel(watchlist, text='(Watchlist items can be added to wallet later.)', text_color=message_color, wraplength=280)
watching_list_message.grid(row=2, column=0, columnspan=2, pady=0, padx=20)

padding_label2 = CTkLabel(watchlist, text='')
padding_label2.grid(row=3, column=0, columnspan=2, pady=0, padx=20)

set_name_entry = CTkEntry(watchlist, placeholder_text='Enter a set name', fg_color='white', border_width=2, text_color=default_text_color)
set_name_entry.grid(row=4, column=0, columnspan=2, pady=0, padx=20, sticky='w')

url_entry = CTkEntry(watchlist, placeholder_text='paste collection url', fg_color='white', border_width=2, text_color=default_text_color)
url_entry.grid(row=5, column=0, columnspan=2, pady=2, padx=20, sticky='w')

submit_button = CTkButton(watchlist, text='SUBMIT', command=opensea_url_validator)
submit_button.grid(row=6, column=0, pady=4, padx=20, sticky='w', ipady=5)
#
padding_label3 = CTkLabel(watchlist, text='')
padding_label3.grid(row=7, column=0, columnspan=2, pady=20, padx=20)

remove_watchlist_title = CTkLabel(watchlist, text='Remove from Watchlist', font=title_font)
remove_watchlist_title.grid(row=8, column=0, columnspan=2, pady=15, padx=20, sticky='w')

    # create the options menu 2
my_var2 = StringVar()
my_var2.set('Choose a set')
collection_optionsmenu2 = CTkOptionMenu(watchlist, fg_color=opmenu_color, values=options(), variable=my_var2, command=opmenu_text2, text_color=greyed_out_color)
collection_optionsmenu2.grid(row=9, column=0, pady=0, sticky='w', padx=20)

confirm_button = CTkButton(watchlist, text='CONFIRM', command=remove_watchlist)
confirm_button.grid(row=10, column=0, pady=8, padx=20, sticky='w', ipady=5)

padding_label4 = CTkLabel(watchlist, text='')
padding_label4.grid(row=11, column=0, columnspan=2, pady=0, padx=20)



build_nftgrid()
window.mainloop()