from os import listdir
#Simple concatenation of all pokemon in a generation
#the output will be a js array with every pokemon from a generation
gen=["1ra","2da","3ra","4ta","5ta","6ta","7ma","8va","9na"]
path="..\\json_files\\Español\\{gen} Generacion"
def open_file(func):
    def new_func(*args):
        with open("pokemon_info.js","w",encoding='utf-8') as f:
            f.write("export var pkdex=[\n")
            func(args,f)
            f.write("]")
    return new_func
def __concat(gen_num,f)->None: 
    current_path=path.format(gen=gen[gen_num-1])
    files=[file for file in listdir(current_path) if ".json" in file]
    __append(f,files,current_path)       
@open_file
def concat(*args):
    __concat(args[0][0],args[1])
def concat_all(*args):
    __concat(args[0][0],args[1])
def __append(f, files:list,current_path:str)->None:
    for i in files:
        with open(f"{current_path}\\{i}","r",encoding='utf-8') as pkmn:
            f.write(pkmn.read())
            f.write(",\n")
