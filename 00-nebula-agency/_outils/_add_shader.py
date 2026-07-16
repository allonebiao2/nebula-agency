#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajoute le fond animé WebGL (shader nébuleuse @atzedent) au hero de v9,
recoloré aux couleurs NEBULA (bleu/violet/cyan). Repli WebGL, pause hors-vue, reduced-motion. UTF-8."""
import io, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "nebula_agency_v9.html"
s = io.open(F, encoding="utf-8").read()

# 1) HTML : canvas + scrim juste après l'ouverture du hero
old_open = '<header class="hero">\n  <div class="container hero-grid">'
new_open = ('<header class="hero">\n'
            '  <canvas id="shader" aria-hidden="true"></canvas>\n'
            '  <div class="hero-scrim" aria-hidden="true"></div>\n'
            '  <div class="container hero-grid">')
assert old_open in s, "ouverture hero introuvable"
s = s.replace(old_open, new_open, 1)

# 2) retire l'orbe + anneaux (remplacés par le shader), garde les aperçus flottants
old_orb = ('      <div class="ring r2"><b></b></div>\n'
           '      <div class="ring r1"><b></b></div>\n'
           '      <div class="orb"></div>\n')
assert old_orb in s, "orbe/anneaux introuvables"
s = s.replace(old_orb, '', 1)

# 3) CSS : positionne le shader en fond du hero + lisibilité
CSS = """
/* ===== Fond animé WebGL (shader nébuleuse NEBULA) ===== */
.hero{position:relative;overflow:hidden}
#shader{position:absolute;inset:0;width:100%;height:100%;z-index:0;display:block;background:#05060f}
.hero-scrim{position:absolute;inset:0;z-index:1;pointer-events:none;background:
  linear-gradient(90deg,rgba(6,7,19,.92) 0%,rgba(6,7,19,.62) 40%,rgba(6,7,19,.15) 70%,rgba(6,7,19,.35) 100%),
  radial-gradient(120% 85% at 50% -5%,transparent,rgba(6,7,19,.25) 55%,rgba(6,7,19,.8) 100%)}
