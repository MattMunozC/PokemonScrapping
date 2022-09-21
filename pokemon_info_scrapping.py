
import requests as r
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup as bs
from pprint import pprint
r.packages.urllib3.disable_warnings(InsecureRequestWarning) 
#usable_tables=[2,4,6,8,10,12,14,16]
def list_pkmn():
    url="https://www.wikidex.net/wiki/Lista_de_Pok%C3%A9mon"
    url_html=r.get(url,verify=False).text
    url_html=bs(url_html,"html.parser")
    return url_html.find_all("table",{"class": "tabpokemon"})
def table_unwrapper(table):
    return [{"num":i.find_all("td")[0].text[:-1],"name":i.find_all("td")[1].text[:-1],"url":i.find_all("td")[1].a['href']} for i in table.find_all("tr")[1::]] 

def first_gen(list):
    for i in list:
        #info dumb
        info=i["url"]
        dexnum=i["num"]
        pkmnname=i["name"]

        url=r.get("https://www.wikidex.net/"+info,verify=False)

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
            hidden=None


        pkdex_info=Pokedex(url_html)
        location_info=Location(url_html)

        stats=Stats(url_html,pkmnname)
        try:
            evo=evolution(url_html,pkmnname,evo)
        except:
            evo=evolution(url_html,pkmnname)
        #level_moves=url_html.find_all("section",{"class":"tabber__section"})[0]

        MO_MT=[i.text for i in url_html.find_all("section",{"class":"tabber__section"})[1].find_all("tr")]
        pprint(MO_MT)
        break
        #save_json(pkmnname,dexnum,types,abilities,hidden,stats,location_info,pkdex_info,evo)

        #pprint({"dex number":dexnum,"pokemon name":pkmnname,"types":types,"abilities":abilities,"hidden abilities":hidden,"stats":{"hp":stats[0],"atk":stats[1],"def":stats[2],"atk esp":stats[3],"def esp":stats[4],"speed":stats[5]},"location":location_info,"pokedex":pkdex_info,"evolution":evo})


def save_json(pkmnname,dexnum,types,abilities,hidden,stats,location_info,pkdex_info,evo):
    with open(f"{pkmnname}.json","w") as f:
        f.write(str({"dex number":dexnum,"pokemon name":pkmnname,"types":types,"abilities":abilities,"hidden abilities":hidden,"stats":{"hp":stats[0],"atk":stats[1],"def":stats[2],"atk esp":stats[3],"def esp":stats[4],"speed":stats[5]},"location":location_info,"pokedex":pkdex_info,"evolution":evo}).replace("Let'","let").replace("'",'"'))
        f.close()
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
        if pkmnname=="Mew":
            raw_stats=raw_stats[1]
        else:
            raw_stats=raw_stats[0]
    return [raw_stats.find_all("tr")[i].find_all("td")[0].text.replace("\n","") for i in range(1,7)]

def Pokedex(url_html):
    pkdex_table=url_html.find_all("table",{"class":"pokedex"})[0].find_all("tr")    
    pkdex_info={}
    for i in pkdex_table[1::]:
        th=i.find_all("th")
        if len(th)==2:
            region=th[1].text[:-1]
            pkdex_info[region]=i.find_all("td")[0].text[:-1]
    return pkdex_info

def Location(url_html):
    location_table=url_html.find_all("table",{"class":"localizacion"})[0].find_all("tr")
    location_info={}
    for i in location_table[1::]:
        th=i.find_all("th")
        if len(th)==2:
            region=th[1].text[:-1]
            location_info[region]=i.find_all("td")[0].text[:-1].split("\n")[1::]
    return location_info

def evolution(url_html,pkmname,previous=None):
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
#url_html=bs(url.text,"html.parser").find_all("table")[2] Evolucion
if __name__=="__main__":
    gen=[table_unwrapper(i) for i in list_pkmn()]
    first_gen(gen[0])