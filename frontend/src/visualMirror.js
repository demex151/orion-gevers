const SUBTITLE_ID='gever-live-subtitles';

function ensureSubtitleBox(home){
 let box=document.getElementById(SUBTITLE_ID);if(box)return box;
 box=document.createElement('div');box.id=SUBTITLE_ID;
 Object.assign(box.style,{position:'absolute',zIndex:'8',left:'50%',top:'72%',transform:'translateX(-50%)',width:'790px',minHeight:'38px',display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',color:'#f5f9ff',fontSize:'14px',lineHeight:'1.45',fontWeight:'500',textShadow:'0 0 16px rgba(97,232,255,.35)',pointerEvents:'none',transition:'opacity .2s ease'});
 home.appendChild(box);return box;
}
function readLegacySubtitles(){
 const core=document.querySelector('.legacy-app .core-content');if(!core)return '';
 const candidates=[...core.querySelectorAll('div')].filter(el=>{const style=el.getAttribute('style')||'';return style.includes('min-height: 64px')||style.includes('min-height:64px')});
 const target=candidates[0];if(!target)return '';
 return [...target.children].map(el=>el.textContent?.trim()).filter(Boolean).slice(-2).join(' ');
}
function readRuntimeState(subtitle){
 const legacy=document.querySelector('.legacy-app');
 const text=(legacy?.textContent||'').toUpperCase();
 if(subtitle)return 'speaking';
 if(text.includes('HABLANDO'))return 'speaking';
 if(text.includes('ESCUCHANDO'))return 'listening';
 if(text.includes('PENSANDO')||text.includes('PREPARANDO_VOZ'))return 'thinking';
 if(text.includes('EJECUTANDO'))return 'working';
 return 'idle';
}
function applyOrbState(home,state){
 const orb=home.querySelector('.figma-orb-visualizer');if(!orb)return;
 for(const name of ['idle','listening','thinking','speaking','working'])orb.classList.remove(`is-${name}`);
 orb.classList.add(`is-${state}`);orb.dataset.geverState=state;
}
function sync(){
 const home=document.querySelector('.figma-home');if(!home)return;
 const subtitle=readLegacySubtitles();
 const subtitleBox=ensureSubtitleBox(home);subtitleBox.textContent=subtitle;subtitleBox.style.opacity=subtitle?'1':'0';
 applyOrbState(home,readRuntimeState(subtitle));
}
if(typeof window!=='undefined'){window.setInterval(sync,120);window.addEventListener('DOMContentLoaded',sync)}
