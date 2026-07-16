// Lane cost calculator
let calcDistances={};
let calcDiesel=0;

fetch('data/distances.json').then(r=>r.json()).then(d=>{
  calcDistances=d.distances;
  d.cities.forEach(c=>{
    var o=document.createElement('option');
    o.value=c.code;o.textContent=c.name;
    document.getElementById('cf').appendChild(o.cloneNode(true));
    document.getElementById('ct').appendChild(o.cloneNode(true));
  });
});

fetch('data/fuel.json').then(r=>r.json()).then(d=>{
  calcDiesel=d.national_avg||3.83;
});

function runCalc(){
  var f=document.getElementById('cf').value;
  var t=document.getElementById('ct').value;
  var m=parseFloat(document.getElementById('cmpg').value)||6;
  var r=document.getElementById('cr');
  var e=document.getElementById('ce');
  
  if(!f||!t||f===t){
    r.className='cresult';e.style.display='block';return;
  }
  
  var d=calcDistances[f+'-'+t]||calcDistances[t+'-'+f];
  if(!d){
    r.className='cresult';e.style.display='block';
    e.textContent='Route not available for this lane yet.';
    return;
  }
  
  var g=d/m;
  var tot=g*calcDiesel;
  
  document.getElementById('cv').textContent='$'+tot.toFixed(0);
  document.getElementById('cd').innerHTML='<strong>'+f+'</strong> &rarr; <strong>'+t+'</strong><br>'+d.toLocaleString()+' mi &middot; '+m+' MPG &middot; '+g.toFixed(1)+' gal &middot; $'+calcDiesel.toFixed(2)+'/gal';
  
  r.className='cresult v';e.style.display='none';
}
