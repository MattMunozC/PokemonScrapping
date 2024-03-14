from os import listdir
#Simple concatenation of all pokemon in a generation
#the output will be a js array with every pokemon from a generation
gen=["1ra","2da","3ra","4ta","5ta","6ta","7ma","8va","9na"]
path=f"..\\json_files\\Español\\{gen[0]} Generacion"
files=[file for file in listdir(path) if ".json" in file]
with open("pokemon_info.js","w",encoding='utf-8') as f:
    f.write("export var pkdex=[\n")
    for i in files:
        with open(f"{path}\\{i}","r",encoding='utf-8') as pkmn:
            f.write(pkmn.read())
            f.write(",\n")
    f.write("]")
