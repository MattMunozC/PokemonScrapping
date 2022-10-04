import {pkdex} from './pokemon_info.js'

var displayer=document.getElementById("pkmnimg");

var selector=document.getElementById("pkmnname");
pkdex.forEach(function(pokemon,i){
    selector.innerHTML+=`
    <option value=${i}>${pokemon['pokemon name']}</option>
    `
})

var hp=document.getElementById("hp_ev");
var atk=document.getElementById("atk_ev");
var def=document.getElementById("def_ev");
var espatk=document.getElementById("atkesp_ev")
var espdef=document.getElementById("defesp_ev")
var spd=document.getElementById("spd_ev")
hp.addEventListener('input',()=>{
    document.getElementById("hp_ev_label").innerText=hp.value;
})
atk.addEventListener('input',()=>{
    document.getElementById("atk_ev_label").innerText=atk.value;
})
def.addEventListener('input',()=>{
    document.getElementById("def_ev_label").innerText=def.value;
})
espatk.addEventListener('input',()=>{
    document.getElementById("atkesp_ev_label").innerText=espatk.value;
})
espdef.addEventListener('input',()=>{
    document.getElementById("defesp_ev_label").innerText=espdef.value;
})
spd.addEventListener('input',()=>{
    document.getElementById("spd_ev_label").innerText=spd.value;
})

selector.addEventListener('change',function(){
    displayer.src=`https://assets.pokemon.com/assets/cms2/img/pokedex/full/${pkdex[selector.value]['dex number']}.png`;
})

displayer.src=`https://assets.pokemon.com/assets/cms2/img/pokedex/full/${pkdex[selector.value]['dex number']}.png`;
console.log()

