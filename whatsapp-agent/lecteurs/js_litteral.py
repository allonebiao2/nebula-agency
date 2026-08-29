"""Lire un littéral d'objet JavaScript/TypeScript sans exécuter de JavaScript.

Les catalogues des clients NEBULA sont écrits dans leur site, en TypeScript
(`CARTE` chez Au Braisé d'Or) ou en JavaScript dans le HTML (`PIECES` chez
Hillary). Ce ne sont pas des fichiers JSON : les clés n'ont pas de guillemets,
les chaînes en ont de simples, il traîne des virgules finales et beaucoup de
commentaires — dont certains sont les décisions de la maison, en français.

⚠️ On ne peut donc pas faire `json.loads`, et on ne veut surtout pas d'un `eval`
sur un fichier du dépôt. Ce module lit le littéral caractère par caractère :
rien n'est exécuté, et un fichier mal formé lève une erreur nommée au lieu de
rendre un demi-catalogue en silence.
"""
from __future__ import annotations


class ErreurLitteral(ValueError):
    """Le fichier ne contient pas le littéral attendu, ou il est mal formé."""


_IDENT_DEBUT = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_$")
_IDENT_SUITE = _IDENT_DEBUT | set("0123456789")


class _Lecteur:
    def __init__(self, src: str, depart: int = 0):
        self.s = src
        self.i = depart

    # --- déplacement ---------------------------------------------------
    def _sauter_vide(self) -> None:
        """Espaces ET commentaires — jamais à l'intérieur d'une chaîne."""
        while self.i < len(self.s):
            c = self.s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif self.s.startswith("//", self.i):
                fin = self.s.find("\n", self.i)
                self.i = len(self.s) if fin == -1 else fin + 1
            elif self.s.startswith("/*", self.i):
                fin = self.s.find("*/", self.i + 2)
                if fin == -1:
                    raise ErreurLitteral("commentaire /* jamais refermé")
                self.i = fin + 2
            else:
                return

    def _attendre(self, c: str) -> None:
        self._sauter_vide()
        if self.i >= len(self.s) or self.s[self.i] != c:
            raise ErreurLitteral(f"« {c} » attendu à la position {self.i}, {self._ici()}")
        self.i += 1

    def _ici(self) -> str:
        bout = self.s[self.i:self.i + 40].replace("\n", " ")
        return f"trouvé : « {bout}… »"

    # --- valeurs -------------------------------------------------------
    def valeur(self):
        self._sauter_vide()
        if self.i >= len(self.s):
            raise ErreurLitteral("fin de fichier au milieu d'une valeur")
        c = self.s[self.i]
        if c == "{":
            return self._objet()
        if c == "[":
            return self._tableau()
        if c in "\"'":
            return self._chaine()
        if c == "`":
            raise ErreurLitteral("chaîne à gabarit (`) non gérée : ce lecteur n'exécute pas de JS")
        if c == "-" or c.isdigit():
            return self._nombre()
        mot = self._identifiant()
        if mot == "true":
            return True
        if mot == "false":
            return False
        if mot in ("null", "undefined"):
            return None
        raise ErreurLitteral(f"valeur inattendue « {mot} » à la position {self.i}")

    def _objet(self) -> dict:
        self._attendre("{")
        obj: dict = {}
        while True:
            self._sauter_vide()
            if self.i < len(self.s) and self.s[self.i] == "}":
                self.i += 1
                return obj
            cle = self._chaine() if self.s[self.i] in "\"'" else self._identifiant()
            self._attendre(":")
            obj[cle] = self.valeur()
            self._sauter_vide()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1  # virgule finale tolérée : le tour suivant verra « } »
            elif self.i < len(self.s) and self.s[self.i] == "}":
                self.i += 1
                return obj
            else:
                raise ErreurLitteral(f"« , » ou « }} » attendu, {self._ici()}")

    def _tableau(self) -> list:
        self._attendre("[")
        arr: list = []
        while True:
            self._sauter_vide()
            if self.i < len(self.s) and self.s[self.i] == "]":
                self.i += 1
                return arr
            arr.append(self.valeur())
            self._sauter_vide()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1
            elif self.i < len(self.s) and self.s[self.i] == "]":
                self.i += 1
                return arr
            else:
                raise ErreurLitteral(f"« , » ou « ] » attendu, {self._ici()}")

    def _chaine(self) -> str:
        guillemet = self.s[self.i]
        self.i += 1
        out: list[str] = []
        echappements = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f",
                        "\\": "\\", "/": "/", "'": "'", '"': '"', "\n": ""}
        while True:
            if self.i >= len(self.s):
                raise ErreurLitteral("chaîne jamais refermée")
            c = self.s[self.i]
            if c == "\\":
                suite = self.s[self.i + 1]
                if suite == "u":
                    out.append(chr(int(self.s[self.i + 2:self.i + 6], 16)))
                    self.i += 6
                    continue
                out.append(echappements.get(suite, suite))
                self.i += 2
                continue
            if c == guillemet:
                self.i += 1
                return "".join(out)
            out.append(c)
            self.i += 1

    def _nombre(self):
        debut = self.i
        if self.s[self.i] == "-":
            self.i += 1
        while self.i < len(self.s) and (self.s[self.i].isdigit() or self.s[self.i] in ".eE+-"):
            # « 3000, » : la virgule arrête, le point décimal continue
            if self.s[self.i] in "+-" and self.s[self.i - 1] not in "eE":
                break
            self.i += 1
        brut = self.s[debut:self.i]
        try:
            return float(brut) if ("." in brut or "e" in brut or "E" in brut) else int(brut)
        except ValueError as exc:
            raise ErreurLitteral(f"nombre illisible « {brut} »") from exc

    def _identifiant(self) -> str:
        debut = self.i
        if self.i < len(self.s) and self.s[self.i] in _IDENT_DEBUT:
            self.i += 1
            while self.i < len(self.s) and self.s[self.i] in _IDENT_SUITE:
                self.i += 1
        if debut == self.i:
            raise ErreurLitteral(f"nom attendu à la position {self.i}, {self._ici()}")
        return self.s[debut:self.i]


