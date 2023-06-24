import {pkdex} from './pokemon_info.js'

var displayer=document.getElementById("pkmnimg");
var selector=document.getElementById("pkmnname");
pkdex.forEach(function(pokemon,i){
    selector.innerHTML+=`
    <option value=${i}>${pokemon['pokemon name']}</option>
    `
})
function getTotal(exception=undefined){
    let sum=0
    for (const key in stats) {
        if (stats.hasOwnProperty(key) && key!=exception) {
            sum+=parseInt(stats[key].value);
        }
    }  
    return sum;
}
function statistics_formula(EV,level,Nature,Base,IV){
    return ((Math.floor(0.01*(2* Base+IV+Math.floor(0.25*EV))*level) + 5)*Nature)
}
function hp_formula(EV,level,Base,IV){
    return Math.floor(0.01*(2*Base+IV+Math.floor(0.25*EV))*level)+level+10
}
function max_reached(key){
    if(getTotal()>MAX_VALUE){
        stats[key].value=MAX_VALUE-getTotal(key)
    }
    document.getElementById(`${key}_ev_label`).innerText=stats[key].value;
}
var stats={
    hp:document.getElementById("hp_ev"),
    atk:document.getElementById("atk_ev"),
    def:document.getElementById("def_ev"),
    atkesp:document.getElementById("atkesp_ev"),
    defesp:document.getElementById("defesp_ev"),
    spd:document.getElementById("spd_ev")
}
const MAX_VALUE=512;
for (const key in stats) {
    if (stats.hasOwnProperty(key)) {
        document.getElementById(`${key}_ev_label`).innerText=stats[key].value;
        if(key!="hp"){
            stats[key].addEventListener('input',()=>{
                max_reached(key)
                console.log(statistics_formula(stats[key].value,100,1,parseInt(pkdex[selector.value].stats[key]),31))
            })
        }else{
            stats[key].addEventListener('input',()=>{
                max_reached(key)
                console.log(hp_formula(stats[key].value,100,parseInt(pkdex[selector.value].stats[key]),31))
            })
        }

    }
  }
selector.addEventListener('change',function(){
    displayer.src=`https://assets.pokemon.com/assets/cms2/img/pokedex/full/${pkdex[selector.value]['dex number']}.png`;
})

displayer.src=`https://assets.pokemon.com/assets/cms2/img/pokedex/full/${pkdex[selector.value]['dex number']}.png`;
