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
      stats[key].addEventListener('input',()=>{
        if(getTotal()>MAX_VALUE){
            stats[key].value=MAX_VALUE-getTotal(key)
        }
        document.getElementById(`${key}_ev_label`).innerText=stats[key].value;
      })
    }
  }
selector.addEventListener('change',function(){
    displayer.src=`https://assets.pokemon.com/assets/cms2/img/pokedex/full/${pkdex[selector.value]['dex number']}.png`;
})

displayer.src=`https://assets.pokemon.com/assets/cms2/img/pokedex/full/${pkdex[selector.value]['dex number']}.png`;

