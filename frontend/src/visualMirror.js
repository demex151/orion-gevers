const SUBTITLE_ID = 'gever-live-subtitles';
const CHAT_ID = 'gever-chat-overlay';

function ensureSubtitleBox(home) {
  let box = document.getElementById(SUBTITLE_ID);
  if (box) return box;
  box = document.createElement('div');
  box.id = SUBTITLE_ID;
  Object.assign(box.style, {
    position:'absolute', zIndex:'8', left:'560px', top:'490px', width:'790px', minHeight:'38px',
    display:'flex', alignItems:'center', justifyContent:'center', textAlign:'center',
    color:'#f5f9ff', fontSize:'14px', lineHeight:'1.45', fontWeight:'500',
    textShadow:'0 0 16px rgba(97,232,255,.35)', pointerEvents:'none'
  });
  home.appendChild(box);
  return box;
}

function readLegacySubtitles() {
  const core = document.querySelector('.legacy-app .core-content');
  if (!core) return '';
  const candidates = [...core.querySelectorAll('div')].filter(el => {
    const style = el.getAttribute('style') || '';
    return style.includes('min-height: 64px') || style.includes('min-height:64px');
  });
  const target = candidates[0];
  if (!target) return '';
  return [...target.children].map(el => el.textContent?.trim()).filter(Boolean).slice(-2).join(' ');
}

function readMessages() {
  return [...document.querySelectorAll('.legacy-app .gever-message')].map(el => {
    const sender = el.querySelector('span')?.textContent?.trim() || '';
    const text = el.querySelector('p')?.textContent?.trim() || '';
    return { sender, text };
  }).filter(item => item.text);
}

function ensureChat(home) {
  let panel = document.getElementById(CHAT_ID);
  if (panel) return panel;
  panel = document.createElement('section');
  panel.id = CHAT_ID;
  Object.assign(panel.style, {
    position:'absolute', zIndex:'20', left:'535px', top:'115px', width:'850px', height:'820px',
    padding:'24px', border:'1px solid #163452', borderRadius:'18px',
    background:'rgba(3,10,22,.94)', backdropFilter:'blur(18px)', display:'none', overflow:'hidden'
  });
  panel.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px"><div><b style="font-size:20px">Conversaciones</b><div style="font-size:11px;color:#61e8ff;margin-top:4px">GEVER · conversación en tiempo real</div></div><button data-close-chat style="border:1px solid #163452;background:#091629;color:#f5f9ff;border-radius:10px;padding:8px 12px;cursor:pointer">Cerrar</button></div><div data-chat-list style="height:735px;overflow:auto;padding-right:8px"></div>`;
  panel.querySelector('[data-close-chat]').addEventListener('click', () => panel.style.display='none');
  home.appendChild(panel);
  return panel;
}

function renderMessages(panel, messages) {
  const list = panel.querySelector('[data-chat-list]');
  if (!list) return;
  const signature = JSON.stringify(messages);
  if (list.dataset.signature === signature) return;
  list.dataset.signature = signature;
  list.innerHTML = messages.map(item => `<div style="margin:0 0 14px;padding:14px 16px;border:1px solid #12233f;border-radius:14px;background:rgba(9,22,41,.78)"><b style="display:block;color:${item.sender==='GEVER'?'#61e8ff':'#f5f9ff'};font-size:11px;margin-bottom:6px">${escapeHtml(item.sender)}</b><div style="color:#c9d4e6;font-size:13px;line-height:1.5">${escapeHtml(item.text)}</div></div>`).join('');
  list.scrollTop = list.scrollHeight;
}

function escapeHtml(value='') { const div=document.createElement('div'); div.textContent=value; return div.innerHTML; }

function bindConversationButton(home, panel) {
  const button = [...home.querySelectorAll('.figma-nav button')].find(el => el.textContent?.includes('Conversaciones'));
  if (!button || button.dataset.visualBound) return;
  button.dataset.visualBound='1';
  button.addEventListener('click', () => { panel.style.display='block'; });
}

function sync() {
  const home = document.querySelector('.figma-home');
  if (!home) return;
  const subtitleBox = ensureSubtitleBox(home);
  const subtitle = readLegacySubtitles();
  subtitleBox.textContent = subtitle;
  subtitleBox.style.opacity = subtitle ? '1' : '0';
  const panel = ensureChat(home);
  bindConversationButton(home, panel);
  renderMessages(panel, readMessages());
}

if (typeof window !== 'undefined') {
  window.setInterval(sync, 180);
  window.addEventListener('DOMContentLoaded', sync);
}
