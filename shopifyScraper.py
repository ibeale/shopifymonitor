import requests
from json import loads, load, dumps, dump
import sys
import time
import utils
from discord_webhook import DiscordWebhook, DiscordEmbed
import os


def get_json(link: str):
    json_link = link + "/products.json?limit=300"
    response = requests.get(json_link, timeout=10, proxies=utils.get_proxy())
    json = response.json()
    return json["products"]


def main():
    # When changing links, make sure to delete the database.json file
    hook = "https://discordapp.com/api/webhooks/698641374895145021/DpTKruC5Q_XgqBCBxTwBKMLJVSrQnxsFYbmDJONtagmV-NyYs0dK4SpHm_akIwLbqXb5"
    link = "https://moanabikini.com"
    try:
        with open("database.json", "r") as database:
            dbjson = loads(database.read())
            id_list = list(map(lambda prod: prod["id"], dbjson))
    except FileNotFoundError:
        print("Making Request")
        json = get_json(link)
        with open("database.json", "w") as database:
            dump(json, database)
        id_list = list(map(lambda prod: prod["id"], json))

    while True:
        print("Scraping")
        json = get_json(link)
        with open("database.json", "r") as database:
            dbjson = loads(database.read())

        for product in json:
            if product["id"] not in id_list:
                with open("database.json", "w") as database:
                    dump(json, database)
                print("New Item Found")
                webhook = DiscordWebhook(url=hook)
                embed = DiscordEmbed(title=product["title"])
                embed.set_image(url=product["images"][0]["src"])
                for variant in product["variants"]:
                    embed.add_embed_field(name=f'{variant["title"]} -- {variant["price"]}',
                                          value=f"[Purchase]({link}/cart/{variant['id']}:1) -- AVAILABLE: {variant['available']}",
                                          inline=True)
                webhook.add_embed(embed)
                webhook.execute()
                id_list.append(product["id"])
            else:
                for product2 in dbjson:
                    if product["id"] == product2["id"]:
                        for variant in product["variants"]:
                            for variant2 in product2["variants"]:
                                if (variant["id"] == variant2["id"]) and (not variant2["available"] and variant["available"]):
                                    webhook = DiscordWebhook(url=hook)
                                    embed = DiscordEmbed(
                                        title=f'{product["title"]} RESTOCK in size {variant["title"]}')
                                    embed.set_image(
                                        url=product["images"][0]["src"])
                                    for variant in product["variants"]:
                                        embed.add_embed_field(
                                            name=f'{variant["title"]} -- {variant["price"]}', value=f"[Purchase]({link}/cart/{variant['id']}:1) -- AVAILABLE: {variant['available']}", inline=True)
                                    webhook.add_embed(embed)
                                    webhook.execute()
                                    with open("database.json", "w") as database:
                                        dump(json, database)

        time.sleep(5)
    print(id_list)


if __name__ == "__main__":
    main()
