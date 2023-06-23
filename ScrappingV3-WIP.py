#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests as r
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup as bs
from pprint import pprint
import json
from os import getcwd
r.packages.urllib3.disable_warnings(InsecureRequestWarning) 

VALID_TITLES=['RojoAzul', 'Amarillo', 'Oro', 'Plata', 'Cristal', 'Rubí', 'Zafiro', 'Esmeralda', 'Rojo Fuego', 'Verde Hoja', 'Diamante', 'Perla', 'Platino', 'Oro HeartGold', 'Plata SoulSilver', 'Negro', 'Blanco', 'Negro 2', 'Blanco 2', 'Pokémon X', 'Pokémon Y', 'Rubí Omega', 'Zafiro Alfa', 'Sol', 'Luna', 'Ultrasol', 'Ultraluna', "Let's Go Pikachu!Let's Go Eevee!", 'Espada', 'Escudo', 'Diamante Brillante', 'Perla Reluciente', 'Leyendas: Arceus']
EXCEPTED_POKEMON=["Mew","Typhlosion","Deoxys"]
SPECIAL_CASE={"Ditto":-2,"Cinderace":-1}
BASE_URL="https://www.wikidex.net/"
BASE_DIR=getcwd()

class PokemonList():
    url=f"{BASE_URL}/wiki/Lista_de_Pok%C3%A9mon"
    def __init__(self,gen_num):
        url_html=r.get(self.url,verify=False).text
        url_html=bs(url_html,"html.parser")
        table=url_html.find_all("table",{"class": "tabpokemon"})[gen_num-1]
        self.PokemonList=self.table_unwrapper(table)
        self.AltPokemonList=self.alternative_forms(table)
    def table_unwrapper(self,table):
        return [
            {
                "num":i.find_all("td")[0].text[:-1],
                "name":i.find_all("td")[1].text[:-1],
                "url":i.find_all("td")[1].a['href']
            } 
                for i in table.find_all("tr")[1::] 
                    if i.find_all("td")[0].text[:-1].isnumeric()
                ] 
    def alternative_forms(self,table):
        return [
            {
                "name":i.find_all("td")[0].text[:-1],
                "url":i.find_all("td")[0].a['href']
            } 
                for i in table.find_all("tr")[1::] 
                    if not i.find_all("td")[0].text[:-1].isnumeric()
                ] 
class Pokemon():
    def __init__(self,data):
        self.name=data["name"]
        self.num=data["num"]
        raw_html=r.get(f'{BASE_URL}{data["url"]}',verify=False).text
        self.html_parse=bs(raw_html,"html.parser")
        self.raw_data=self.html_parse.find("table",{"class":"datos"})
        self.type()
        self.abilities_filter()
        self.Pokedex()
        self.Location()
        self.Stats_debug()
    def type(self):
        raw_types=self.raw_data.find("tr",{"title":"Tipos a los que pertenece"}).find_all("a")[1::]
        self.types=[i['title'].replace("Tipo ","") for i in raw_types if i.has_attr("title")]
    def abilities_filter(self):
        raw_abilities=self.raw_data.find("tr",{"title":"Habilidades que puede conocer"}).find_all("a")[1::]
        self.abilities=[i['title'].replace("Tipo ","") for i in raw_abilities if i.has_attr("title")]
        try:
            raw_hidden=self.raw_data.find("tr",{"title":"Habilidad oculta"}).find_all("a")[1::]
            self.hidden=[i['title'] for i in raw_hidden if i.has_attr("title")]
        except AttributeError:
            self.hidden="None"
    def Pokedex(self):
        pkdex_table=self.html_parse.find_all("table",{"class":"pokedex"})[0].find_all("tr")    
        self.pkdex_info={i.find_all("th")[1].text[:-1]:i.find_all("td")[0].text[:-1] for i in pkdex_table[1::] if len(i.find_all("th")) and i.find_all("th")[1].text[:-1] in VALID_TITLES}
    def Location(self):
        location_table=self.html_parse.find_all("table",{"class":"localizacion"})[0].find_all("tr")
        location_info={}
        for i in location_table[1::]:
            row=[row_content for row_content in i.text.split("\n") if row_content!=""]
            if row[0] in VALID_TITLES: location_info[row[0]]=row[1::]
        self.location_info=location_info
    def Stats_debug(self):
        index=0
        while (1):
            try:
                stats_table=self.html_parse.find_all("table",{"class","tabpokemon"})
                stats_table=stats_table[index].find_all("tr")[1:7]
                stats_names=["hp","atk","def","atk esp","def esp", "speed"]
                self.stats={stat_name:int(stat_value.find("td").text[:-1]) for stat_name,stat_value in tuple(zip(stats_names,stats_table))}
                if(index>1):
                    print(f"index value for {self.name}: {index}")
                    pprint(self.stats)
                break
            except:
                index+=1
    def Stats(self):
        stats_table=self.html_parse.find_all("table",{"class","tabpokemon"})
        index=0
        if(self.name in SPECIAL_CASE.keys()): index=SPECIAL_CASE[self.name]
        elif (self.name in EXCEPTED_POKEMON or stats_table[0].has_attr("style")): index=1
        stats_table=stats_table[index].find_all("tr")[1:7]
        stats_names=["hp","atk","def","atk esp","def esp", "speed"]
        self.stats={stat_name:int(stat_value.find("td").text[:-1]) for stat_name,stat_value in tuple(zip(stats_names,stats_table))}
    def data(self):
        return {
                "dex number":self.num,
                "pokemon name":self.name,
                "types":self.types,
                "abilities":self.abilities,
                "hidden abilities":self.hidden,
                "stats":self.stats,
                "location":self.location_info,
                "pokedex":self.pkdex_info
                }
class Scrapping():
    def __init__(self,list):
        for pokemon_data in list:
            pkmn=Pokemon(pokemon_data)
            #self.save_image(pkmn.num,pkmn.name)
            #self.save_json(Pokemon)
            #self.print_json(pkmn)
    def print_json(self,Pokemon):
        pprint(Pokemon.data())
    def save_json(self,pokemon):
        print(f"saving {pokemon.name}...")
        with open(f"{BASE_DIR}\\json_files\\{pokemon.num}-{pokemon.name}.json","w",encoding="utf-8") as f:
            f.write(json.dumps(pokemon.data(),indent=4,ensure_ascii=False))
            f.close()
        print(f"{pokemon.name} saved!")
    def save_image(self,dexnum,pkmnname):
        dexnum=dexnum[1::] if dexnum[0]=="0" else dexnum
        content=r.get(f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/{dexnum}.png").content
        with open(f"{BASE_DIR}\\Portraits\\{dexnum}-{pkmnname}.png","wb") as img:
            img.write(content)
            img.close()
if __name__=="__main__":
    #gen 1 ok
    #gen 2 
    #gen 3 
    #gen 4 
    #gen 5 
    #gen 6 
    #gen 7 
    #gen 8 
    #gen 9 NOT WORKING
    
    Scrapping(PokemonList(1).PokemonList)
    #debug=PokemonList(8).PokemonList[5]
    #pprint(Pokemon(debug).data())