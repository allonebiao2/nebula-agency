/* ═══════════════════════════════════════════════════════════════════════════
   MA LETTRE À… · LE THÉÂTRE DES OUVERTURES, version « cinéma » (2026-10-22)
   Un moteur 3D écrit pour la lettre, WebGL 1, AUCUNE bibliothèque.
   ─ Mongazi, au premier essai : « pixelisé », « pas fluide », « une qualité de
     console Sega au lieu de PS5 ». Donc, comme une console :
       · l'image est calculée HORS écran, plus grande qu'affichée sur un écran
         d'ordinateur, puis lissée (FXAA) : plus d'escaliers sur les bords ;
       · un halo de lumière (« bloom ») autour de tout ce qui brille ;
       · une profondeur de champ : la table au loin et l'avant-plan sont flous,
         l'objet est net, comme une photo de près ;
       · un vignetage, un grain de pellicule, une courbe de couleur ;
       · le papier se COURBE quand il se soulève (dans le nuanceur), et la
         lumière glisse dessus (un reflet doux) ;
       · 60 images par seconde, et une baisse de qualité automatique, par
         paliers, seulement si l'appareil peine.
   ─ La LUMIÈRE des matières est calculée une fois pour toutes dans Blender
     (Cycles) : les « matcaps » (`rites/matieres/`).
   ─ Tout bouge par le TEMPS (secondes), jamais par image : le même rite tourne
     dans la lettre et se filme image par image dans le studio. Aucun
     Math.random : un tirage à graine (`hasard`).
   ═══════════════════════════════════════════════════════════════════════════ */
