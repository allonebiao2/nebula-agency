'use strict';

// Add render deps before any require calls
process.env.NODE_PATH = (process.env.NODE_PATH || '') + ':/tmp/nebula-render/node_modules';
require('module').Module._initPaths();

const fs   = require('fs');
const path = require('path');
const {spawn} = require('child_process');

const TOPICS_FILE = path.join(__dirname, 'topics.json');
const LOGO_FILE   = '/home/user/nebula-agency/00-nebula-agency/logo-nebula-agency.jpg';
const FFMPEG      = '/tmp/nebula-render/node_modules/@ffmpeg-installer/linux-x64/ffmpeg';
const OUT_DIR     = '/home/user/nebula-agency/clients/nebula-agency/videos-daily';
const FPS = 60, TOTAL = 30, FRAMES = FPS * TOTAL;

// ─── Topic management ────────────────────────────────────
function pickTopic() {
  const data = JSON.parse(fs.readFileSync(TOPICS_FILE, 'utf8'));
  if (!data.queue.length) { data.queue = data.used.slice(); data.used = []; }
  const topic = data.queue.shift();
  data.used.push(topic);
  fs.writeFileSync(TOPICS_FILE, JSON.stringify(data, null, 2));
  return topic;
}

// ─── Logo ────────────────────────────────────────────────
function loadLogo() {
  return 'data:image/jpeg;base64,' + fs.readFileSync(LOGO_FILE).toString('base64');
}

// ─── Audio synthesis ─────────────────────────────────────
function makeAudio() {
  const SR=44100,DUR=30,NC=2,N=SR*DUR;
  const L=new Float32Array(N),R=new Float32Array(N);
  const BPM=118,BEAT=60/BPM;
  const NOTE={E2:82.4,A2:110,B2:123.5,D3:146.8,E3:164.8,G3:196,B3:246.9,D4:293.7,E4:329.6,G4:392};
  const sin=(f,t)=>Math.sin(2*Math.PI*f*t);
  const saw=(f,t)=>2*(t*f%1)-1;
  const noise=()=>Math.random()*2-1;
  const clamp=v=>v<-1?-1:v>1?1:v;
  const c01=v=>v<0?0:v>1?1:v;
  const DL=Math.round(SR*.06),DB=Math.round(SR*.11);
  const dlBuf=new Float32Array(DL*2),dlPos=[0,0];
  const reverb=(s,ch)=>{var o=dlBuf[dlPos[ch]];dlBuf[dlPos[ch]]=s+o*.35;dlPos[ch]=(dlPos[ch]+1)%(ch===0?DL:DB);return s+o*.38;};
  for(let i=0;i<N;i++){
    const t=i/SR;
    const kt=t%BEAT;
    const kick=0.48*sin(80*(1+3*Math.exp(-kt*22)),t)*Math.exp(-kt*9)*(kt<0.2?1:0);
    const beatNum=Math.floor(t/BEAT),st2=t%(BEAT*2);
    const snare=((beatNum%2===1)&&st2<0.12)?0.22*noise()*Math.exp(-st2*28):0;
    const hT=t%(BEAT/2);
    const hat=0.08*noise()*Math.exp(-hT*40)*(hT<0.04?1:0);
    const oT=t%(BEAT*4)-BEAT*2;
    const ohat=(oT>0&&oT<0.18)?0.05*noise()*Math.exp(-oT*12):0;
    const barLen=BEAT*4,barPos=Math.floor(t/barLen)%8;
    const bassN=[NOTE.E2,NOTE.E2,NOTE.A2,NOTE.A2,NOTE.D3,NOTE.D3,NOTE.B2,NOTE.B2];
    const bF=bassN[barPos],bT=t%barLen,bEnv=Math.exp(-bT*.8)*.7+.3;
    const bass=0.22*(saw(bF,t)*.6+sin(bF*2,t)*.4)*bEnv;
    const padPh=Math.floor(t/(barLen*2))%2,p1=padPh===0?NOTE.E3:NOTE.D3;
    const pad=(sin(p1,t)*.04+sin(NOTE.G3,t)*.03+sin(NOTE.B3,t)*.025)*.9;
    let mel=0;
    if(t>8){const mN=[NOTE.E4,NOTE.G4,NOTE.E4,NOTE.D4,NOTE.B3,NOTE.D4,NOTE.E4,NOTE.G4];
      mel=.09*sin(mN[Math.floor(t/barLen)%8],t)*(Math.exp(-(t%barLen)*1.2)*.5+.05)*c01((t-8)/2);}
    let arp=0;
    if(t>5){const aN=[NOTE.E4,NOTE.B3,NOTE.G3,NOTE.E3,NOTE.B3,NOTE.G3,NOTE.E4,NOTE.D4];
      arp=.06*sin(aN[Math.floor(t/(BEAT/2))%8]*2,t)*Math.exp(-(t%(BEAT/2))*6)*c01((t-5)/1.5);}
    const dry=clamp(kick+snare+hat+ohat+bass*.95+pad+mel+arp);
    L[i]=clamp(reverb(dry,0)*.82);
    R[i]=clamp(reverb(dry+sin(NOTE.E3,t)*.004,1)*.82);
  }
  for(let i=0;i<SR;i++){const f=i/SR;L[i]*=f;R[i]*=f;const j=N-1-i;L[j]*=f;R[j]*=f;}
  const dataLen=N*2*4;
  const hdr=Buffer.alloc(44);
  hdr.write('RIFF',0);hdr.writeUInt32LE(36+dataLen,4);hdr.write('WAVE',8);hdr.write('fmt ',12);
  hdr.writeUInt32LE(16,16);hdr.writeUInt16LE(3,20);hdr.writeUInt16LE(NC,22);hdr.writeUInt32LE(SR,24);
  hdr.writeUInt32LE(SR*NC*4,28);hdr.writeUInt16LE(NC*4,32);hdr.writeUInt16LE(32,34);hdr.write('data',36);
  hdr.writeUInt32LE(dataLen,40);
  const pcm=Buffer.alloc(N*8);
  for(let i=0;i<N;i++){pcm.writeFloatLE(L[i],i*8);pcm.writeFloatLE(R[i],i*8+4);}
  return Buffer.concat([hdr,pcm]);
}

