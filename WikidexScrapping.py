#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests as r
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import bs4
from bs4 import BeautifulSoup as bs
from pprint import pprint
import json
from os import getcwd,path
r.packages.urllib3.disable_warnings(InsecureRequestWarning) 

VALID_TITLES=[
    'RojoAzul', 
    'Amarillo', 
    'Oro', 
    'Plata', 
    'Cristal', 
    'Rubí', 
    'Zafiro', 
    'Esmeralda', 
    'Rojo Fuego', 
    'Verde Hoja', 
    'Diamante', 
    'Perla', 
    'Platino', 
    'Oro HeartGold', 
    'Plata SoulSilver', 
    'Negro', 
    'Blanco', 
    'Negro 2', 
    'Blanco 2', 
    'Pokémon X', 
    'Pokémon Y', 
    'Rubí Omega', 
    'Zafiro Alfa', 
    'Sol', 
    'Luna', 
    'Ultrasol', 
    'Ultraluna', 
    "Let's Go Pikachu!Let's Go Eevee!", 
    'Espada', 
    'Escudo', 
    'Diamante Brillante', 
    'Perla Reluciente', 
    'Leyendas: Arceus'
    ]
#Excepted_pokemon are pokemon that their pages act differently to the standard therefore need special treatment
EXCEPTED_POKEMON=["Mew","Typhlosion","Deoxys"]
#Special_case are pokemon that have special characteristics that their tables are in a different position
SPECIAL_CASE={"Ditto":3,"Cinderace":2,"Inteleon":2,"Sinistea":2,"Milcery":2}
BASE_URL="https://www.wikidex.net/"
BASE_DIR=getcwd()
class RequestQuery():
    def __init__(self,url:str):
        url_request=r.get(url,verify=False).text
        self.parsed_request=bs(url_request,"html.parser")
    def table_query(self,name:str)->bs4.element.ResultSet:
        return self.parsed_request.find_all("table",{"class": name})
    @staticmethod
    def tr_query(table,subquery,subtag):
        query=table.find("tr",{"title":subquery})
        return query.find_all(subtag) 
    @staticmethod
    def to_matrix(table):
        row=table.find_all("tr")
        depure=lambda list:[i.replace("\n","") for i in list if i!="\n"]
        return [depure([i.text for i in j]) for j in row]
class PokemonList():
    url=f"{BASE_URL}/wiki/Lista_de_Pok%C3%A9mon"
    def __init__(self,gen_num:int):
        request=RequestQuery(self.url)
        table=request.table_query("tabpokemon")[gen_num-1]
        self.PokemonList=self.table_unwrapper(table)
        self.AltPokemonList=self.alternative_forms(table)
    def table_unwrapper(self,table)->list:
        return [
            {
                "num":i.find_all("td")[0].text[:-1],
                "name":i.find_all("td")[1].text[:-1],
                "url":i.find_all("td")[1].a['href']
            } 
                for i in table.find_all("tr")[1::] 
                    if i.find_all("td")[0].text[:-1].isnumeric()
                ] 
    def alternative_forms(self,table)->list:
        return [
            {
                "name":i.find_all("td")[0].text[:-1],
                "url":i.find_all("td")[0].a['href']
            } 
                for i in table.find_all("tr")[1::] 
                    if not i.find_all("td")[0].text[:-1].isnumeric()
                ] 
