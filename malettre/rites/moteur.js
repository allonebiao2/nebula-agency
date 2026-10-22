/* ═══════════════════════════════════════════════════════════════════════════
   MA LETTRE À… · LE THÉÂTRE DES OUVERTURES (2026-10-22)
   Un moteur 3D minuscule, WebGL 1, AUCUNE bibliothèque : une lettre doit
   s'ouvrir dans un taxi, sur un téléphone modeste.
   ─ La LUMIÈRE est calculée une fois pour toutes dans Blender (Cycles) : les
     « matcaps » (`rites/matieres/`, une sphère photographiée sous la lumière
     d'une chambre, le soir) donnent à la cire, à l'or, à la perle leur vrai
     reflet, pour le prix d'une texture de 128 px.
   ─ Tout bouge par le TEMPS (secondes), jamais par image : le même rite tourne
     dans la lettre et se filme image par image dans le studio (Remotion), et
     les deux sont identiques. Aucun Math.random : un tirage à graine (`hasard`).
   ─ Le moteur ne sait rien des occasions : chaque rite (`rites/<id>.js`) monte
     sa scène et la joue.
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
    /* Une chaîne de transformations, lue de gauche à droite : chaine(T, R, S) = T·R·S. */
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
    /* La matrice des normales (3×3) d'une matrice SANS échelle inégale : son coin. */
    coin: function (m) { return new Float32Array([m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]]); }
  };
  function sous(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function croix(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function pt(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function norm(a) { var l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }

  /* ── Les courbes et les petits outils du temps. ── */
  var C = {
    borne: function (x) { return x < 0 ? 0 : x > 1 ? 1 : x; },
    /* p(t, a, b) : 0 → 1 entre a et b. */
    p: function (t, a, b) { return C.borne((t - a) / (b - a)); },
    sort: function (x) { return 1 - Math.pow(1 - x, 4); },          /* décélère (quart) */
    doux: function (x) { return x * x * (3 - 2 * x); },             /* lisse aux deux bouts */
    entre: function (x) { return x * x * x; },                        /* accélère */
    mix: function (a, b, k) { return a + (b - a) * k; },
    /* un tirage à graine (mulberry32) : le même rite rejoue le même hasard */
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

  /* ── Les géométries : des listes de sommets, montées ensuite sur la carte. ── */
  function Geo() { this.p = []; this.n = []; this.uv = []; this.i = []; }
  Geo.prototype.sommet = function (x, y, z, nx, ny, nz, u, v) {
    this.p.push(x, y, z); this.n.push(nx, ny, nz); this.uv.push(u, v); return this.p.length / 3 - 1;
  };
  /* Les normales recalculées depuis les faces (pour une surface déformée). */
  Geo.prototype.normales = function () {
    var n = new Float32Array(this.p.length), p = this.p, i = this.i;
    for (var k = 0; k < i.length; k += 3) {
      var a = i[k] * 3, b = i[k + 1] * 3, c = i[k + 2] * 3;
      var e1 = [p[b] - p[a], p[b + 1] - p[a + 1], p[b + 2] - p[a + 2]], e2 = [p[c] - p[a], p[c + 1] - p[a + 1], p[c + 2] - p[a + 2]];
      var f = croix(e1, e2);
      for (var j = 0; j < 3; j++) { var q = i[k + j] * 3; n[q] += f[0]; n[q + 1] += f[1]; n[q + 2] += f[2]; }
    }
    for (var q = 0; q < n.length; q += 3) { var u = norm([n[q], n[q + 1], n[q + 2]]); n[q] = u[0]; n[q + 1] = u[1]; n[q + 2] = u[2]; }
    this.n = Array.prototype.slice.call(n);
    return this;
  };
  var G = {
    /* Un plan couché (XZ), w × h, en nx × nz carreaux ; `f(x, z)` le soulève. */
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
    /* Un polygone (contour XZ, sens quelconque) épaissi vers le haut, arêtes arrondies par un biseau. */
    extrusion: function (contour, ep, biseau, pas) {
      var g = new Geo(), n = contour.length, b = biseau || 0, k = pas || 3, cx = 0, cz = 0, aire = 0, j, i;
      for (i = 0; i < n; i++) { cx += contour[i][0] / n; cz += contour[i][1] / n; var q = contour[(i + 1) % n]; aire += contour[i][0] * q[1] - q[0] * contour[i][1]; }
      var sens = aire > 0 ? 1 : -1;
      /* la normale extérieure de chaque sommet (moyenne des deux arêtes) */
      var dehors = contour.map(function (pp, i2) {
        var a = contour[(i2 - 1 + n) % n], c = contour[(i2 + 1) % n];
        var e1 = norm([pp[0] - a[0], 0, pp[1] - a[1]]), e2 = norm([c[0] - pp[0], 0, c[1] - pp[1]]);
        var m = norm([e1[2] + e2[2], 0, -(e1[0] + e2[0])]);
        return [m[0] * sens, m[2] * sens];
      });
      /* les anneaux : du dessous au dessus, le biseau en quart de cercle */
      var anneaux = [];
      for (j = 0; j <= k; j++) { var a1 = (j / k) * Math.PI / 2; anneaux.push([b * (1 - Math.cos(a1)), b * Math.sin(a1)]); }
      var profil = anneaux.map(function (r) { return [-r[0], r[1]]; })
        .concat(anneaux.slice().reverse().map(function (r) { return [-r[0], ep - r[1]]; }));
      var base = g.p.length / 3;
      profil.forEach(function (pr, pi) {
        var ny = pi < profil.length / 2 ? -(1 - pi / (profil.length / 2)) : (pi - profil.length / 2 + 1) / (profil.length / 2);
        for (i = 0; i <= n; i++) {
          var c2 = contour[i % n], d = dehors[i % n], h = Math.sqrt(Math.max(0, 1 - ny * ny));
          g.sommet(c2[0] + d[0] * (b + pr[0]), pr[1], c2[1] + d[1] * (b + pr[0]), d[0] * h, ny, d[1] * h, i / n, pi / (profil.length - 1));
        }
      });
      for (j = 0; j < profil.length - 1; j++) for (i = 0; i < n; i++) {
        var a2 = base + j * (n + 1) + i, b2 = a2 + 1, c3 = a2 + n + 1, d2 = c3 + 1;
        if (sens > 0) g.i.push(a2, b2, c3, b2, d2, c3); else g.i.push(a2, c3, b2, b2, c3, d2);
      }
      /* les deux faces (éventail depuis le centre : le contour est presque convexe) */
      [[0, -1], [ep, 1]].forEach(function (f) {
        var centre = g.sommet(cx, f[0], cz, 0, f[1], 0, 0.5, 0.5);
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
    /* Une révolution autour de Y : profil = [[rayon, hauteur], …] du bas vers le haut. */
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

  /* ── Les nuanceurs. Une seule « matière » pour les solides, en trois manières. ── */
  var VS = "attribute vec3 a_p;attribute vec3 a_n;attribute vec2 a_uv;uniform mat4 u_pv,u_v,u_m;uniform mat3 u_vn;" +
    "varying vec3 v_n,v_e;varying vec2 v_uv;varying vec3 v_w;" +
    "void main(){vec4 w=u_m*vec4(a_p,1.);v_w=w.xyz;v_e=(u_v*w).xyz;v_n=u_vn*a_n;v_uv=a_uv;gl_Position=u_pv*w;}";
  function FS(derive) {
    return (derive ? "#extension GL_OES_standard_derivatives : enable\n" : "") +
      "precision mediump float;uniform float u_mode,u_bump,u_brume,u_coupe;uniform sampler2D u_tex,u_haut;uniform vec4 u_teinte;" +
      "uniform vec3 u_emis,u_lum,u_lumc,u_lp,u_lpc,u_amb;uniform vec2 u_rep;varying vec3 v_n,v_e;varying vec2 v_uv;varying vec3 v_w;" +
      (derive ?
        /* le relief d'une carte de hauteur, sans tangentes (Mikkelsen 2010) */
        "vec3 relief(vec3 n){vec3 dx=dFdx(v_e),dy=dFdy(v_e);float h=texture2D(u_haut,v_uv*u_rep).r;" +
        "float hx=dFdx(h),hy=dFdy(h);vec3 r1=cross(dy,n),r2=cross(n,dx);float d=dot(dx,r1);" +
        "return normalize(abs(d)*n-u_bump*sign(d)*(hx*r1+hy*r2));}" : "vec3 relief(vec3 n){return n;}") +
      "void main(){vec3 n=normalize(v_n);if(!gl_FrontFacing)n=-n;if(u_bump>0.)n=relief(n);vec4 c;" +
      /* 0 · matcap : la sphère de Blender, lue par le reflet (tient compte de la perspective) */
      "if(u_mode<.5){vec3 e=normalize(v_e),r=reflect(e,n);float m=2.8284*sqrt(r.z+1.001);" +
      "c=vec4(texture2D(u_tex,r.xy/m*.96+.5).rgb*u_teinte.rgb,u_teinte.a);}" +
      /* 1 · papier : la clé chaude enveloppante + une lumière ponctuelle (la bougie, le halo) */
      "else if(u_mode<1.5){vec4 a=texture2D(u_tex,v_uv*u_rep)*u_teinte;float w=max((dot(n,u_lum)+.3)/1.3,0.);" +
      "vec3 d=u_lp-v_w;float l2=dot(d,d);float pl=max(dot(n,normalize(d)),0.)/(1.+l2*.7);" +
      "c=vec4(a.rgb*(u_amb+u_lumc*w+u_lpc*pl),a.a);}" +
      /* 2 · plat : la texture telle quelle */
      "else{c=texture2D(u_tex,v_uv*u_rep)*u_teinte;}" +
      "if(c.a<u_coupe)discard;c.rgb+=u_emis;c.rgb=mix(c.rgb,vec3(.031,.024,.043),u_brume*clamp(-v_e.z*.06-.2,0.,1.));" +
      "gl_FragColor=vec4(c.rgb*c.a,c.a);}";
  }
  /* Les lutins : lumières, étincelles, pétales, fumée. Préparés en un seul tampon. */
  var VS2 = "attribute vec3 a_p;attribute vec2 a_uv;attribute vec4 a_c;uniform mat4 u_pv;varying vec2 v_uv;varying vec4 v_c;" +
    "void main(){v_uv=a_uv;v_c=a_c;gl_Position=u_pv*vec4(a_p,1.);}";
  var FS2 = "precision mediump float;uniform sampler2D u_tex;uniform float u_add;varying vec2 v_uv;varying vec4 v_c;" +
    "void main(){vec4 t=texture2D(u_tex,v_uv);float a=t.a*v_c.a;gl_FragColor=vec4(t.rgb*v_c.rgb*a,a*(1.-u_add));}";

  function Theatre(canvas, options) {
    var o = options || {};
    var gl = canvas.getContext("webgl", { antialias: true, alpha: true, premultipliedAlpha: true, preserveDrawingBuffer: !!o.garder }) ||
      canvas.getContext("experimental-webgl");
    if (!gl) return null;
    var derive = !!gl.getExtension("OES_standard_derivatives");
    var S = { gl: gl, M: M, C: C, G: G, k: 1, W: 1, H: 1, pret: true, attente: 0 };

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
    }
    /* Une texture dessinée (canvas) : prête tout de suite. */
    S.toile = function (w, h, dessin, repete) {
      var c = document.createElement("canvas"); c.width = w; c.height = h;
      dessin(c.getContext("2d"), w, h);
      var t = gl.createTexture(); poser(t, c, repete); t.toile = c; return t;
    };
    /* Une image (une matcap en data:) : le théâtre attend qu'elle soit décodée. */
    S.image = function (src) {
      var t = gl.createTexture(), im = new Image();
      poser(t, (function () { var c = document.createElement("canvas"); c.width = c.height = 1; return c; })(), false);
      S.attente++; S.pret = false;
      im.onload = function () { poser(t, im, false); if (--S.attente === 0) { S.pret = true; } };
      im.onerror = function () { if (--S.attente === 0) { S.pret = true; } };
      im.src = src;
      return t;
    };
    /* La lueur ronde : partout la même recette (halos, étincelles, ombres). */
    S.rond = S.toile(64, 64, function (g) {
      var r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(0.35, "rgba(255,255,255,.5)"); r.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = r; g.fillRect(0, 0, 64, 64);
    });

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

    /* ── la caméra, cadrée sur un rectangle de la page ── */
    var V = M.id(), PV = M.id(), cam = { oeil: [0, 3, 3], cible: [0, 0, 0] };
    S.taille = function () {
      var k = Math.min(window.devicePixelRatio || 1, o.kmax || 2);
      var w = canvas.clientWidth || window.innerWidth, h = canvas.clientHeight || window.innerHeight;
      S.k = k; S.W = w; S.H = h;
      canvas.width = Math.round(w * k); canvas.height = Math.round(h * k);
    };
    S.taille();
    /* oeil, cible, champ (degrés), et le point de l'écran (px) où tombe la cible. */
    S.camera = function (oeil, cible, champ, ecranX, ecranY) {
      cam.oeil = oeil; cam.cible = cible;
      V = M.vise(oeil, cible, [0, 1, 0]);
      var P = M.persp((champ || 32) * Math.PI / 180, S.W / S.H, 0.05, 80);
      if (ecranX != null) { P[8] = -((ecranX / S.W) * 2 - 1); P[9] = -(1 - (ecranY / S.H) * 2); }
      PV = M.mul(P, V);
      S.V = V; S.PV = PV;
    };
    /* La distance à laquelle un objet de largeur `l` occupe `px` pixels de large (champ vertical, en degrés). */
    S.distance = function (l, px, champ) {
      return (l * S.H) / (2 * px * Math.tan((champ || 32) * Math.PI / 360));
    };

    /* ── la lumière ── */
    var L = { lum: norm([-0.5, 0.8, 0.6]), lumc: [1.0, 0.86, 0.68], amb: [0.16, 0.13, 0.18], lp: [0, 1, 0], lpc: [0, 0, 0], brume: 0 };
    S.lumiere = function (o2) { for (var c in o2) L[c] = o2[c]; };

    /* ── dessiner un solide ── */
    S.effacer = function () {
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.disable(gl.CULL_FACE);
    };
    var blanc = S.toile(4, 4, function (g) { g.fillStyle = "#fff"; g.fillRect(0, 0, 4, 4); });
    S.blanc = blanc;
    /* matiere : {mode: "matcap"|"papier"|"plat", tex, teinte:[r,g,b,a], haut, bump, rep:[u,v], emis:[r,g,b]} */
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
      var rep = mat.rep || [1, 1]; gl.uniform2f(u.u_rep, rep[0], rep[1]);
      gl.uniform1f(u.u_bump, derive && mat.haut ? (mat.bump || 1) : 0);
      /* une découpe (bord festonné, dentelle) : ce que la texture laisse transparent n'est pas peint */
      gl.uniform1f(u.u_coupe, mat.coupe || 0);
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

    /* ── les lutins : un tampon refait à chaque image ──
       liste : [{p:[x,y,z], s:taille, c:[r,g,b,a], r:rotation, ax:[…], ay:[…] (orientés), u:[u0,v0,u1,v1]}] */
    var tamponL = gl.createBuffer(), indL = gl.createBuffer(), maxL = 0;
    S.lutins = function (liste, tex, additif) {
      if (!liste.length) return;
      var n = liste.length;
      if (n > maxL) {
        maxL = n; var ix = new Uint16Array(n * 6);
        for (var q = 0; q < n; q++) { ix.set([q * 4, q * 4 + 1, q * 4 + 2, q * 4 + 2, q * 4 + 1, q * 4 + 3], q * 6); }
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indL); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, ix, gl.STATIC_DRAW);
      }
      var d = new Float32Array(n * 4 * 9), dx = [V[0], V[4], V[8]], dy = [V[1], V[5], V[9]];
      liste.forEach(function (l, q) {
        var s = l.s / 2, ax = l.ax || dx, ay = l.ay || dy, c = Math.cos(l.r || 0), sn = Math.sin(l.r || 0), uv = l.u || [0, 0, 1, 1];
        var X = [(ax[0] * c + ay[0] * sn) * s, (ax[1] * c + ay[1] * sn) * s, (ax[2] * c + ay[2] * sn) * s];
        var Y = [(ay[0] * c - ax[0] * sn) * s * (l.h || 1), (ay[1] * c - ax[1] * sn) * s * (l.h || 1), (ay[2] * c - ax[2] * sn) * s * (l.h || 1)];
        [[-1, -1, uv[0], uv[3]], [1, -1, uv[2], uv[3]], [-1, 1, uv[0], uv[1]], [1, 1, uv[2], uv[1]]].forEach(function (k, v) {
          var o2 = (q * 4 + v) * 9;
          d[o2] = l.p[0] + X[0] * k[0] + Y[0] * k[1]; d[o2 + 1] = l.p[1] + X[1] * k[0] + Y[1] * k[1]; d[o2 + 2] = l.p[2] + X[2] * k[0] + Y[2] * k[1];
          d[o2 + 3] = k[2]; d[o2 + 4] = k[3];
          d[o2 + 5] = l.c[0]; d[o2 + 6] = l.c[1]; d[o2 + 7] = l.c[2]; d[o2 + 8] = l.c[3] == null ? 1 : l.c[3];
        });
      });
      var P = P2;
      gl.useProgram(P.p);
      gl.uniformMatrix4fv(P.u.u_pv, false, PV); gl.uniform1f(P.u.u_add, additif ? 1 : 0);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex || S.rond); gl.uniform1i(P.u.u_tex, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, tamponL); gl.bufferData(gl.ARRAY_BUFFER, d, gl.DYNAMIC_DRAW);
      gl.enableVertexAttribArray(P.a.p); gl.vertexAttribPointer(P.a.p, 3, gl.FLOAT, false, 36, 0);
      gl.enableVertexAttribArray(P.a.uv); gl.vertexAttribPointer(P.a.uv, 2, gl.FLOAT, false, 36, 12);
      gl.enableVertexAttribArray(P.a.c); gl.vertexAttribPointer(P.a.c, 4, gl.FLOAT, false, 36, 20);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indL);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, additif ? gl.ONE : gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false);
      gl.drawElements(gl.TRIANGLES, n * 6, gl.UNSIGNED_SHORT, 0);
      gl.depthMask(true); gl.disableVertexAttribArray(P.a.c);
    };
    /* Une ombre douce couchée sur la table (y donné), sous un objet. */
    S.ombre = function (x, y, z, rx, rz, force, rot) {
      S.lutins([{ p: [x, y + 0.002, z], s: rx * 2, h: rz / rx, r: rot || 0, ax: [1, 0, 0], ay: [0, 0, 1], c: [0.02, 0.01, 0.03, force] }], S.rond, false);
    };
    return S;
  }

  /* ═══ La mise en scène : le théâtre joue un rite dans un canvas, puis rend la main.
     jouer(canvas, rite, D, {fin, abandon}) → {ouvrir(), arreter()}
     ─ avant le geste : le rite respire (t < 0), à 30 images par seconde au plus, et rien quand la page est cachée ;
     ─ au geste : t va de 0 à rite.duree ; à rite.revele, la lettre peut commencer à paraître (fin()) ;
     ─ au moindre souci (pas de WebGL, une erreur), abandon() : la lettre s'ouvre comme avant, sans rien perdre. ═══ */
  function jouer(canvas, rite, D, rappels) {
    var S;
    try { S = Theatre(canvas, { kmax: rite.kmax || 2 }); } catch (e) { S = null; }
    if (!S) { rappels.abandon && rappels.abandon(); return null; }
    try { rite.monter(S, D); } catch (e) { rappels.abandon && rappels.abandon(e); return null; }
    var t0 = 0, tOuvre = -1, fini = false, revele = false, dernier = 0, lent = 0, arret = false;
    function image(now) {
      if (arret) return;
      requestAnimationFrame(image);
      if (!t0) t0 = now;
      if (document.hidden) return;
      if (tOuvre < 0 && now - dernier < 33) return; /* au repos : 30 images par seconde suffisent */
      var dt = now - dernier; dernier = now;
      if (dt > 60 && tOuvre >= 0 && ++lent > 20 && S.k > 1) { lent = 0; rite.kmax = 1; S.taille(); } /* téléphone à la peine : moins de pixels */
      if (!S.pret) return;
      var t = tOuvre < 0 ? -1 : (now - tOuvre) / 1000, ti = (now - t0) / 1000;
      try { rite.rendre(S, t, ti); } catch (e) { arret = true; rappels.abandon && rappels.abandon(e); return; }
      if (tOuvre >= 0 && !revele && t >= (rite.revele || rite.duree)) { revele = true; rappels.fin && rappels.fin(); }
      if (tOuvre >= 0 && t >= rite.duree + 0.6) { arret = true; fini = true; }
    }
    requestAnimationFrame(image);
    addEventListener("resize", function () { S.taille(); });
    return {
      S: S,
      ouvrir: function () { if (tOuvre < 0) { tOuvre = performance.now(); rite.geste && rite.geste(S); } },
      arreter: function () { arret = true; },
      fini: function () { return fini; }
    };
  }

  Theatre.jouer = jouer;
  Theatre.M = M; Theatre.C = C; Theatre.G = G;
  return Theatre;
})();