// ─── Numeric parser ──────────────────────────────────────
// "95" → {v:95, sfx:""}, "3x" → {v:3, sfx:"x"}, "8s" → {v:8, sfx:"s"}
function parseNum(s) {
  const m=String(s).match(/^(\d+\.?\d*)(.*)/);
  return m?{v:parseFloat(m[1]),sfx:m[2]}:{v:0,sfx:String(s)};
}

// ─── Illustration HTML (p = scene prefix 0/1/2) ───────────
function illustrationHTML(type, p) {
  switch(type) {
    case 'phone': return `<div style="width:76px;height:130px;background:linear-gradient(155deg,#1a0840,#08001c);border-radius:16px;border:2.5px solid rgba(160,130,255,.45);overflow:hidden;box-shadow:0 8px 32px rgba(124,58,237,.3);"><div style="height:14px;background:linear-gradient(90deg,#4f46e5,#7c3aed);display:flex;align-items:center;justify-content:center;"><div style="width:20px;height:3px;background:rgba(255,255,255,.3);border-radius:2px;"></div></div><div style="padding:8px 7px;"><div style="height:5px;background:rgba(124,58,237,.3);border-radius:3px;margin-bottom:5px;"></div><div style="height:5px;background:rgba(124,58,237,.2);border-radius:3px;width:65%;margin-bottom:10px;"></div><div style="display:flex;align-items:flex-end;gap:4px;height:46px;"><div id="i${p}b1" style="flex:1;background:linear-gradient(to top,#7c3aed,#c084fc);border-radius:2px 2px 0 0;height:0%;transition:none;"></div><div id="i${p}b2" style="flex:1;background:linear-gradient(to top,#7c3aed,#c084fc);border-radius:2px 2px 0 0;height:0%;transition:none;"></div><div id="i${p}b3" style="flex:1;background:linear-gradient(to top,#c084fc,#ffd700);border-radius:2px 2px 0 0;height:0%;transition:none;"></div><div id="i${p}b4" style="flex:1;background:linear-gradient(to top,#ffd700,#fff);border-radius:2px 2px 0 0;height:0%;transition:none;"></div></div></div><div style="height:14px;background:rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;border-top:1px solid rgba(255,255,255,.05);"><div style="width:26px;height:5px;border-radius:3px;border:1.5px solid rgba(255,255,255,.25);"></div></div></div>`;

    case 'chart': return `<div style="width:140px;height:95px;background:rgba(255,255,255,.04);border:1.5px solid rgba(124,58,237,.3);border-radius:12px;padding:10px 12px 8px;box-sizing:border-box;"><div style="display:flex;align-items:flex-end;gap:6px;height:66px;"><div id="i${p}c1" style="flex:1;background:linear-gradient(to top,#4f46e5,#7c3aed);border-radius:2px 2px 0 0;height:0%;transition:none;"></div><div id="i${p}c2" style="flex:1;background:linear-gradient(to top,#7c3aed,#c084fc);border-radius:2px 2px 0 0;height:0%;transition:none;"></div><div id="i${p}c3" style="flex:1;background:linear-gradient(to top,#c084fc,#e879f9);border-radius:2px 2px 0 0;height:0%;transition:none;"></div><div id="i${p}c4" style="flex:1;background:linear-gradient(to top,#f59e0b,#ffd700);border-radius:2px 2px 0 0;height:0%;transition:none;"></div><div id="i${p}c5" style="flex:1;background:linear-gradient(to top,#ffd700,#fff);border-radius:2px 2px 0 0;height:0%;transition:none;"></div></div><div style="height:1.5px;background:rgba(255,255,255,.15);margin-top:4px;border-radius:1px;"></div></div>`;

    case 'clock': return `<div style="width:110px;height:110px;border-radius:50%;background:radial-gradient(circle at 40% 40%,#1a0850,#08001c);border:2.5px solid rgba(124,58,237,.5);position:relative;box-shadow:0 0 32px rgba(124,58,237,.22);"><span style="position:absolute;top:7px;left:50%;transform:translateX(-50%);font-size:9px;font-weight:700;color:rgba(255,255,255,.65);">12</span><span style="position:absolute;right:7px;top:50%;transform:translateY(-50%);font-size:9px;font-weight:700;color:rgba(255,255,255,.65);">3</span><span style="position:absolute;bottom:6px;left:50%;transform:translateX(-50%);font-size:9px;font-weight:700;color:rgba(255,255,255,.65);">6</span><span style="position:absolute;left:7px;top:50%;transform:translateY(-50%);font-size:9px;font-weight:700;color:rgba(255,255,255,.65);">9</span><div id="i${p}hh" style="position:absolute;bottom:50%;left:50%;width:3px;height:28px;margin-left:-1.5px;border-radius:2px 2px 0 0;background:linear-gradient(to top,#7c3aed,#c084fc);transform-origin:bottom center;transform:rotate(0deg);"></div><div id="i${p}hm" style="position:absolute;bottom:50%;left:50%;width:2px;height:38px;margin-left:-1px;border-radius:2px 2px 0 0;background:linear-gradient(to top,#ffd700,#fff);transform-origin:bottom center;transform:rotate(0deg);"></div><div id="i${p}hs" style="position:absolute;bottom:50%;left:50%;width:1.5px;height:42px;margin-left:-.75px;border-radius:2px 2px 0 0;background:#ff4444;transform-origin:bottom center;transform:rotate(0deg);"></div><div style="position:absolute;top:50%;left:50%;width:8px;height:8px;border-radius:50%;background:#ffd700;transform:translate(-50%,-50%);z-index:5;box-shadow:0 0 6px rgba(255,215,0,.7);"></div></div>`;

    case 'chat': return `<div style="position:relative;width:150px;height:110px;"><div id="i${p}m1" style="position:absolute;top:0;left:0;background:linear-gradient(135deg,#4f46e5,#7c3aed);border-radius:14px 14px 14px 2px;padding:9px 14px;font-size:11px;color:#fff;font-weight:600;white-space:nowrap;opacity:0;transform:scale(.7);">Ça coûte combien ?</div><div id="i${p}m2" style="position:absolute;bottom:0;right:0;background:linear-gradient(135deg,#7c3aed,#c084fc);border-radius:14px 14px 2px 14px;padding:9px 14px;font-size:11px;color:#fff;font-weight:600;white-space:nowrap;opacity:0;transform:scale(.7);">Je commande !</div></div>`;

    case 'check': return `<div style="width:100px;height:100px;border-radius:50%;background:linear-gradient(135deg,rgba(124,58,237,.2),rgba(192,132,252,.1));border:3px solid rgba(124,58,237,.5);display:flex;align-items:center;justify-content:center;box-shadow:0 0 32px rgba(124,58,237,.22);"><svg id="i${p}chk" width="52" height="52" viewBox="0 0 52 52" style="opacity:0;transform:scale(.5);"><polyline points="10,27 22,39 42,14" stroke="#ffd700" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>`;

    case 'camera': return `<div style="position:relative;width:110px;height:90px;"><div style="width:110px;height:78px;background:linear-gradient(155deg,#1a0840,#0d0525);border-radius:14px;border:2px solid rgba(160,130,255,.35);display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;"><div style="position:absolute;top:7px;left:9px;width:10px;height:10px;border-radius:50%;background:rgba(255,215,0,.3);border:2px solid rgba(255,215,0,.5);"></div><div style="width:48px;height:48px;border-radius:50%;border:3px solid rgba(124,58,237,.5);display:flex;align-items:center;justify-content:center;"><div id="i${p}lens" style="width:30px;height:30px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#4f46e5,#08001c);border:2px solid rgba(124,58,237,.8);box-shadow:0 0 14px rgba(124,58,237,.5);"></div></div><div id="i${p}flash" style="position:absolute;top:7px;right:9px;width:10px;height:10px;border-radius:2px;background:rgba(255,215,0,0);"></div></div><div style="width:28px;height:12px;background:linear-gradient(155deg,#1a0840,#0d0525);border-radius:5px 5px 0 0;border:2px solid rgba(160,130,255,.35);border-bottom:none;position:absolute;top:-12px;left:18px;"></div></div>`;

    case 'rocket': return `<div id="i${p}rkt" style="position:relative;width:54px;height:110px;display:flex;flex-direction:column;align-items:center;"><div style="width:0;height:0;border-left:14px solid transparent;border-right:14px solid transparent;border-bottom:26px solid #7c3aed;"></div><div style="width:28px;flex:1;background:linear-gradient(to bottom,#7c3aed,#c084fc);position:relative;display:flex;align-items:center;justify-content:center;"><div style="width:14px;height:14px;border-radius:50%;background:rgba(255,255,255,.15);border:1.5px solid rgba(255,255,255,.35);"></div><div style="position:absolute;bottom:0;left:-9px;width:0;height:0;border-right:9px solid #9f56d4;border-top:12px solid transparent;border-bottom:12px solid transparent;"></div><div style="position:absolute;bottom:0;right:-9px;width:0;height:0;border-left:9px solid #9f56d4;border-top:12px solid transparent;border-bottom:12px solid transparent;"></div></div><div id="i${p}flame" style="width:14px;height:0px;background:linear-gradient(to bottom,#ffd700,#ff6600,transparent);border-radius:0 0 50% 50%;"></div></div>`;

    case 'star': return `<div style="display:flex;gap:4px;align-items:center;"><div id="i${p}s1" style="font-size:26px;opacity:0;transform:scale(.4);">&#11088;</div><div id="i${p}s2" style="font-size:34px;opacity:0;transform:scale(.4);">&#11088;</div><div id="i${p}s3" style="font-size:26px;opacity:0;transform:scale(.4);">&#11088;</div></div>`;

    default: return `<div style="width:100px;height:100px;border-radius:50%;background:radial-gradient(circle at 38% 38%,#4f46e5,#08001c);border:2.5px solid rgba(124,58,237,.5);display:flex;align-items:center;justify-content:center;box-shadow:0 0 32px rgba(124,58,237,.25);"><div style="width:50px;height:50px;border-radius:50%;border:2.5px solid rgba(192,132,252,.5);"></div></div>`;
  }
}

