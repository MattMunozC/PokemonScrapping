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
SPECIAL_CASE={"Ditto":3,"Cinderace":2,"Inteleon":2,"Sinistea":2,"Milcery":2}
BASE_URL="https://www.wikidex.net/"
BASE_DIR=getcwd()
class RequestQuery():
    def __init__(self,url):
        url_request=r.get(url,verify=False).text
        self.parsed_request=bs(url_request,"html.parser")
    def table_query(self,name):
        return self.parsed_request.find_all("table",{"class": name})
    def tr_query(self,subquery):
        return self.parsed_request.find_all("tr",{"title":subquery})[0].find_all("a")[1::]
class PokemonList():
    url=f"{BASE_URL}/wiki/Lista_de_Pok%C3%A9mon"
    def __init__(self,gen_num):
        request=RequestQuery(self.url)
        table=request.table_query("tabpokemon")[gen_num-1]
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
        self.request=RequestQuery(f'{BASE_URL}{data["url"]}')
        self.raw_data=self.request.table_query("datos")
        self.types=[type['title'][4::] for type in self.request.tr_query("Tipos a los que pertenece") if type.has_attr("title")]
        self.abilities=[ability['title'].replace("Tipo ","") for ability in self.request.tr_query("Habilidades que puede conocer") if ability.has_attr("title")]
        try:
            self.hidden=[i['title'] for i in self.request.tr_query("Habilidad oculta") if i.has_attr("title")]
        except IndexError:
            self.hidden="None"
        self.Pokedex()
        self.Location()
        self.Stats_debug()
    def Pokedex(self):
        pkdex_table=self.request.table_query("pokedex")[0].find_all("tr")
        self.pkdex_info={game.find_all("th")[1].text[:-1]:game.find_all("td")[0].text[:-1] for game in pkdex_table[1::] if len(game.find_all("th")) and game.find_all("th")[1].text[:-1] in VALID_TITLES}
    def Location(self):
        location_table=self.request.table_query("localizacion")[0].find_all("tr")
        location_info={}
        for game in location_table[1::]:
            row=[row_content for row_content in game.text.split("\n") if row_content!=""]
            if row[0] in VALID_TITLES: location_info[row[0]]=row[1::]
        self.location_info=location_info
    def Stats_debug(self):
        index=0
        while (1):
            try:
                stats_table=self.request.table_query("tabpokemon")
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
        stats_table=self.request.table_query("tabpokemon")
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
            #pprint(pkmn.data())
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
    #gen 2 ok
    #gen 3 ok
    #gen 4 ok
    #gen 5 ok
    #gen 6 ok
    #gen 7 ok
    #gen 8 ok
    #gen 9 NOT WORKING

    Scrapping(PokemonList(9).PokemonList)
    #debug=PokemonList(3).PokemonList[-3]
    #pprint(Pokemon(debug).data())