.hero>.container{position:relative;z-index:2}
.hero-visual{z-index:2}
@media(max-width:960px){.hero-scrim{background:linear-gradient(180deg,rgba(6,7,19,.5) 0%,rgba(6,7,19,.35) 40%,rgba(6,7,19,.75) 100%)}}
@media(prefers-reduced-motion:reduce){#shader{opacity:.85}}
</style>
</head>"""
assert s.count("</style>\n</head>") == 1, "ancre </style></head> non unique"
s = s.replace("</style>\n</head>", CSS, 1)

# 4) JS : port vanilla du renderer + shader recoloré NEBULA (inséré avant le dernier </script>)
JS = r"""
/* ===== Shader nébuleuse WebGL (port vanilla d'après @atzedent, recoloré NEBULA) ===== */
(function(){
  var cv=document.getElementById('shader'); if(!cv) return;
  var rm=matchMedia('(prefers-reduced-motion:reduce)').matches;
  var gl=cv.getContext('webgl2',{antialias:false,alpha:false,powerPreference:'low-power'});
  if(!gl){cv.style.display='none';return;}   // repli : dégradé + étoiles restent
  var VERT='#version 300 es\nprecision highp float;\nin vec4 position;\nvoid main(){gl_Position=position;}';
  var FRAG=`#version 300 es
precision highp float;
out vec4 O;
uniform vec2 resolution;
uniform float time;
#define FC gl_FragCoord.xy
#define T time
#define R resolution
#define MN min(R.x,R.y)
float rnd(vec2 p){p=fract(p*vec2(12.9898,78.233));p+=dot(p,p+34.56);return fract(p.x*p.y);}
float noise(in vec2 p){vec2 i=floor(p),f=fract(p),u=f*f*(3.-2.*f);float a=rnd(i),b=rnd(i+vec2(1,0)),c=rnd(i+vec2(0,1)),d=rnd(i+1.);return mix(mix(a,b,u.x),mix(c,d,u.x),u.y);}
float fbm(vec2 p){float t=.0,a=1.;mat2 m=mat2(1.,-.5,.2,1.2);for(int i=0;i<5;i++){t+=a*noise(p);p*=2.*m;a*=.5;}return t;}
float clouds(vec2 p){float d=1.,t=.0;for(float i=.0;i<3.;i++){float a=d*fbm(i*10.+p.x*.2+.2*(1.+i)*p.y+d+i*i+p);t=mix(t,d,a);d=a;p*=2./(i+1.);}return t;}
void main(void){
  vec2 uv=(FC-.5*R)/MN,st=uv*vec2(2,1);
  vec3 col=vec3(0);
  float bg=clouds(vec2(st.x+T*.4,-st.y));
  uv*=1.-.3*(sin(T*.2)*.5+.5);
  for(float i=1.;i<12.;i++){
    uv+=.1*cos(i*vec2(.1+.01*i,.8)+i*i+T*.45+.1*uv.x);
    vec2 p=uv;
    float d=length(p);
    col+=.00125/d*(cos(sin(i)*vec3(1,2,3))+1.)*vec3(.82,.86,1.24);
    float b=noise(i+p+bg*1.731);
    col+=.002*b/length(max(p,vec2(b*p.x*.02,p.y)));
    col=mix(col,vec3(bg*.11,bg*.07,bg*.30),d);
  }
  O=vec4(col,1);
}`;
  function mk(t,src){var sh=gl.createShader(t);gl.shaderSource(sh,src);gl.compileShader(sh);
    if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS)){gl.deleteShader(sh);return null;}return sh;}
  var vs=mk(gl.VERTEX_SHADER,VERT),fs=mk(gl.FRAGMENT_SHADER,FRAG);
  if(!vs||!fs){cv.style.display='none';return;}
  var pr=gl.createProgram();gl.attachShader(pr,vs);gl.attachShader(pr,fs);gl.linkProgram(pr);
  if(!gl.getProgramParameter(pr,gl.LINK_STATUS)){cv.style.display='none';return;}
  gl.useProgram(pr);
  var buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,1,-1,-1,1,1,1,-1]),gl.STATIC_DRAW);
  var pos=gl.getAttribLocation(pr,'position');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
  var uRes=gl.getUniformLocation(pr,'resolution'),uT=gl.getUniformLocation(pr,'time');
  var host=cv.parentElement;
  function size(){var sc=matchMedia('(max-width:760px)').matches?.55:.78;
    var w=Math.max(1,host.clientWidth),h=Math.max(1,host.clientHeight);
    cv.width=Math.round(w*sc);cv.height=Math.round(h*sc);gl.viewport(0,0,cv.width,cv.height);}
  size();addEventListener('resize',size,{passive:true});
  function draw(now){gl.uniform2f(uRes,cv.width,cv.height);gl.uniform1f(uT,now*1e-3);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);}
  var raf=null,vis=true;
  function loop(now){draw(now);raf=requestAnimationFrame(loop);}
  function start(){if(!raf&&!rm)raf=requestAnimationFrame(loop);}
  function stop(){if(raf){cancelAnimationFrame(raf);raf=null;}}
  if(rm){draw(2200);}   // mouvement réduit : une seule image fixe
  else{
    if('IntersectionObserver' in window){new IntersectionObserver(function(e){vis=e[0].isIntersecting;vis?start():stop();},{threshold:.01}).observe(cv);}
    else start();
    document.addEventListener('visibilitychange',function(){document.hidden?stop():(vis&&start());});
  }
})();
"""
assert s.count("\n</script>\n</body>") == 1, "ancre </script></body> non unique"
s = s.replace("\n</script>\n</body>", JS + "\n</script>\n</body>", 1)

io.open(F, "w", encoding="utf-8").write(s)
print("shader nébuleuse ajouté au hero · recoloré NEBULA · repli WebGL + pause hors-vue + reduced-motion")