// ─── Illustration animation JS (embedded in setTime) ──────
// Returns a JS code string; p=scene prefix, ss=scene start time
function illustrationAnim(type, p, ss) {
  switch(type) {
    case 'phone': return (
      'var _pb=[document.getElementById("i'+p+'b1"),document.getElementById("i'+p+'b2"),document.getElementById("i'+p+'b3"),document.getElementById("i'+p+'b4")];'+
      'var _pbt=[30,52,44,72];'+
      '_pb.forEach(function(b,i){if(b)b.style.height=(eO(rng(t,'+(ss+.6)+'+i*.22,'+(ss+1.6)+'+i*.22))*_pbt[i])+"%";});'
    );
    case 'chart': return (
      'var _cc=[document.getElementById("i'+p+'c1"),document.getElementById("i'+p+'c2"),document.getElementById("i'+p+'c3"),document.getElementById("i'+p+'c4"),document.getElementById("i'+p+'c5")];'+
      'var _cct=[32,50,66,80,95];'+
      '_cc.forEach(function(c,i){if(c)c.style.height=(eO(rng(t,'+(ss+.4)+'+i*.18,'+(ss+1.4)+'+i*.18))*_cct[i])+"%";});'
    );
    case 'clock': return (
      'var _hh=document.getElementById("i'+p+'hh"),_hm=document.getElementById("i'+p+'hm"),_hs=document.getElementById("i'+p+'hs");'+
      'if(_hh)_hh.style.transform="rotate("+(t*8)+"deg)";'+
      'if(_hm)_hm.style.transform="rotate("+(t*52)+"deg)";'+
      'if(_hs)_hs.style.transform="rotate("+(t*360)+"deg)";'
    );
    case 'chat': return (
      'var _cm1=document.getElementById("i'+p+'m1"),_cm2=document.getElementById("i'+p+'m2");'+
      'if(_cm1){var _cp1=eBk(rng(t,'+(ss+.8)+','+(ss+1.6)+'));_cm1.style.opacity=_cp1;_cm1.style.transform="scale("+lerp(.7,1,_cp1)+")";}'+
      'if(_cm2){var _cp2=eBk(rng(t,'+(ss+1.6)+','+(ss+2.4)+'));_cm2.style.opacity=_cp2;_cm2.style.transform="scale("+lerp(.7,1,_cp2)+")";}  '
    );
    case 'check': return (
      'var _ck=document.getElementById("i'+p+'chk");'+
      'if(_ck){var _cp=eBk(rng(t,'+(ss+.6)+','+(ss+1.5)+'));_ck.style.opacity=_cp;_ck.style.transform="scale("+lerp(.5,1,_cp)+")";}  '
    );
    case 'camera': return (
      'var _cl=document.getElementById("i'+p+'lens"),_cf=document.getElementById("i'+p+'flash");'+
      'if(_cl){var _clp=.5+.5*Math.sin(t*3.2);_cl.style.boxShadow="0 0 "+(14+_clp*10)+"px rgba(124,58,237,"+(.5+_clp*.3)+")";}'+
      'if(_cf){_cf.style.background="rgba(255,215,0,"+(Math.sin(t*4)>.8?.7:0)+")";}  '
    );
    case 'rocket': return (
      'var _rfl=document.getElementById("i'+p+'flame"),_rrkt=document.getElementById("i'+p+'rkt");'+
      'if(_rfl){var _rfp=eO(rng(t,'+(ss+.5)+','+(ss+1)+'));_rfl.style.height=(_rfp*(18+Math.sin(t*12)*4))+"px";}'+
      'if(_rrkt)_rrkt.style.transform="translateY("+(Math.sin(t*6)*2)+"px)";  '
    );
    case 'star': return (
      'var _ss=[document.getElementById("i'+p+'s1"),document.getElementById("i'+p+'s2"),document.getElementById("i'+p+'s3")];'+
      '['+ss+'.5,'+ss+'.9,'+(ss+1.3)+'].forEach(function(d,i){var _sp=eBk(rng(t,d,d+.7));_ss[i].style.opacity=_sp;_ss[i].style.transform="scale("+lerp(.4,1,_sp)+")";});'
    );
    default: return '';
  }
}

