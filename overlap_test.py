# Overlap test: caller panel (Mama, ball, speech bubble), recent balls, pattern + hall chips, 1-4 cards (incl. glow margin),
# power-up meter & buttons, bottom buttons, DOM buttons and modals - sampled over full games in every room at 4 phone sizes.
import sys,asyncio,json
from playwright.async_api import async_playwright
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8800/mama-macgregors-bingo-hall/'
VIEWS=[(390,844,None),(375,667,None),(430,932,None),(390,844,{'t':47,'b':34})]
JS=r'''async ([rid,n])=>{const T=__T;T.setSave({lvl:20,coins:1e6,ncards:n,auto:Math.random()<.6,speed:3,voice:false});T.setRoom(rid);T.startGame();const ov=(a,b)=>a.x<b.x+b.w-.01&&b.x<a.x+a.w-.01&&a.y<b.y+b.h-.01&&b.y<a.y+a.h-.01;
 const btns=()=>{const L=T.layout();return[...document.querySelectorAll('.tb')].filter(e=>getComputedStyle(e).display!='none').map(e=>{const b=e.getBoundingClientRect();return{k:'dom-'+e.id,x:(b.left-L.OXs)/L.SC,y:(b.top-L.OYs)/L.SC,w:b.width/L.SC,h:b.height/L.SC}})};
 let frames=0,games=0;const bad=[];const check=()=>{frames++;const L=T.layout(),E=L.els.concat(btns());const vis={x0:Math.max(0,(L.SAFE.l-L.OXs)/L.SC),y0:Math.max(0,(L.SAFE.t-L.OYs)/L.SC),x1:Math.min(400,(L.VW-L.SAFE.r-L.OXs)/L.SC),y1:Math.min(720,(L.VH-L.SAFE.b-L.OYs)/L.SC)};
  for(let i=0;i<E.length;i++){for(let j=i+1;j<E.length;j++)if(ov(E[i],E[j]))bad.push([E[i].k,E[j].k]);const e=E[i];if(!e.k.startsWith('dom')&&(e.x<vis.x0-.01||e.y<vis.y0-.01||e.x+e.w>vis.x1+.01||e.y+e.h>vis.y1+.01))bad.push(['edge',e.k])}
  if(L.modal){const m=L.modal;if(m.x<vis.x0||m.y<vis.y0||m.x+m.w>vis.x1||m.y+m.h>vis.y1)bad.push(['modal-edge']);for(const b of btns())if(ov(m,b))bad.push(['modal-dom',b.k])}};
 for(let gI=0;gI<3;gI++){if(gI){T.setSave({ncards:n});T.startGame()}games++;let k=0;
  while(k<4000){k++;T.update(1/10);if(k%3==0)check();const g=T.get();if(!g.G||g.G.over)break;
   if(Math.random()<.02){const p=['hoof','lamb','dove','donkey'][Math.floor(Math.random()*4)];T.setSave({pow:{hoof:3,lamb:3,dove:3,donkey:3}});T.usePow(p);if(p=='lamb')T.daub(0,Math.floor(Math.random()*5),Math.floor(Math.random()*5))}
   if(!T.save().auto&&Math.random()<.3){const cs=T.cards();cs.forEach((c,i)=>{for(let r=0;r<5;r++)for(let q=0;q<5;q++)T.daub(i,r,q)})}
   if(g.G.need.some(x=>x==0)&&Math.random()<.15)T.claim()}
  for(let j=0;j<30;j++){T.update(1/10);check()}while(T.get().modal){T.closeModal();T.update(.1);check()}}
 return{rid,n,games,frames,overlaps:bad.length,sample:bad.slice(0,4)}}'''
async def main():
  tot=0;fr=0
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for (w,h,safe) in VIEWS:
      pg=await b.new_page(viewport={'width':w,'height':h},is_mobile=True,has_touch=True);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
      if safe:await pg.add_init_script('window.__SAFE='+json.dumps(safe))
      await pg.goto(URL);await pg.wait_for_timeout(600)
      for rid,n in [('kirk',1),('barn',2),('donkey',3),('lamb',4),('cathedral',4),('kirk',2)]:
        r=await pg.evaluate(JS,[rid,n]);tot+=r['overlaps'];fr+=r['frames'];print(f"{w}x{h}{' safe' if safe else ''} {rid:9} {n} cards: games {r['games']} frames {r['frames']} overlaps {r['overlaps']}",r['sample'] if r['overlaps'] else '')
      if errs:print('PAGE ERRORS',errs);tot+=len(errs)
      await pg.close()
    await b.close()
  print(f'TOTAL frames {fr} overlaps {tot}');sys.exit(1 if tot else 0)
asyncio.run(main())