var Theatre = (function () {
  "use strict";

  /* ── Les matrices 4×4, en colonnes (l'ordre de WebGL). ── */
  var M = {
    id: function () { return new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]); },
    mul: function (a, b) {
      var o = new Float32Array(16);
      for (var c = 0; c < 4; c++) for (var r = 0; r < 4; r++) {
        o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3];
      }
      return o;
    },
    trans: function (x, y, z) { var m = M.id(); m[12] = x; m[13] = y; m[14] = z; return m; },
    echelle: function (x, y, z) { var m = M.id(); m[0] = x; m[5] = y == null ? x : y; m[10] = z == null ? x : z; return m; },
    rx: function (a) { var c = Math.cos(a), s = Math.sin(a), m = M.id(); m[5] = c; m[6] = s; m[9] = -s; m[10] = c; return m; },
    ry: function (a) { var c = Math.cos(a), s = Math.sin(a), m = M.id(); m[0] = c; m[2] = -s; m[8] = s; m[10] = c; return m; },
    rz: function (a) { var c = Math.cos(a), s = Math.sin(a), m = M.id(); m[0] = c; m[1] = s; m[4] = -s; m[5] = c; return m; },
    chaine: function () { var m = arguments[0]; for (var i = 1; i < arguments.length; i++) m = M.mul(m, arguments[i]); return m; },
    persp: function (fov, asp, pres, loin) {
      var f = 1 / Math.tan(fov / 2), m = new Float32Array(16);
      m[0] = f / asp; m[5] = f; m[10] = (loin + pres) / (pres - loin); m[11] = -1; m[14] = 2 * loin * pres / (pres - loin);
      return m;
    },
    vise: function (oeil, cible, haut) {
      var z = norm(sous(oeil, cible)), x = norm(croix(haut || [0, 1, 0], z)), y = croix(z, x);
      return new Float32Array([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0,
        -pt(x, oeil), -pt(y, oeil), -pt(z, oeil), 1]);
    },
    coin: function (m) { return new Float32Array([m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]]); }
  };
  function sous(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function croix(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function pt(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function norm(a) { var l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }

  /* ── Les courbes et les petits outils du temps. ── */
  var C = {
    borne: function (x) { return x < 0 ? 0 : x > 1 ? 1 : x; },
    p: function (t, a, b) { return C.borne((t - a) / (b - a)); },
    sort: function (x) { return 1 - Math.pow(1 - x, 4); },
    doux: function (x) { return x * x * (3 - 2 * x); },
    entre: function (x) { return x * x * x; },
    mix: function (a, b, k) { return a + (b - a) * k; },
    hasard: function (graine) {
      var s = graine >>> 0;
      return function () {
        s = (s + 0x6D2B79F5) >>> 0;
        var t = Math.imul(s ^ (s >>> 15), 1 | s);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    }
  };

  /* ── Les géométries. ── */
  function Geo() { this.p = []; this.n = []; this.uv = []; this.i = []; }
  Geo.prototype.sommet = function (x, y, z, nx, ny, nz, u, v) {
    this.p.push(x, y, z); this.n.push(nx, ny, nz); this.uv.push(u, v); return this.p.length / 3 - 1;
  };
  Geo.prototype.normales = function () {
    var n = new Float32Array(this.p.length), p = this.p, i = this.i;
    for (var k = 0; k < i.length; k += 3) {
      var a = i[k] * 3, b = i[k + 1] * 3, c = i[k + 2] * 3;
      var f = croix([p[b] - p[a], p[b + 1] - p[a + 1], p[b + 2] - p[a + 2]], [p[c] - p[a], p[c + 1] - p[a + 1], p[c + 2] - p[a + 2]]);
      for (var j = 0; j < 3; j++) { var q = i[k + j] * 3; n[q] += f[0]; n[q + 1] += f[1]; n[q + 2] += f[2]; }
    }
    for (var q2 = 0; q2 < n.length; q2 += 3) { var u = norm([n[q2], n[q2 + 1], n[q2 + 2]]); n[q2] = u[0]; n[q2 + 1] = u[1]; n[q2 + 2] = u[2]; }
    this.n = Array.prototype.slice.call(n);
    return this;
  };
  var G = {
    plan: function (w, h, nx, nz, f) {
      var g = new Geo();
      for (var j = 0; j <= nz; j++) for (var i = 0; i <= nx; i++) {
        var x = (i / nx - 0.5) * w, z = (j / nz - 0.5) * h;
        g.sommet(x, f ? f(x, z) : 0, z, 0, 1, 0, i / nx, j / nz);
      }
      for (j = 0; j < nz; j++) for (i = 0; i < nx; i++) {
        var a = j * (nx + 1) + i, b = a + 1, c = a + nx + 1, d = c + 1;
        g.i.push(a, c, b, b, c, d);
      }
      return f ? g.normales() : g;
    },
    /* Une feuille qui se COURBE : un triangle (base de largeur b sur la charnière, pointe à h), en n bandes le long
       de z. Le nuanceur la plie (`pli`) : elle se soulève et s'enroule comme du vrai papier. */
    feuille: function (b, h, n, base, ep) {
      var g = new Geo(), m = n || 12, y = ep || 0;
      for (var j = 0; j <= m; j++) {
        var z = (j / m) * h, w = base === "rect" ? b / 2 : (b / 2) * (1 - j / m);
        g.sommet(-w, y, z, 0, 1, 0, 0.5 - w / b, j / m);
        g.sommet(w, y, z, 0, 1, 0, 0.5 + w / b, j / m);
      }
      for (j = 0; j < m; j++) { var a = j * 2; g.i.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
      return g;
    },
    extrusion: function (contour, ep, biseau, pas) {
      var g = new Geo(), n = contour.length, b = biseau || 0, k = pas || 3, cx = 0, cz = 0, aire = 0, j, i;
      for (i = 0; i < n; i++) { cx += contour[i][0] / n; cz += contour[i][1] / n; var q = contour[(i + 1) % n]; aire += contour[i][0] * q[1] - q[0] * contour[i][1]; }
      var sens = aire > 0 ? 1 : -1;
      var dehors = contour.map(function (pp, i2) {
        var a = contour[(i2 - 1 + n) % n], c = contour[(i2 + 1) % n];
        var e1 = norm([pp[0] - a[0], 0, pp[1] - a[1]]), e2 = norm([c[0] - pp[0], 0, c[1] - pp[1]]);
        var m = norm([e1[2] + e2[2], 0, -(e1[0] + e2[0])]);
        return [m[0] * sens, m[2] * sens];
      });
      var anneaux = [];
      for (j = 0; j <= k; j++) { var a1 = (j / k) * Math.PI / 2; anneaux.push([b * (1 - Math.cos(a1)), b * Math.sin(a1)]); }
      var profil = anneaux.map(function (r) { return [-r[0], r[1]]; })
        .concat(anneaux.slice().reverse().map(function (r) { return [-r[0], ep - r[1]]; }));
      var base = g.p.length / 3;
      profil.forEach(function (pr, pi) {
        var ny = pi < profil.length / 2 ? -(1 - pi / (profil.length / 2)) : (pi - profil.length / 2 + 1) / (profil.length / 2);
        for (i = 0; i <= n; i++) {
          var c2 = contour[i % n], d = dehors[i % n], hh = Math.sqrt(Math.max(0, 1 - ny * ny));
          g.sommet(c2[0] + d[0] * (b + pr[0]), pr[1], c2[1] + d[1] * (b + pr[0]), d[0] * hh, ny, d[1] * hh, i / n, pi / (profil.length - 1));
        }
      });
      for (j = 0; j < profil.length - 1; j++) for (i = 0; i < n; i++) {
        var a2 = base + j * (n + 1) + i, b2 = a2 + 1, c3 = a2 + n + 1, d2 = c3 + 1;
        if (sens > 0) g.i.push(a2, b2, c3, b2, d2, c3); else g.i.push(a2, c3, b2, b2, c3, d2);
      }
      [[0, -1], [ep, 1]].forEach(function (f) {
        var centre = g.sommet(cx, f[0], cz, 0, f[1], 0, 0.5 + cx * 0.5, 0.5 + cz * 0.5);
        var bord = g.p.length / 3;
        for (i = 0; i < n; i++) g.sommet(contour[i][0], f[0], contour[i][1], 0, f[1], 0, 0.5 + contour[i][0] * 0.5, 0.5 + contour[i][1] * 0.5);
        for (i = 0; i < n; i++) {
          var u = bord + i, v = bord + (i + 1) % n;
          if ((f[1] > 0) === (sens > 0)) g.i.push(centre, v, u); else g.i.push(centre, u, v);
        }
      });
      return g;
    },
    sphere: function (r, n) {
      var g = new Geo(), m = n || 16;
      for (var j = 0; j <= m; j++) for (var i = 0; i <= m * 2; i++) {
        var th = (j / m) * Math.PI, ph = (i / (m * 2)) * Math.PI * 2;
        var x = Math.sin(th) * Math.cos(ph), y = Math.cos(th), z = Math.sin(th) * Math.sin(ph);
        g.sommet(x * r, y * r, z * r, x, y, z, i / (m * 2), j / m);
      }
      for (j = 0; j < m; j++) for (i = 0; i < m * 2; i++) {
        var a = j * (m * 2 + 1) + i, b = a + 1, c = a + m * 2 + 1, d = c + 1;
        g.i.push(a, b, c, b, d, c);
      }
      return g;
    },
    tore: function (R, r, n1, n2) {
      var g = new Geo();
      for (var j = 0; j <= n1; j++) for (var i = 0; i <= n2; i++) {
        var u = (j / n1) * Math.PI * 2, v = (i / n2) * Math.PI * 2;
        var cx = Math.cos(u), cz = Math.sin(u), nx = Math.cos(v) * cx, ny = Math.sin(v), nz = Math.cos(v) * cz;
        g.sommet(cx * R + nx * r, ny * r, cz * R + nz * r, nx, ny, nz, j / n1, i / n2);
      }
      for (j = 0; j < n1; j++) for (i = 0; i < n2; i++) {
        var a = j * (n2 + 1) + i, b = a + 1, c = a + n2 + 1, d = c + 1;
        g.i.push(a, c, b, b, c, d);
      }
      return g;
    },
    tour: function (profil, n) {
      var g = new Geo(), m = n || 24;
      for (var j = 0; j < profil.length; j++) for (var i = 0; i <= m; i++) {
        var a = (i / m) * Math.PI * 2, r = profil[j][0];
        g.sommet(Math.cos(a) * r, profil[j][1], Math.sin(a) * r, Math.cos(a), 0, Math.sin(a), i / m, j / (profil.length - 1));
      }
      for (j = 0; j < profil.length - 1; j++) for (i = 0; i < m; i++) {
        var a2 = j * (m + 1) + i, b = a2 + 1, c = a2 + m + 1, d = c + 1;
        g.i.push(a2, c, b, b, c, d);
      }
      return g.normales();
    }
  };

  /* ── Les nuanceurs des objets. ── */
  var VS = "attribute vec3 a_p;attribute vec3 a_n;attribute vec2 a_uv;uniform mat4 u_pv,u_v,u_m;uniform mat3 u_vn;uniform vec3 u_pli;" +
    "varying vec3 v_n,v_e,v_w;varying vec2 v_uv;" +
    "void main(){vec3 p=a_p,n=a_n;" +
    /* le pli : la feuille tourne autour de sa charnière (angle de base) ET s'enroule (courbure) le long de z */
    "if(u_pli.z>.5){float s=p.z,th=u_pli.x,k=u_pli.y,a=th+k*s,cy,cz;" +
    "if(abs(k)<.001){cy=s*sin(th);cz=s*cos(th);}else{cy=(cos(th)-cos(a))/k;cz=(sin(a)-sin(th))/k;}" +
    "vec3 nn=vec3(0.,cos(a),-sin(a));p=vec3(p.x,cy,cz)+nn*p.y;n=normalize(vec3(n.x,0.,0.)+nn*n.y+vec3(0.,sin(a),cos(a))*n.z);}" +
    "vec4 w=u_m*vec4(p,1.);v_w=w.xyz;v_e=(u_v*w).xyz;v_n=u_vn*n;v_uv=a_uv;gl_Position=u_pv*w;}";
  function FS(derive) {
    return (derive ? "#extension GL_OES_standard_derivatives : enable\n" : "") +
      "precision mediump float;uniform float u_mode,u_bump,u_brume,u_coupe,u_metal;uniform sampler2D u_tex,u_haut;uniform vec4 u_teinte;" +
      "uniform vec3 u_emis,u_lum,u_lumc,u_lp,u_lpc,u_amb,u_rim;uniform vec2 u_rep,u_spec;varying vec3 v_n,v_e,v_w;varying vec2 v_uv;" +
      (derive ?
        "vec3 relief(vec3 n){vec3 dx=dFdx(v_e),dy=dFdy(v_e);float h=texture2D(u_haut,v_uv*u_rep).r;" +
        "float hx=dFdx(h),hy=dFdy(h);vec3 r1=cross(dy,n),r2=cross(n,dx);float d=dot(dx,r1);" +
        "return normalize(abs(d)*n-u_bump*sign(d)*(hx*r1+hy*r2));}" : "vec3 relief(vec3 n){return n;}") +
      "void main(){vec3 n=normalize(v_n);if(!gl_FrontFacing)n=-n;if(u_bump>0.)n=relief(n);vec4 c;vec3 e=normalize(v_e);" +
      /* 0 · matcap : la sphère de Blender, lue par le reflet (tient compte de la perspective) */
      "if(u_mode<.5){vec3 r=reflect(e,n);float m=2.8284*sqrt(r.z+1.001);" +
      "c=vec4(texture2D(u_tex,r.xy/m*.96+.5).rgb*u_teinte.rgb,u_teinte.a);}" +
      /* 1 · papier : la clé enveloppante, la lumière ponctuelle, et le reflet doux qui glisse sur la feuille ;
         là où la hauteur porte du vert (`u_metal`), c'est une feuille d'or : sombre de face, éclatante sous le reflet */
      "else if(u_mode<1.5){vec4 a=texture2D(u_tex,v_uv*u_rep)*u_teinte;float w=max((dot(n,u_lum)+.3)/1.3,0.);" +
      "vec3 d=u_lp-v_w;float l2=dot(d,d);float pl=max(dot(n,normalize(d)),0.)/(1.+l2*.7);" +
      "float mt=u_metal*texture2D(u_haut,v_uv*u_rep).g,hv=max(dot(n,normalize(u_lum-e)),0.);" +
      "float sp=pow(hv,mix(u_spec.y,70.,mt))*mix(u_spec.x,2.4,mt)+mt*pow(hv,6.)*.35;" +
      "vec3 df=a.rgb*(u_amb+u_lumc*w+u_lpc*pl);" +
      "float hp=max(dot(n,normalize(normalize(d)-e)),0.),spp=pow(hp,mix(u_spec.y,70.,mt))*mix(u_spec.x,2.4,mt)*2./(1.+l2*.7);" +
      "c=vec4(mix(df,df*.7+a.rgb*u_lpc*pl*.9,mt)+sp*mix(u_lumc,a.rgb*u_lumc*1.7,mt)+spp*u_lpc*mix(vec3(1.),a.rgb*1.7,mt)" +
      "+mt*a.rgb*pow(1.-abs(dot(n,e)),2.)*.35,a.a);}" +
      "else{c=texture2D(u_tex,v_uv*u_rep)*u_teinte;}" +
      /* le liseré : une lumière froide qui dessine les bords contre la lumière chaude (le regard du cinéma) */
      "if(c.a<u_coupe)discard;c.rgb+=u_emis+u_rim*pow(1.-abs(dot(n,e)),3.)*c.a;c.rgb=mix(c.rgb,vec3(.031,.024,.043),u_brume*clamp(-v_e.z*.06-.2,0.,1.));" +
      "gl_FragColor=vec4(c.rgb*c.a,c.a);}";
  }
  var VS2 = "attribute vec3 a_p;attribute vec2 a_uv;attribute vec4 a_c;uniform mat4 u_pv;varying vec2 v_uv;varying vec4 v_c;" +
    "void main(){v_uv=a_uv;v_c=a_c;gl_Position=u_pv*vec4(a_p,1.);}";
  var FS2 = "precision mediump float;uniform sampler2D u_tex;uniform float u_add;varying vec2 v_uv;varying vec4 v_c;" +
    "void main(){vec4 t=texture2D(u_tex,v_uv);float a=t.a*v_c.a;gl_FragColor=vec4(t.rgb*v_c.rgb*a,a*(1.-u_add));}";

  /* ── Les nuanceurs de l'image finale (le « post-traitement »). Un triangle qui couvre l'écran. ── */
  var VSQ = "attribute vec2 a_p;varying vec2 v_uv;void main(){v_uv=a_p*.5+.5;gl_Position=vec4(a_p,0.,1.);}";
  /* réduire l'image au quart (4 lectures), et ne garder que ce qui brille pour le halo */
  var FS_RED = "precision mediump float;uniform sampler2D u_tex;uniform vec2 u_px;uniform float u_seuil;varying vec2 v_uv;" +
    "void main(){vec4 c=(texture2D(u_tex,v_uv+u_px*vec2(-1.,-1.))+texture2D(u_tex,v_uv+u_px*vec2(1.,-1.))+" +
    "texture2D(u_tex,v_uv+u_px*vec2(-1.,1.))+texture2D(u_tex,v_uv+u_px*vec2(1.,1.)))*.25;" +
    "if(u_seuil>0.){float l=max(c.r,max(c.g,c.b));c.rgb*=smoothstep(u_seuil,u_seuil+.25,l);}gl_FragColor=c;}";
  /* un flou gaussien séparable, 9 points en 5 lectures (filtrage linéaire) */
  var FS_FLOU = "precision mediump float;uniform sampler2D u_tex;uniform vec2 u_dir;varying vec2 v_uv;" +
    "void main(){vec4 c=texture2D(u_tex,v_uv)*.227027;" +
    "c+=(texture2D(u_tex,v_uv+u_dir*1.384615)+texture2D(u_tex,v_uv-u_dir*1.384615))*.316216;" +
    "c+=(texture2D(u_tex,v_uv+u_dir*3.230769)+texture2D(u_tex,v_uv-u_dir*3.230769))*.070270;" +
    "gl_FragColor=c;}";
  /* l'image finale : lissage FXAA, profondeur de champ, halo, vignetage, courbe de couleur, grain */
  var FS_FIN = "precision mediump float;uniform sampler2D u_scene,u_halo,u_flou;uniform vec2 u_px;" +
    "uniform float u_bloom,u_dof,u_foyer,u_largeur,u_vign,u_grain,u_t,u_alpha;varying vec2 v_uv;" +
    "vec3 fxaa(vec2 uv){vec3 l3=vec3(.299,.587,.114);" +
    "vec3 nw=texture2D(u_scene,uv+vec2(-1.,-1.)*u_px).rgb,ne=texture2D(u_scene,uv+vec2(1.,-1.)*u_px).rgb," +
    "sw=texture2D(u_scene,uv+vec2(-1.,1.)*u_px).rgb,se=texture2D(u_scene,uv+vec2(1.,1.)*u_px).rgb,m=texture2D(u_scene,uv).rgb;" +
    "float a=dot(nw,l3),b=dot(ne,l3),c=dot(sw,l3),d=dot(se,l3),e=dot(m,l3);" +
    "float lo=min(e,min(min(a,b),min(c,d))),hi=max(e,max(max(a,b),max(c,d)));" +
    "vec2 dir=vec2(-((a+b)-(c+d)),((a+c)-(b+d)));float red=max((a+b+c+d)*.03125,.0078125);" +
    "dir=clamp(dir/(min(abs(dir.x),abs(dir.y))+red),-8.,8.)*u_px;" +
    "vec3 p=.5*(texture2D(u_scene,uv-dir*.1667).rgb+texture2D(u_scene,uv+dir*.1667).rgb);" +
    "vec3 q=p*.5+.25*(texture2D(u_scene,uv-dir*.5).rgb+texture2D(u_scene,uv+dir*.5).rgb);" +
    "float lq=dot(q,l3);return (lq<lo||lq>hi)?p:q;}" +
    "void main(){vec3 c=fxaa(v_uv);float a=texture2D(u_scene,v_uv).a;" +
    "float k=smoothstep(u_largeur,u_largeur+.3,abs(v_uv.y-u_foyer))*u_dof;vec4 fl=texture2D(u_flou,v_uv);c=mix(c,fl.rgb,k);a=mix(a,fl.a,k);" +
    "c+=texture2D(u_halo,v_uv).rgb*u_bloom;float A=mix(1.,a,u_alpha);" +
    "vec2 v=v_uv-.5;c*=1.-u_vign*dot(v,v)*1.7*A;" +
    /* une courbe en S douce, les noirs vers l'encre de nuit, les hautes lumières un rien dorées */
    "c=mix(c,c*c*(3.-2.*c),.22);c=c*vec3(1.02,1.,.97)+vec3(.012,.008,.018)*(1.-c)*A;" +
    "c+=(fract(sin(dot(v_uv*(1.+u_t),vec2(12.9898,78.233)))*43758.5453)-.5)*u_grain*A;" +
    /* en fenêtre (`transparent`), la page se voit là où il n'y a rien ; la lumière d'un halo la voile à peine
       (une couleur prémultipliée ne dépasse jamais son alpha) */
    "c=max(c,0.);float ao=mix(1.,clamp(max(a,max(c.r,max(c.g,c.b))),0.,1.),u_alpha);gl_FragColor=vec4(min(c,vec3(ao)),ao);}";

  function Theatre(canvas, options) {
    var o = options || {};
    var gl = canvas.getContext("webgl", { antialias: true, alpha: !!o.transparent, premultipliedAlpha: true, preserveDrawingBuffer: !!o.garder }) ||
      canvas.getContext("experimental-webgl", { alpha: !!o.transparent });
    if (!gl) return null;
    var derive = !!gl.getExtension("OES_standard_derivatives");
    var aniso = gl.getExtension("EXT_texture_filter_anisotropic") || gl.getExtension("WEBKIT_EXT_texture_filter_anisotropic");
    var S = { gl: gl, M: M, C: C, G: G, k: 1, W: 1, H: 1, pret: true, attente: 0, transparent: !!o.transparent,
      /* la qualité : 2 = cinéma (sur-échantillonnage, halo, flou), 1 = sans flou ni sur-échantillonnage, 0 = image directe */
      qualite: o.qualite == null ? 2 : o.qualite,
      post: { bloom: 0.6, seuil: 0.86, dof: 0.8, foyer: 0.5, largeur: 0.12, vign: 0.42, grain: 0.02 } };

    function programme(vs, fs) {
      function shader(type, src) {
        var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
        if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
        return s;
      }
      var p = gl.createProgram();
      gl.attachShader(p, shader(gl.VERTEX_SHADER, vs)); gl.attachShader(p, shader(gl.FRAGMENT_SHADER, fs));
      gl.linkProgram(p);
      if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
      var u = {}, n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
      for (var i = 0; i < n; i++) { var nom = gl.getActiveUniform(p, i).name; u[nom] = gl.getUniformLocation(p, nom); }
      return { p: p, u: u, a: { p: gl.getAttribLocation(p, "a_p"), n: gl.getAttribLocation(p, "a_n"), uv: gl.getAttribLocation(p, "a_uv"), c: gl.getAttribLocation(p, "a_c") } };
    }
    var P1 = programme(VS, FS(derive)), P2 = programme(VS2, FS2);
    var PR = programme(VSQ, FS_RED), PF = programme(VSQ, FS_FLOU), PZ = programme(VSQ, FS_FIN);
    var tri = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, tri); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

    /* ── les textures ── */
    function poser(tex, src, repete) {
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
      var p2 = (src.width & (src.width - 1)) === 0 && (src.height & (src.height - 1)) === 0;
      if (p2) { gl.generateMipmap(gl.TEXTURE_2D); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); }
      else gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      var w = p2 && repete ? gl.REPEAT : gl.CLAMP_TO_EDGE;
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, w); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, w);
      /* vue de biais (la table, le papier couché), une texture reste nette avec le filtrage anisotrope */
      if (aniso && p2) gl.texParameterf(gl.TEXTURE_2D, aniso.TEXTURE_MAX_ANISOTROPY_EXT, Math.min(8, gl.getParameter(aniso.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));
    }
    S.toile = function (w, h, dessin, repete) {
      var c = document.createElement("canvas"); c.width = w; c.height = h;
      dessin(c.getContext("2d"), w, h);
      var t = gl.createTexture(); poser(t, c, repete); t.toile = c; return t;
    };
    S.image = function (src) {
      var t = gl.createTexture(), im = new Image();
      poser(t, (function () { var c = document.createElement("canvas"); c.width = c.height = 1; return c; })(), false);
      S.attente++; S.pret = false;
      im.onload = function () { poser(t, im, false); if (--S.attente === 0) { S.pret = true; } };
      im.onerror = function () { if (--S.attente === 0) { S.pret = true; } };
      im.src = src;
      return t;
    };
    S.rond = S.toile(64, 64, function (g) {
      var r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(0.35, "rgba(255,255,255,.5)"); r.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = r; g.fillRect(0, 0, 64, 64);
    });
    var blanc = S.toile(4, 4, function (g) { g.fillStyle = "#fff"; g.fillRect(0, 0, 4, 4); });
    S.blanc = blanc;

    /* ── les maillages ── */
    S.maillage = function (g) {
      var m = { n: g.i.length, b: [] };
      [[g.p, 3], [g.n, 3], [g.uv, 2]].forEach(function (d) {
        var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(d[0]), gl.STATIC_DRAW); m.b.push(b);
      });
      m.i = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, m.i);
      gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(g.i), gl.STATIC_DRAW);
      return m;
    };

    /* ── les images hors écran : la scène, et les quarts pour le halo et le flou ── */
    function cible(w, h, profondeur) {
      var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      var f = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, f);
      gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0);
      var r = null;
      if (profondeur) {
        /* ⚠️ DEPTH_STENCIL, pas DEPTH_COMPONENT16 : à 16 bits, deux feuilles à 2 mm se battaient (la doublure du rabat
           transparaissait au repos) ; le format profondeur + gabarit donne 24 bits partout en WebGL 1 */
        r = gl.createRenderbuffer(); gl.bindRenderbuffer(gl.RENDERBUFFER, r);
        gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH_STENCIL, w, h);
        gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_STENCIL_ATTACHMENT, gl.RENDERBUFFER, r);
      }
      var ok = gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE;
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      return { t: t, f: f, r: r, w: w, h: h, ok: ok };
    }
    function liberer(c) { if (!c) return; gl.deleteTexture(c.t); gl.deleteFramebuffer(c.f); if (c.r) gl.deleteRenderbuffer(c.r); }
    var FB = {};
    function cibles() {
      ["scene", "q1", "q2", "f1", "f2"].forEach(function (k) { liberer(FB[k]); FB[k] = null; });
      if (S.qualite < 1) return;
      /* sur un écran d'ordinateur (densité 1), la scène est calculée une fois et demie plus grande : l'escalier
         des bords disparaît à la réduction ; sur un téléphone (densité 2 ou 3), la densité suffit */
      var sur = S.qualite >= 2 ? Math.max(1, Math.min(1.5, 1.6 / S.k)) : 1;
      var w = Math.round(canvas.width * sur), h = Math.round(canvas.height * sur);
      var max = gl.getParameter(gl.MAX_RENDERBUFFER_SIZE);
      if (w > max || h > max) { var r = max / Math.max(w, h); w = Math.floor(w * r); h = Math.floor(h * r); }
      FB.scene = cible(w, h, true);
      var qw = Math.max(2, Math.round(canvas.width / 4)), qh = Math.max(2, Math.round(canvas.height / 4));
      FB.q1 = cible(qw, qh); FB.q2 = cible(qw, qh); FB.f1 = cible(qw, qh); FB.f2 = cible(qw, qh);
      if (!FB.scene.ok || !FB.q1.ok) { S.qualite = 0; cibles(); }
    }

    /* ── la taille, la caméra cadrée sur un rectangle de la page ── */
    var V = M.id(), PV = M.id();
    S.taille = function () {
      var k = Math.min(window.devicePixelRatio || 1, o.kmax || 2);
      var w = canvas.clientWidth || window.innerWidth, h = canvas.clientHeight || window.innerHeight;
      S.k = k; S.W = w; S.H = h;
      canvas.width = Math.round(w * k); canvas.height = Math.round(h * k);
      cibles();
    };
    S.taille();
    S.camera = function (oeil, cible2, champ, ecranX, ecranY) {
      V = M.vise(oeil, cible2, [0, 1, 0]);
      var P = M.persp((champ || 32) * Math.PI / 180, S.W / S.H, 0.3, 60);
      if (ecranX != null) { P[8] = -((ecranX / S.W) * 2 - 1); P[9] = -(1 - (ecranY / S.H) * 2); }
      PV = M.mul(P, V);
      S.V = V; S.PV = PV; S.oeil = oeil;
      /* le foyer de la profondeur de champ suit l'objet visé : là où tombe la cible à l'écran */
      if (ecranY != null) S.post.foyer = 1 - ecranY / S.H;
    };
    S.distance = function (l, px, champ) {
      return (l * S.H) / (2 * px * Math.tan((champ || 32) * Math.PI / 360));
    };

    /* ── la lumière ── */
    var L = { lum: norm([-0.5, 0.8, 0.6]), lumc: [1.0, 0.86, 0.68], amb: [0.16, 0.13, 0.18], lp: [0, 1, 0], lpc: [0, 0, 0], brume: 0, rim: [0.12, 0.14, 0.2] };
    S.lumiere = function (o2) { for (var c in o2) L[c] = o2[c]; };

    /* ── commencer une image : dans la scène hors écran (ou l'écran, sans post-traitement) ── */
    S.effacer = function () {
      if (FB.scene) { gl.bindFramebuffer(gl.FRAMEBUFFER, FB.scene.f); gl.viewport(0, 0, FB.scene.w, FB.scene.h); }
      else { gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, canvas.width, canvas.height); }
      if (S.transparent) gl.clearColor(0, 0, 0, 0); else gl.clearColor(0.07, 0.055, 0.09, 1);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.disable(gl.CULL_FACE);
    };

    /* matiere : {mode: "matcap"|"papier"|"plat", tex, teinte, haut, bump, rep, emis, coupe, spec:[force, dureté], pli:[angle, courbure],
       metal (0 → 1 : le vert de `haut` devient une feuille d'or)} */
    S.dessiner = function (mesh, mat, m) {
      var P = P1, u = P.u;
      gl.useProgram(P.p);
      var vm = M.mul(V, m), ln = mulDir(V, L.lum);
      gl.uniformMatrix4fv(u.u_pv, false, PV); gl.uniformMatrix4fv(u.u_v, false, V); gl.uniformMatrix4fv(u.u_m, false, m);
      gl.uniformMatrix3fv(u.u_vn, false, M.coin(vm));
      gl.uniform1f(u.u_mode, mat.mode === "papier" ? 1 : mat.mode === "plat" ? 2 : 0);
      var te = mat.teinte || [1, 1, 1, 1];
      gl.uniform4f(u.u_teinte, te[0], te[1], te[2], te[3] == null ? 1 : te[3]);
      var em = mat.emis || [0, 0, 0]; gl.uniform3f(u.u_emis, em[0], em[1], em[2]);
      gl.uniform3f(u.u_lum, ln[0], ln[1], ln[2]); gl.uniform3fv(u.u_lumc, L.lumc); gl.uniform3fv(u.u_amb, L.amb);
      gl.uniform3fv(u.u_lp, L.lp); gl.uniform3fv(u.u_lpc, L.lpc); gl.uniform1f(u.u_brume, L.brume);
      var rim = mat.rim || L.rim; gl.uniform3f(u.u_rim, rim[0], rim[1], rim[2]);
      var rep = mat.rep || [1, 1]; gl.uniform2f(u.u_rep, rep[0], rep[1]);
      var sp = mat.spec || (mat.mode === "papier" ? [0.07, 18] : [0, 1]); gl.uniform2f(u.u_spec, sp[0], sp[1]);
      gl.uniform1f(u.u_bump, derive && mat.haut ? (mat.bump || 1) : 0);
      gl.uniform1f(u.u_coupe, mat.coupe || 0); gl.uniform1f(u.u_metal, mat.haut ? mat.metal || 0 : 0);
      var pl = mat.pli; gl.uniform3f(u.u_pli, pl ? pl[0] : 0, pl ? pl[1] || 0 : 0, pl ? 1 : 0);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, mat.tex || blanc); gl.uniform1i(u.u_tex, 0);
      gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, mat.haut || blanc); gl.uniform1i(u.u_haut, 1);
      var tr = te[3] != null && te[3] < 1;
      if (tr || mat.fondu) { gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(!mat.fondu); }
      else { gl.disable(gl.BLEND); gl.depthMask(true); }
      lier(mesh, P);
      gl.drawElements(gl.TRIANGLES, mesh.n, gl.UNSIGNED_SHORT, 0);
      gl.depthMask(true);
    };
    function lier(mesh, P) {
      [[P.a.p, 3], [P.a.n, 3], [P.a.uv, 2]].forEach(function (a, i) {
        if (a[0] < 0) return;
        gl.bindBuffer(gl.ARRAY_BUFFER, mesh.b[i]); gl.enableVertexAttribArray(a[0]);
        gl.vertexAttribPointer(a[0], a[1], gl.FLOAT, false, 0, 0);
      });
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, mesh.i);
    }
    function mulDir(m, d) { return norm([m[0] * d[0] + m[4] * d[1] + m[8] * d[2], m[1] * d[0] + m[5] * d[1] + m[9] * d[2], m[2] * d[0] + m[6] * d[1] + m[10] * d[2]]); }

    /* ── les lutins : un tampon réutilisé (aucune mémoire jetée à chaque image : pas de saccade du ramasse-miettes) ── */
    var tamponL = gl.createBuffer(), indL = gl.createBuffer(), maxL = 0, donneesL = new Float32Array(0);
    S.lutins = function (liste, tex, additif) {
      if (!liste.length) return;
      var n = liste.length;
      if (n > maxL) {
        maxL = Math.max(n, maxL * 2, 64); var ix = new Uint16Array(maxL * 6);
        for (var q = 0; q < maxL; q++) { ix.set([q * 4, q * 4 + 1, q * 4 + 2, q * 4 + 2, q * 4 + 1, q * 4 + 3], q * 6); }
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indL); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, ix, gl.STATIC_DRAW);
        donneesL = new Float32Array(maxL * 4 * 9);
        gl.bindBuffer(gl.ARRAY_BUFFER, tamponL); gl.bufferData(gl.ARRAY_BUFFER, donneesL.byteLength, gl.DYNAMIC_DRAW);
      }
      var d = donneesL, dx = [V[0], V[4], V[8]], dy = [V[1], V[5], V[9]];
      for (var q2 = 0; q2 < n; q2++) {
        var l = liste[q2], s = l.s / 2, ax = l.ax || dx, ay = l.ay || dy, c = Math.cos(l.r || 0), sn = Math.sin(l.r || 0), uv = l.u || UV1, h = l.h || 1;
        var X0 = (ax[0] * c + ay[0] * sn) * s, X1 = (ax[1] * c + ay[1] * sn) * s, X2 = (ax[2] * c + ay[2] * sn) * s;
        var Y0 = (ay[0] * c - ax[0] * sn) * s * h, Y1 = (ay[1] * c - ax[1] * sn) * s * h, Y2 = (ay[2] * c - ax[2] * sn) * s * h;
        var a = l.c[3] == null ? 1 : l.c[3];
        for (var v = 0; v < 4; v++) {
          var kx = v & 1 ? 1 : -1, ky = v & 2 ? 1 : -1, o2 = (q2 * 4 + v) * 9;
          d[o2] = l.p[0] + X0 * kx + Y0 * ky; d[o2 + 1] = l.p[1] + X1 * kx + Y1 * ky; d[o2 + 2] = l.p[2] + X2 * kx + Y2 * ky;
          d[o2 + 3] = kx < 0 ? uv[0] : uv[2]; d[o2 + 4] = ky < 0 ? uv[3] : uv[1];
          d[o2 + 5] = l.c[0]; d[o2 + 6] = l.c[1]; d[o2 + 7] = l.c[2]; d[o2 + 8] = a;
        }
      }
      var P = P2;
      gl.useProgram(P.p);
      gl.uniformMatrix4fv(P.u.u_pv, false, PV); gl.uniform1f(P.u.u_add, additif ? 1 : 0);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex || S.rond); gl.uniform1i(P.u.u_tex, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, tamponL); gl.bufferSubData(gl.ARRAY_BUFFER, 0, d.subarray(0, n * 36));
      gl.enableVertexAttribArray(P.a.p); gl.vertexAttribPointer(P.a.p, 3, gl.FLOAT, false, 36, 0);
      gl.enableVertexAttribArray(P.a.uv); gl.vertexAttribPointer(P.a.uv, 2, gl.FLOAT, false, 36, 12);
      gl.enableVertexAttribArray(P.a.c); gl.vertexAttribPointer(P.a.c, 4, gl.FLOAT, false, 36, 20);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indL);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, additif ? gl.ONE : gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false);
      gl.drawElements(gl.TRIANGLES, n * 6, gl.UNSIGNED_SHORT, 0);
      gl.depthMask(true); gl.disableVertexAttribArray(P.a.c);
    };
    var UV1 = [0, 0, 1, 1];
    S.ombre = function (x, y, z, rx, rz, force, rot) {
      S.lutins([{ p: [x, y + 0.002, z], s: rx * 2, h: rz / rx, r: rot || 0, ax: [1, 0, 0], ay: [0, 0, 1], c: [0.02, 0.01, 0.03, force] }], S.rond, false);
    };

    /* ── finir l'image : le post-traitement, de la scène hors écran à l'écran ── */
    function passe(P, sortie, w, h) {
      gl.bindFramebuffer(gl.FRAMEBUFFER, sortie ? sortie.f : null);
      gl.viewport(0, 0, w, h);
      gl.useProgram(P.p);
      gl.bindBuffer(gl.ARRAY_BUFFER, tri); gl.enableVertexAttribArray(P.a.p); gl.vertexAttribPointer(P.a.p, 2, gl.FLOAT, false, 0, 0);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    function lireTex(P, nom, unite, t) { gl.activeTexture(gl.TEXTURE0 + unite); gl.bindTexture(gl.TEXTURE_2D, t); gl.uniform1i(P.u[nom], unite); }
    S.composer = function (temps) {
      if (!FB.scene) return;
      gl.disable(gl.DEPTH_TEST); gl.disable(gl.BLEND); gl.depthMask(true);
      var q = FB.q1, R = PR, F = PF, Z = PZ, sw = FB.scene.w, sh = FB.scene.h;
      /* 1 · le quart de l'image (tel quel), pour le flou de la profondeur de champ */
      gl.useProgram(R.p); lireTex(R, "u_tex", 0, FB.scene.t); gl.uniform2f(R.u.u_px, 1.5 / sw, 1.5 / sh); gl.uniform1f(R.u.u_seuil, 0);
      passe(R, FB.f1, q.w, q.h);
      /* 2 · ce qui brille, pour le halo */
      gl.useProgram(R.p); lireTex(R, "u_tex", 0, FB.scene.t); gl.uniform2f(R.u.u_px, 1.5 / sw, 1.5 / sh); gl.uniform1f(R.u.u_seuil, S.post.seuil);
      passe(R, FB.q1, q.w, q.h);
      /* 3 · les flous (deux passes chacun : horizontal, vertical) */
      var flou = function (de, vers, dx, dy) { gl.useProgram(F.p); lireTex(F, "u_tex", 0, de.t); gl.uniform2f(F.u.u_dir, dx / q.w, dy / q.h); passe(F, vers, q.w, q.h); };
      flou(FB.q1, FB.q2, 1.4, 0); flou(FB.q2, FB.q1, 0, 1.4); flou(FB.q1, FB.q2, 2.6, 0); flou(FB.q2, FB.q1, 0, 2.6);
      if (S.qualite >= 2) { flou(FB.f1, FB.f2, 1.2, 0); flou(FB.f2, FB.f1, 0, 1.2); }
      /* 4 · l'image finale */
      gl.useProgram(Z.p);
      lireTex(Z, "u_scene", 0, FB.scene.t); lireTex(Z, "u_halo", 1, FB.q1.t); lireTex(Z, "u_flou", 2, FB.f1.t);
      var p = S.post;
      gl.uniform2f(Z.u.u_px, 1 / sw, 1 / sh);
      gl.uniform1f(Z.u.u_bloom, p.bloom); gl.uniform1f(Z.u.u_dof, S.qualite >= 2 ? p.dof : 0); gl.uniform1f(Z.u.u_foyer, p.foyer);
      gl.uniform1f(Z.u.u_largeur, p.largeur); gl.uniform1f(Z.u.u_vign, p.vign); gl.uniform1f(Z.u.u_grain, p.grain);
      gl.uniform1f(Z.u.u_t, (temps || 0) % 7); gl.uniform1f(Z.u.u_alpha, S.transparent ? 1 : 0);
      passe(Z, null, canvas.width, canvas.height);
    };
    /* baisser la qualité d'un palier (appelé par `jouer` quand l'appareil peine) */
    S.alleger = function () { if (S.qualite > 0) { S.qualite--; cibles(); return true; } return false; };
    return S;
  }

  /* ═══ La mise en scène : le théâtre joue un rite dans un canvas, puis rend la main.
     jouer(canvas, rite, D, {fin, abandon, fini}) → {ouvrir(), arreter(), fini(), toucher(e)}
     ─ 60 images par seconde, au repos comme pendant l'ouverture ; rien quand la page est cachée ;
     ─ si l'appareil peine (plus de 24 ms par image en moyenne), la qualité baisse d'un palier, deux au plus ;
     ─ un rite à geste (les portes qu'on écarte) décide lui-même : `revele(t)` vrai → la lettre se montre,
       `fini(t)` vrai → le théâtre s'arrête ; sinon, `revele` et `duree` sont des secondes ;
     ─ `plein` : le rite prend tout l'écran, en fenêtre (transparent : on voit la page derrière) ;
     ─ au moindre souci (pas de WebGL, une erreur), abandon() : la lettre s'ouvre comme avant. ═══ */
  function jouer(canvas, rite, D, rappels) {
    var S;
    try { S = Theatre(canvas, { kmax: rite.kmax || 2, transparent: !!rite.plein }); } catch (e) { S = null; }
    if (!S) { rappels.abandon && rappels.abandon(); return null; }
    try { rite.monter(S, D); } catch (e) { rappels.abandon && rappels.abandon(e); return null; }
    var t0 = 0, tOuvre = -1, fini = false, revele = false, dernier = 0, arret = false, somme = 0, compte = 0, repos = 0;
    function image(now) {
      if (arret) return;
      requestAnimationFrame(image);
      if (!t0) { t0 = now; dernier = now; }
      if (document.hidden) { dernier = now; return; }
      var dt = now - dernier; dernier = now;
      /* au repos depuis longtemps (une lettre peut attendre son heure des heures) : on économise la batterie */
      if (tOuvre < 0 && now - t0 > 90000 && ++repos % 4) return;
      if (!S.pret) return;
      if (dt > 0 && dt < 200) { somme += dt; compte++; }
      if (compte >= 45) { if (somme / compte > 24 && S.alleger()) { /* un palier de moins */ } somme = 0; compte = 0; }
      var t = tOuvre < 0 ? -1 : (now - tOuvre) / 1000, ti = (now - t0) / 1000;
      try { rite.rendre(S, t, ti); S.composer(ti); } catch (e) { arret = true; rappels.abandon && rappels.abandon(e); return; }
      if (tOuvre >= 0 && !revele && (typeof rite.revele === "function" ? rite.revele(t) : t >= (rite.revele || rite.duree))) { revele = true; rappels.fin && rappels.fin(); }
      if (tOuvre >= 0 && (typeof rite.fini === "function" ? rite.fini(t) : t >= rite.duree + 0.6)) { arret = true; fini = true; rappels.fini && rappels.fini(); }
    }
    requestAnimationFrame(image);
    addEventListener("resize", function () { S.taille(); });
    return {
      S: S,
      ouvrir: function () { if (tOuvre < 0) { tOuvre = performance.now(); rite.geste && rite.geste(S); } },
      arreter: function () { arret = true; },
      fini: function () { return fini; },
      /* le doigt : {type: "survol"|"bas"|"glisse"|"haut", x, y} en px de la page ; le rite le reçoit avec ses horloges */
      toucher: function (e) {
        if (arret || !rite.toucher) return;
        var now = performance.now();
        e.ti = t0 ? (now - t0) / 1000 : 0; e.t = tOuvre < 0 ? -1 : (now - tOuvre) / 1000;
        try { rite.toucher(S, e); } catch (x) { /* un geste mal compris ne casse jamais la lettre */ }
      }
    };
  }

  Theatre.jouer = jouer;
  Theatre.M = M; Theatre.C = C; Theatre.G = G;
  return Theatre;
})();