// ─── HTML builder ─────────────────────────────────────────
function buildHTML(topic, logoB64) {
  const f = topic.facts;
  const n0=parseNum(f[0].num), n1=parseNum(f[1].num), n2=parseNum(f[2].num);
  const lbl = x => x.label.replace(/\n/g,'<br>');
  const SS1=5, SS2=13, SS3=21, SS4=27;
  const a0=illustrationAnim(f[0].illustration,0,SS1);
  const a1=illustrationAnim(f[1].illustration,1,SS2);
  const a2=illustrationAnim(f[2].illustration,2,SS3);

  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>NEBULA — ${topic.title}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:540px;height:960px;overflow:hidden;background:#04010c;
  font-family:'Segoe UI',system-ui,Arial,sans-serif;-webkit-font-smoothing:antialiased;}
#cv{width:540px;height:960px;position:relative;overflow:hidden;}
.sc{position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;padding:50px 34px;pointer-events:none;}
#pb{position:absolute;bottom:0;left:0;height:4px;
  background:linear-gradient(90deg,#7c3aed,#c084fc,#ffd700);z-index:99;width:0%;}
</style>
</head>
<body>
<div id="cv">
  <canvas id="bg" width="540" height="960" style="position:absolute;inset:0;z-index:0;"></canvas>
  <div id="pb"></div>

  <!-- S0: Hook 0-5s -->
  <div class="sc" id="s0" style="z-index:10;opacity:0;">
    <div id="s0badge" style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#c084fc;margin-bottom:28px;opacity:0;">LE SAVIEZ-VOUS ?</div>
    <div id="s0icon" style="font-size:72px;margin-bottom:24px;opacity:0;transform:scale(.7);">&#128161;</div>
    <div id="s0t" style="font-size:26px;font-weight:900;color:#fff;text-align:center;line-height:1.4;opacity:0;transform:translateY(24px);">${topic.hook}</div>
    <div id="s0d" style="height:3px;width:0;background:linear-gradient(90deg,#7c3aed,#ffd700);border-radius:2px;margin:20px auto;"></div>
  </div>

  <!-- S1: Fact 0 · ${SS1}-${SS2}s -->
  <div class="sc" id="s1" style="z-index:10;opacity:0;">
    <div id="s1src" style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:rgba(192,132,252,.7);margin-bottom:16px;opacity:0;text-align:center;">${f[0].source}</div>
    <div id="s1il" style="margin-bottom:22px;opacity:0;transform:translateY(16px) scale(.85);">
      ${illustrationHTML(f[0].illustration, 0)}
    </div>
    <div id="s1card" style="background:rgba(124,58,237,.12);border:1.5px solid rgba(124,58,237,.35);border-radius:20px;padding:22px 24px;width:100%;text-align:center;opacity:0;transform:translateY(18px);">
      <div style="display:flex;align-items:flex-end;justify-content:center;gap:1px;line-height:1;">
        <div id="s1n" style="font-size:76px;font-weight:900;color:#ffd700;text-shadow:0 0 28px rgba(255,215,0,.4);font-variant-numeric:tabular-nums;">0</div>
        <div style="font-size:40px;font-weight:900;color:#ffd700;margin-bottom:8px;">${n0.sfx}${f[0].unit}</div>
      </div>
      <div style="font-size:15px;font-weight:600;color:#fff;margin-top:6px;line-height:1.5;">${lbl(f[0])}</div>
    </div>
  </div>

  <!-- S2: Fact 1 · ${SS2}-${SS3}s -->
  <div class="sc" id="s2" style="z-index:10;opacity:0;">
    <div id="s2src" style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:rgba(192,132,252,.7);margin-bottom:16px;opacity:0;text-align:center;">${f[1].source}</div>
    <div id="s2il" style="margin-bottom:22px;opacity:0;transform:translateY(16px) scale(.85);">
      ${illustrationHTML(f[1].illustration, 1)}
    </div>
    <div id="s2card" style="background:rgba(124,58,237,.12);border:1.5px solid rgba(124,58,237,.35);border-radius:20px;padding:22px 24px;width:100%;text-align:center;opacity:0;transform:translateY(18px);">
      <div style="display:flex;align-items:flex-end;justify-content:center;gap:1px;line-height:1;">
        <div id="s2n" style="font-size:76px;font-weight:900;color:#ffd700;text-shadow:0 0 28px rgba(255,215,0,.4);font-variant-numeric:tabular-nums;">0</div>
        <div style="font-size:40px;font-weight:900;color:#ffd700;margin-bottom:8px;">${n1.sfx}${f[1].unit}</div>
      </div>
      <div style="font-size:15px;font-weight:600;color:#fff;margin-top:6px;line-height:1.5;">${lbl(f[1])}</div>
    </div>
  </div>

  <!-- S3: Fact 2 · ${SS3}-${SS4}s -->
  <div class="sc" id="s3" style="z-index:10;opacity:0;">
    <div id="s3src" style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:rgba(192,132,252,.7);margin-bottom:16px;opacity:0;text-align:center;">${f[2].source}</div>
    <div id="s3il" style="margin-bottom:22px;opacity:0;transform:translateY(16px) scale(.85);">
      ${illustrationHTML(f[2].illustration, 2)}
    </div>
    <div id="s3card" style="background:rgba(124,58,237,.12);border:1.5px solid rgba(124,58,237,.35);border-radius:20px;padding:22px 24px;width:100%;text-align:center;opacity:0;transform:translateY(18px);">
      <div style="display:flex;align-items:flex-end;justify-content:center;gap:1px;line-height:1;">
        <div id="s3n" style="font-size:76px;font-weight:900;color:#ffd700;text-shadow:0 0 28px rgba(255,215,0,.4);font-variant-numeric:tabular-nums;">0</div>
        <div style="font-size:40px;font-weight:900;color:#ffd700;margin-bottom:8px;">${n2.sfx}${f[2].unit}</div>
      </div>
      <div style="font-size:15px;font-weight:600;color:#fff;margin-top:6px;line-height:1.5;">${lbl(f[2])}</div>
    </div>
  </div>

  <!-- S4: Outro · ${SS4}-30s -->
  <div class="sc" id="s4" style="z-index:10;opacity:0;">
    <div id="s4glow" style="position:absolute;width:380px;height:380px;border-radius:50%;top:50%;left:50%;transform:translate(-50%,-50%);z-index:0;"></div>
    <img id="s4logo" src="${logoB64}" style="width:210px;height:auto;object-fit:contain;position:relative;z-index:1;opacity:0;transform:scale(.85);" alt="NEBULA Agency">
    <div id="s4d" style="height:3px;width:0;background:linear-gradient(90deg,#7c3aed,#ffd700);border-radius:2px;margin:18px auto;position:relative;z-index:1;"></div>
    <div id="s4cta" style="font-size:16px;color:rgba(255,255,255,.7);text-align:center;line-height:1.65;position:relative;z-index:1;opacity:0;font-weight:500;">${topic.cta}</div>
    <div id="s4btn" style="background:linear-gradient(135deg,#7c3aed,#9c27b0);border-radius:50px;padding:16px 32px;font-size:15px;font-weight:800;color:#fff;text-align:center;margin-top:22px;width:100%;box-shadow:0 0 32px rgba(124,58,237,.45);position:relative;z-index:1;opacity:0;transform:translateY(14px);">&#128172; Contactez-nous sur WhatsApp</div>
  </div>
</div>

<script>
function c01(v){return v<0?0:v>1?1:v;}
function lerp(a,b,t){return a+(b-a)*c01(t);}
function rng(t,s,e){return c01((t-s)/(e-s));}
function eO(t){t=c01(t);return 1-Math.pow(1-t,3);}
function eIO(t){t=c01(t);return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;}
function eBk(t){t=c01(t);var c=1.70158;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2);}
function eEl(t){if(!t||t===1)return t;return Math.pow(2,-10*t)*Math.sin((t*10-.75)*Math.PI*2/3)+1;}