class Pokemon():
    def __init__(self,data:dict):
        self.name=data["name"]
        self.num=data["num"]
        #Revisit this later, it can be improve upon
        self.request=RequestQuery(f'{BASE_URL}{data["url"]}')
        self.other_data=self.request.table_query("datos")[0].find("tbody")
        types=RequestQuery.tr_query(self.other_data,"Tipos a los que pertenece","a")[1::]
        self.types=[a["title"].split(" ")[-1] for a in types if a.has_attr("title")] 
        abilities=RequestQuery.tr_query(self.other_data,"Habilidades que puede conocer","a")[1::]
        self.abilities=[i.text for i in abilities if i.has_attr("title")]
        try:
            hidden=RequestQuery.tr_query(self.other_data,"Habilidad oculta","a")[1::]
            self.hidden=[i.text for i in hidden if i.has_attr("title")]
        except AttributeError:
            self.hidden=None
        self.weight=float(self.__clean_float(RequestQuery.tr_query(self.other_data,"Peso del Pokémon","td")[0].text))
        self.height=float(self.__clean_float(RequestQuery.tr_query(self.other_data,"Altura del Pokémon","td")[0].text))
        self.Pokedex()
        self.Location()
        self.Stats_debug()
        self.evolve_to()
    def __clean_float(self,string):
        return string.split(" ")[0].replace(",",".")
    def __evolve_to(self,evo,pivot):
        if self.name=="Silcoon":
            self.evo_stage=2
            return ['Beautifly']
        elif self.name=="Cascoon":
            self.evo_stage=2
            return ["Dustox"]
        elif self.evo_stage<len(evo[0][0::2]):
            return [i[::-2][::-1][pivot] for i in evo if len(i[::-2][::-1])*-1<=pivot]
        else:
            return None
    def Pokedex(self)->None:
        pkdex_table=self.request.table_query("pokedex")[0].find_all("tr")
        self.pkdex_info={game.find_all("th")[1].text[:-1]:game.find_all("td")[0].text[:-1] for game in pkdex_table[1::] if len(game.find_all("th")) and game.find_all("th")[1].text[:-1] in VALID_TITLES}
    def Location(self)->None:
        location_table=self.request.table_query("localizacion")[0].find_all("tr")
        location_info={}
        for game in location_table[1::]:
            row=[row_content for row_content in game.text.split("\n") if row_content!=""]
            if row[0] in VALID_TITLES: location_info[row[0]]=row[1::]
        self.location_info=location_info
    def Stats_debug(self)->None:
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
    def Stats(self)->None:
        stats_table=self.request.table_query("tabpokemon")
        index=0
        if(self.name in SPECIAL_CASE.keys()): index=SPECIAL_CASE[self.name]
        elif (self.name in EXCEPTED_POKEMON or stats_table[0].has_attr("style")): index=1
        stats_table=stats_table[index].find_all("tr")[1:7]
        stats_names=["hp","atk","def","atk esp","def esp", "speed"]
        self.stats={stat_name:int(stat_value.find("td").text[:-1]) for stat_name,stat_value in tuple(zip(stats_names,stats_table))}
    def evolve_to(self):
        evo=self.request.table_query("evolucion")
        evo=RequestQuery.to_matrix(evo[-1]) if len(evo)>1 else RequestQuery.to_matrix(evo[0]) 
        #shift is the gap between the stage number (natural number between 1) 
        shift=1
        for i in evo:
            try:
                evo_stage=i[::-2][::-1].index(self.name)
                break
            except ValueError:
                #in cases where there's a fork the pokemon name will appear in other part of the list rather the first
                #element so the gap is greater
                shift=len(evo[0][::-2][::-1])
                pass
        evo_line_len=len(evo[0][0::2])
        self.evo_stage=evo_stage+shift
        if self.name=="Dustox":
            self.evo_stage=3
        self.evolution=self.__evolve_to(evo,self.evo_stage-evo_line_len)
        print(f"pokemon: {self.name} evo_stage: {self.evo_stage} evolve to:{self.evolution}")
    
    def data(self)->dict:
        return {
                "dex number":self.num,
                "pokemon name":self.name,
                "types":self.types,
                "abilities":self.abilities,
                "hidden abilities":self.hidden,
                "stats":self.stats,
                "location":self.location_info,
                "pokedex":self.pkdex_info,
                "evolution stage":self.evo_stage,
                "evolve to":self.evolution,
                "Height":self.height,
                "Weight":self.weight
                }
class Scrapping():
    def __init__(self,list:list,save_images=False,save=True,print=False):
        for pokemon_data in list:
            pkmn=Pokemon(pokemon_data)
            if save_images: self.save_image(pkmn.num,pkmn.name)
            if save: self.save_json(pkmn)
            if print: pprint(pkmn.data())
    def save_json(self,pokemon):
        print(f"saving {pokemon.name}...")
        with open(f"{BASE_DIR}\\json_files\\Español\\{pokemon.num}-{pokemon.name}.json","w",encoding="utf-8") as f:
            f.write(json.dumps(pokemon.data(),indent=4,ensure_ascii=False))
            f.close()
        print(f"{pokemon.name} saved!")
    def save_image(self,dexnum,pkmnname):
        dexnum=dexnum[1::] if dexnum[0]=="0" else dexnum
        content=r.get(f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/{dexnum}.png").content
        with open(f"{BASE_DIR}\\Portraits\\{dexnum}-{pkmnname}.png","wb") as img:
            img.write(content)
            img.close()
    @staticmethod
    def debug(pokemon_data)->None:
        #Checks just one pokemon instead of a list
        Pokemon(pokemon_data)
if __name__=="__main__":
    #gen 1 ok
    #gen 2 ok
    #gen 3 ok
    #gen 4 ok
    #gen 5 ok
    #gen 6 ok
    #gen 7 ok
    #gen 8 ok
    #gen 9 ok It behaves weird, must find the answer
    #print(PokemonList(1).PokemonList[132:133])
    Scrapping(PokemonList(1).PokemonList,save=False)
    #pkmn={'num': '0133', 'name': 'Eevee', 'url': '/wiki/Eevee'}
    #pkmn={'num': '0025', 'name': 'Pikachu', 'url': '/wiki/Pikachu'}
    #pkmn={'num': '0043', 'name': 'Oddish', 'url': '/wiki/Oddish'}
    #pkmn={'num': '0107', 'name': 'Hitmonchan', 'url': '/wiki/Hitmonchan'}
    #pkmn={'num': '0182', 'name': 'Bellossom', 'url': '/wiki/Bellossom'}
    #pkmn={'num': '0251', 'name': 'Celebi', 'url': '/wiki/Celebi'}
    #debug=Scrapping.debug(pkmn)
    #pprint(Pokemon(debug).data())