def lire_declaration(source: str, nom: str):
    """Rend la valeur de `… <nom> = …` — `export const CARTE = [...]`, `var PIECES = [...]`.

    On cherche la DÉCLARATION, pas la première mention : `NB_PLATS = CARTE.reduce(...)`
    cite `CARTE` sans la déclarer, et se tromper de point de départ rendrait un
    catalogue vide sans le dire.
    """
    depart = 0
    while True:
        pos = source.find(nom, depart)
        if pos == -1:
            raise ErreurLitteral(f"déclaration « {nom} » introuvable")
        depart = pos + len(nom)
        # le nom doit être entier, pas un morceau d'un autre identifiant
        avant = source[pos - 1] if pos else " "
        apres = source[depart] if depart < len(source) else " "
        if avant in _IDENT_SUITE or apres in _IDENT_SUITE:
            continue
        lecteur = _Lecteur(source, depart)
        lecteur._sauter_vide()
        j = lecteur.i
        # Une annotation de type TypeScript peut s'intercaler, et elle a le droit
        # de contenir des crochets : `const CARTE: Cat[] = [`. On la saute jusqu'au
        # « = », au lieu de se fier au premier crochet venu.
        if j < len(source) and source[j] == ":":
            j = source.find("=", j)
            if j == -1:
                continue
        if j >= len(source) or source[j] != "=":
            continue  # une mention (`CARTE.reduce`, un import), pas une déclaration
        if source[j + 1:j + 2] in ("=", ">") or source[j - 1] in "<>!=":
            continue  # « == », « => », « <= » : ce n'est pas une affectation
        lecteur.i = j + 1
        lecteur._sauter_vide()
        if lecteur.i < len(source) and source[lecteur.i] in "[{":
            return lecteur.valeur()
