#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests as r
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup as bs
from pprint import pprint
import json
r.packages.urllib3.disable_warnings(InsecureRequestWarning) 

VALID_TITLES=['RojoAzul', 'Amarillo', 'Oro', 'Plata', 'Cristal', 'Rubí', 'Zafiro', 'Esmeralda', 'Rojo Fuego', 'Verde Hoja', 'Diamante', 'Perla', 'Platino', 'Oro HeartGold', 'Plata SoulSilver', 'Negro', 'Blanco', 'Negro 2', 'Blanco 2', 'Pokémon X', 'Pokémon Y', 'Rubí Omega', 'Zafiro Alfa', 'Sol', 'Luna', 'Ultrasol', 'Ultraluna', "Let's Go Pikachu!Let's Go Eevee!", 'Espada', 'Escudo', 'Diamante Brillante', 'Perla Reluciente', 'Leyendas: Arceus']
EXCEPTED_POKEMON=["Mew","Typhlosion","Deoxys"]

def list_pkmn():
    url="https://www.wikidex.net/wiki/Lista_de_Pok%C3%A9mon"
    url_html=r.get(url,verify=False).text
    url_html=bs(url_html,"html.parser")
    return url_html.find_all("table",{"class": "tabpokemon"})
def table_unwrapper(table):
    return [{"num":i.find_all("td")[0].text[:-1],"name":i.find_all("td")[1].text[:-1],"url":i.find_all("td")[1].a['href']} for i in table.find_all("tr")[1::]] 

def scrapping(list):
    for i in list:
        #info dumb
        info=i["url"]
        dexnum=i["num"]
        pkmnname=i["name"]

        url=r.get(f"https://www.wikidex.net/{info}",verify=False)

        url_html=bs(url.text,"html.parser")

        info=url_html.find("table",{"class":"datos"})

        types=Cleanse(info.find("tr",{"title":"Tipos a los que pertenece"}).find_all("a")[1::])
        types=[i['title'].replace("Tipo ","") for i in types]

        abilities=Cleanse(info.find("tr",{"title":"Habilidades que puede conocer"}).find_all("a")[1::])
        abilities=[i['title'].replace("Tipo ","") for i in abilities]

        try:
            hidden=Cleanse(info.find("tr",{"title":"Habilidad oculta"}).find_all("a")[1::])
            hidden=[i['title'].replace("Tipo ","") for i in hidden]
        except AttributeError:
            hidden="None"

        pkdex_info=Pokedex(url_html)
        location_info=Location(url_html)

        stats=Stats(url_html,pkmnname)
        try:
            evo=evolution(url_html,pkmnname,evo)
        except UnboundLocalError:
            evo=evolution(url_html,pkmnname)
        #level_moves=url_html.find_all("section",{"class":"tabber__section"})[0]

        #MO_MT=[i.text for i in url_html.find_all("section",{"class":"tabber__section"})[1].find_all("tr")]

        save_json(pkmnname,dexnum,types,abilities,hidden,stats,location_info,pkdex_info,evo)
        #print_json(pkmnname,dexnum,types,abilities,hidden,stats,location_info,pkdex_info,evo)

def print_json(pkmnname,dexnum,types,abilities,hidden,stats,location_info,pkdex_info,evo):
    pprint({"dex number":dexnum,
                "pokemon name":pkmnname,
                "types":types,
                "abilities":abilities,
                "hidden abilities":hidden,
                "stats":{
                    "hp":stats[0],
                    "atk":stats[1],
                    "def":stats[2],
                    "atk esp":stats[3],
                    "def esp":stats[4],
                    "speed":stats[5]},
                "location":location_info,
                "pokedex":pkdex_info,
                "evolution":evo})
def save_json(pkmnname,dexnum,types,abilities,hidden,stats,location_info,pkdex_info,evo):
    print(f"saving {pkmnname}...")
    with open(f"json_files\\{dexnum}-{pkmnname}.json","w",encoding="utf-8") as f:
        data={"dex number":dexnum,
                "pokemon name":pkmnname,
                "types":types,
                "abilities":abilities,
                "hidden abilities":hidden,
                "stats":{
                    "hp":stats[0],
                    "atk":stats[1],
                    "def":stats[2],
                    "atk esp":stats[3],
                    "def esp":stats[4],
                    "speed":stats[5]},
                "location":location_info,
                "pokedex":pkdex_info,
                "evolution":evo}
        f.write(json.dumps(data,indent=4,ensure_ascii=False))
        f.close()
    print(f"{pkmnname} saved!")

# Some pages doesn't have the tag require to continue without crashing, that's when the page had notation, to fix this it got remove the tag 
# from the list if it's a notation
def Cleanse(list):
    for i in list:
        try:
            i['title']
        except KeyError:
            list.remove(i)
    return list

def Stats(url_html,pkmnname):
    raw_stats=url_html.find_all("table",{"class","tabpokemon"}) #html table
    try:
        raw_stats[0]['style']
        raw_stats=raw_stats[1]
    except KeyError:
        raw_stats=raw_stats[1] if pkmnname in EXCEPTED_POKEMON  else raw_stats[0]
    return [i.find("td").text[:-1] for i in raw_stats.find_all("tr")[1:7]]

def Pokedex(url_html):
    pkdex_table=url_html.find_all("table",{"class":"pokedex"})[0].find_all("tr")    
    pkdex_info={}
    for i in pkdex_table[1::]:
        th=i.find_all("th")
        if len(th)==2:
            region=th[1].text[:-1]
            if region in VALID_TITLES: pkdex_info[region]=i.find_all("td")[0].text[:-1]
    return pkdex_info

def Location(url_html):
    location_table=url_html.find_all("table",{"class":"localizacion"})[0].find_all("tr")
    location_info={}
    for i in location_table[1::]:
        row=[row_content for row_content in i.text.split("\n") if row_content!=""]
        if row[0] in VALID_TITLES: location_info[row[0]]=row[1::]
    return location_info


def evolution(url_html,pkmname,previous=None):
#   To save some resources, it will be check if the new pokemon is a evolution from the previous or not
    if previous==None or pkmname not in previous:
        evo_raw=url_html.find_all("table",{"class":"evolucion"})[-1].find_all("tr")
        len_line=0
        evolution_lane=[]
        for i in evo_raw:
            evo_stack=i.find_all("td")[::-1]
            len_line=len(evo_stack) if len_line<len(evo_stack) else len_line
            row=["" for _ in range(0,len_line)]
            for count,j in enumerate(evo_stack,1):
                row[count*-1]=j.text[:-1]
                if row not in evolution_lane:
                    evolution_lane.append(row)
        return evolution_lane
    else:
        return previous

if __name__=="__main__":
    gen=[table_unwrapper(i) for i in list_pkmn()]
    #gen 1 ok
    #gen 2 ok
    #gen 3 ok
    #gen 4 ok 
    #gen 5 ok
    #gen 6 ok 
    #gen 7 problem
    #gen 8 problem
    scrapping(gen[1])