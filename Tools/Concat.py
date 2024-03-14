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
@open_file
def concat(*args)->None:
    gen_num=args[0][0]
    f=args[1]
    current_path=path.format(gen=gen[gen_num-1])
    files=[file for file in listdir(current_path) if ".json" in file]
    append_pokemon(f,files,current_path)       
def append_pokemon(f, files:list,current_path:str)->None:
    for i in files:
        with open(f"{current_path}\\{i}","r",encoding='utf-8') as pkmn:
            f.write(pkmn.read())
            f.write(",\n")
if __name__=="__main__":
    concat(2)