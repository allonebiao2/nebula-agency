# -*- coding: utf-8 -*-
"""Point d'entrée de l'exécutable NEBULA Trader (PyInstaller)."""
import sys

from trading.app import main

if __name__ == "__main__":
    sys.exit(main())
