"""LE MONDE · appliquer la correspondance de `projeter_visage.py` : la texture d'origine du modèle (extraite du .glb
telle quelle) + les pixels nets de la photo, mélangés texel par texel.

    python monde/_outils/appliquer_visage.py modele.glb image.jpg correspondance.npz texture-sortie.jpg
"""
import io, json, struct, sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
glb, image, corr, sortie = sys.argv[1:5]
b = open(glb, "rb").read()
L = struct.unpack("<I", b[12:16])[0]; js = json.loads(b[20:20 + L]); off = 20 + L
bin_ = b[off + 8: off + 8 + struct.unpack("<I", b[off:off + 4])[0]]
vue = js["bufferViews"][js["images"][0]["bufferView"]]; o = vue.get("byteOffset", 0)
T = np.asarray(Image.open(io.BytesIO(bin_[o:o + vue["byteLength"]])).convert("RGB"), dtype=np.float32)
S = np.asarray(Image.open(image).convert("RGB"), dtype=np.float32)
c = np.load(corr)
assert T.shape[1] == c["taille"][0] and T.shape[0] == c["taille"][1], "la texture n'a pas la taille attendue"
w = c["w"][:, None]
T[c["ligne"], c["col"]] = T[c["ligne"], c["col"]] * (1 - w) + S[c["v"], c["u"]] * w
Image.fromarray(np.clip(T, 0, 255).astype(np.uint8)).save(sortie, quality=92)
print(f"✅ {len(w)} texels mélangés → {sortie}")
