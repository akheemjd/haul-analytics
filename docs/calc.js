// Lane cost calculator
let calcDistances={};
let calcDiesel=0;

fetch('data/distances.json').then(r=>r.json()).then(d=>{
  calcDistances=d.distances;
  const cities=d.cities;
  ['calc-from','calc-to'].forEach(id=>{
    const sel=document.getElementById(id);
    cities.forEach(c=>{
      const opt=document.createElement('option');
      opt.value=c.code;opt.textContent=c.name;
      sel.appendChild(opt);
    });
  });
});

fetch('data/fuel.json').then(r=>r.json()).then(d=>{
  calcDiesel=d.national_avg||3.83;
});

function runCalc(){
  const from=document.getElementById('calc-from').value;
  const to=document.getElementById('calc-to').value;
  const mpg=parseFloat(document.getElementById('calc-mpg').value)||6;
  const result=document.getElementById('calc-result');
  const empty=document.getElementById('calc-empty');
  const cost=document.getElementById('calc-cost');
  const detail=document.getElementById('calc-detail');
  
  if(!from||!to||from===to){
    result.style.display='none';empty.style.display='block';return;
  }
  
  const dist=calcDistances[from+'-'+to]||calcDistances[to+'-'+from];
  if(!dist){
    result.style.display='none';empty.style.display='block';
    empty.textContent='Route data not available for this lane yet.';
    return;
  }
  
  const gallons=dist/mpg;
  const total=gallons*calcDiesel;
  
  cost.textContent='$'+total.toFixed(0);
  detail.innerHTML='<strong>'+from+'</strong> → <strong>'+to+'</strong><br>'+dist.toLocaleString()+' miles &middot; '+mpg+' MPG &middot; '+gallons.toFixed(1)+' gal &middot; $'+calcDiesel.toFixed(2)+'/gal diesel';
  
  result.style.display='block';empty.style.display='none';
}