var bgc=document.getElementById('bg'),ctx=bgc.getContext('2d');
var bgCache=null,STARS=[];
(function(){
  var pr=[7919,6271,5197,4139,3571,2971,2381,1873,1409,997];
  function sr(i,j){return Math.abs(Math.sin(i*pr[j%10]+j*pr[(i+1)%10]));}
  for(var i=0;i<65;i++){
    STARS.push({x:sr(i,0)*538+1,y:sr(i,1)*958+1,r:sr(i,2)*1.3+.3,
      ph:sr(i,3)*Math.PI*2,sp:sr(i,4)*2+.5,
      c:['#ffffff','#ffffff','#ffd700','#c8a2ff','#ffffff'][i%5]});
  }
  var g=ctx.createRadialGradient(135,130,0,270,480,530);
  g.addColorStop(0,'#1c0055');g.addColorStop(.45,'#0d0025');g.addColorStop(1,'#04010c');
  ctx.fillStyle=g;ctx.fillRect(0,0,540,960);
  bgCache=ctx.getImageData(0,0,540,960);
})();
function drawBG(t){
  ctx.putImageData(bgCache,0,0);
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i],a=c01(.3+.5*Math.sin(t*s.sp+s.ph));
    var hex=Math.round(a*255).toString(16).padStart(2,'0');
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fillStyle=s.c+hex;ctx.fill();
    if(s.r>1.1){
      var grd=ctx.createRadialGradient(s.x,s.y,0,s.x,s.y,s.r*4);
      grd.addColorStop(0,s.c+(Math.round(a*.3*255).toString(16).padStart(2,'0')));
      grd.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=grd;ctx.beginPath();ctx.arc(s.x,s.y,s.r*4,0,Math.PI*2);ctx.fill();
    }
  }
}

