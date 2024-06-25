This Tkinter nft portfolio application can be used on **Mac**, **Windows** and **Linux**, thanks to CTkinter package in python.

## Features

- Add any NFT set from opensea.io to your collection
- Add / Remove nft to your portfolio
- Refresh their floor price with one click, and also refresh the cyrpto prices (ETH, SOL, MATIC)
- Track the value of your portfolio in USD ($) and HUF (hungarian forint)
- Check the MVP set of the day (Biggest volume change in 24h)

## Coming Features
- GUI for adding a new set to the JSON file
- Export collectin as a csv file
- GUI to display NFT sets as widgets
  - total value
  - name
  - image of the set

## Installation
- install the newest version of python from (python.org) to your machine.
- clone this project
```sh
git clone https://github.com/brycebolton17/CTkinter-NFT-portfolio.git
cd CTkinter-NFT-portfolio sh
```

- install the requirments file with PIP
```sh
pip install -r requirments.txt
```
## Guide
Set up your Opensea API key first
- register on opensea.io and collect your api key for free:
  - https://docs.opensea.io/reference/api-keys

 
- edit main.py (line 17 in the code) and enter your api key here:
```sh
opensea_api = "" # enter your opensea API key here
```
Every NFT collection stored in a JSON file as a snippet like this:
```sh
{
        "name": "Lil Pudgy",
        "quantity": 0.0,
        "platform": "opensea",
        "api_name_format": "lilpudgys",
        "token": "ETH",
        "token_floor_price": "0.75",
        "total$": 0,
        "vol_24": "0.86"
}
```

To add a new NFT set, simply add a new snippet to the data.json file
```sh
{
        "name": "Collection Name",  # A name of the collection you want (can be anything)
        "quantity": 0.0,
        "platform": "opensea",
        "api_name_format": "lilpudgys",  # https://opensea.io/collection/lilpudgys (check the name at the end in the opensea URL)
        "token": "ETH",  # leave it as "ETH" in most cases
        "token_floor_price": "0.00",
        "total$": 0,
        "vol_24": "0.0"
}
```