var E={};
's0,s0badge,s0icon,s0t,s0d,s1,s1src,s1il,s1card,s1n,s2,s2src,s2il,s2card,s2n,s3,s3src,s3il,s3card,s3n,s4,s4glow,s4logo,s4d,s4cta,s4btn,pb'.split(',').forEach(function(id){E[id]=document.getElementById(id);});

var N0V=${n0.v}, N1V=${n1.v}, N2V=${n2.v};

window.setTime = function(t){
  drawBG(t);
  E.pb.style.width=(t/30*100)+'%';

  // S0: Hook 0-5s
  (function(){
    var show=eO(rng(t,0,.5)),hide=eIO(rng(t,4.4,5));
    E.s0.style.opacity=c01(show*(1-hide));
    if(show===0)return;
    E.s0badge.style.opacity=eO(rng(t,.1,.8));
    var ip=eBk(rng(t,.2,1.1));
    E.s0icon.style.opacity=ip;E.s0icon.style.transform='scale('+lerp(.7,1,ip)+')';
    var tp=eO(rng(t,.7,1.8));
    E.s0t.style.opacity=tp;E.s0t.style.transform='translateY('+lerp(24,0,tp)+'px)';
    E.s0d.style.width=lerp(0,80,eO(rng(t,1.4,2.4)))+'px';
  })();

  // S1: Fact 0 · SS1=5s
  (function(){
    var show=eO(rng(t,4.8,5.6)),hide=eIO(rng(t,12.5,13.1));
    E.s1.style.opacity=c01(show*(1-hide));
    if(show===0)return;
    E.s1src.style.opacity=eO(rng(t,5,5.9));
    var ip=eEl(rng(t,5.3,6.5));
    E.s1il.style.opacity=ip;E.s1il.style.transform='translateY('+lerp(16,0,ip)+'px) scale('+lerp(.85,1,ip)+')';
    var cp=eO(rng(t,6.1,7));
    E.s1card.style.opacity=cp;E.s1card.style.transform='translateY('+lerp(18,0,cp)+'px)';
    E.s1n.textContent=Math.round(N0V*eO(rng(t,6.5,11)));
    ${a0}
  })();

  // S2: Fact 1 · SS2=13s
  (function(){
    var show=eO(rng(t,12.8,13.6)),hide=eIO(rng(t,20.5,21.1));
    E.s2.style.opacity=c01(show*(1-hide));
    if(show===0)return;
    E.s2src.style.opacity=eO(rng(t,13,13.9));
    var ip=eEl(rng(t,13.3,14.5));
    E.s2il.style.opacity=ip;E.s2il.style.transform='translateY('+lerp(16,0,ip)+'px) scale('+lerp(.85,1,ip)+')';
    var cp=eO(rng(t,14.1,15));
    E.s2card.style.opacity=cp;E.s2card.style.transform='translateY('+lerp(18,0,cp)+'px)';
    E.s2n.textContent=Math.round(N1V*eO(rng(t,14.5,19)));
    ${a1}
  })();

  // S3: Fact 2 · SS3=21s
  (function(){
    var show=eO(rng(t,20.8,21.6)),hide=eIO(rng(t,26.5,27.1));
    E.s3.style.opacity=c01(show*(1-hide));
    if(show===0)return;
    E.s3src.style.opacity=eO(rng(t,21,21.9));
    var ip=eEl(rng(t,21.3,22.5));
    E.s3il.style.opacity=ip;E.s3il.style.transform='translateY('+lerp(16,0,ip)+'px) scale('+lerp(.85,1,ip)+')';
    var cp=eO(rng(t,22.1,23));
    E.s3card.style.opacity=cp;E.s3card.style.transform='translateY('+lerp(18,0,cp)+'px)';
    E.s3n.textContent=Math.round(N2V*eO(rng(t,22.5,26)));
    ${a2}
  })();

  // S4: Outro · SS4=27s
  (function(){
    var show=eO(rng(t,26.8,27.6));
    E.s4.style.opacity=show;
    if(show===0)return;
    var ga=.3+.2*Math.sin(t*1.8);
    E.s4glow.style.background='radial-gradient(circle,rgba(124,58,237,'+ga+') 0%,transparent 70%)';
    var lp=eEl(rng(t,27,28.2));
    E.s4logo.style.opacity=lp;E.s4logo.style.transform='scale('+lerp(.85,1,lp)+')';
    E.s4d.style.width=lerp(0,100,eO(rng(t,27.9,28.8)))+'px';
    E.s4cta.style.opacity=eO(rng(t,28.3,29.2));
    var bp=eO(rng(t,28.6,29.5));
    E.s4btn.style.opacity=bp;E.s4btn.style.transform='translateY('+lerp(14,0,bp)+'px)';
  })();
};

window.setTime(0);
</script>
</body>
</html>`;
}

// ─── Renderer ─────────────────────────────────────────────
async function render(htmlPath, audioPath, outPath) {
  const sparticuz = require('@sparticuz/chromium');
  const {chromium} = require('playwright');
  const t0 = Date.now();

  const execPath = await sparticuz.executablePath();
  const browser = await chromium.launch({
    executablePath: execPath, headless: true,
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage',
           '--use-gl=swiftshader','--enable-unsafe-swiftshader',
           '--hide-scrollbars','--disable-web-security','--font-render-hinting=none'],
  });

  const ctx = await browser.newContext({viewport:{width:540,height:960},deviceScaleFactor:1});
  const page = await ctx.newPage();

  await page.addInitScript(() => {
    const s=document.createElement('style');
    s.textContent='html,body{margin:0!important;padding:0!important;overflow:hidden!important;width:540px;height:960px;}#pb{display:none!important;}';
    if(document.head)document.head.appendChild(s);
    else document.addEventListener('DOMContentLoaded',()=>document.head.appendChild(s));
  });

  await page.goto('file://'+htmlPath, {waitUntil:'load'});

  const ffmpeg = spawn(FFMPEG, [
    '-y',
    '-f','image2pipe','-framerate',String(FPS),'-i','pipe:0',
    '-i',audioPath,
    '-filter_complex','[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v]',
    '-map','[v]','-map','1:a',
    '-c:v','libx264','-profile:v','high','-level','5.1','-preset','fast','-crf','16',
    '-c:a','aac','-b:a','192k','-ar','44100',
    '-r',String(FPS),'-movflags','+faststart',
    outPath
  ]);
  ffmpeg.stderr.on('data', d => {
    const s=d.toString();
    if(s.includes('fps='))process.stderr.write('\r'+s.trim().split('\r').pop());
  });

  let errs=0;
  for(let f=0;f<FRAMES;f++){
    try{
      await page.evaluate(t=>window.setTime(t), f/FPS);
      const png=await page.screenshot({type:'png',clip:{x:0,y:0,width:540,height:960}});
      const ok=ffmpeg.stdin.write(png);
      if(!ok)await new Promise(r=>ffmpeg.stdin.once('drain',r));
    }catch(e){errs++;if(errs>8){console.error('Abort:',e);break;}}
    if(f%300===0){
      const pct=Math.round(f/FRAMES*100);
      const el=((Date.now()-t0)/1000).toFixed(0);
      console.log(pct+'% — frame '+f+'/'+FRAMES+' — '+el+'s');
    }
  }

  ffmpeg.stdin.end();
  const code=await new Promise(r=>ffmpeg.on('close',r));
  await browser.close();
  console.log('\nRendered in '+((Date.now()-t0)/1000).toFixed(1)+'s → '+outPath);
  return code;
}

// ─── Main ─────────────────────────────────────────────────
(async () => {
  const count = parseInt(process.argv[2]) || 1;

  if (!fs.existsSync(FFMPEG)) {
    console.error('ffmpeg manquant. Lancez: cd /tmp/nebula-render && npm install');
    process.exit(1);
  }

  fs.mkdirSync(OUT_DIR, {recursive:true});
  const logoB64 = loadLogo();
  const today = new Date().toISOString().slice(0,10);

  for (let i=0; i<count; i++) {
    const topic = pickTopic();
    console.log('\n['+( i+1)+'/'+count+'] '+topic.title);

    const htmlPath = '/tmp/nebula-topic-'+i+'.html';
    const audioPath = '/tmp/nebula-audio-'+i+'.wav';
    const outPath = path.join(OUT_DIR, today+'-'+(i+1)+'-'+topic.id+'.mp4');

    console.log('  HTML...');
    fs.writeFileSync(htmlPath, buildHTML(topic, logoB64));

    console.log('  Audio...');
    fs.writeFileSync(audioPath, makeAudio());

    console.log('  Render '+FRAMES+' frames...');
    await render(htmlPath, audioPath, outPath);
  }

  console.log('\n✓ '+count+' vidéo(s) prêtes dans '+OUT_DIR);
})();
