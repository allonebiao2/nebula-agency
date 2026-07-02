#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache-bust : ?v=20260701n -> ?v=20260702a sur les 3 pages. UTF-8."""
import io, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
OLD, NEW = "?v=20260701n", "?v=20260702a"
for f in ("weinkeller.html", "index.html", "speed.html"):
    s = io.open(f, encoding="utf-8").read()
    n = s.count(OLD)
    io.open(f, "w", encoding="utf-8").write(s.replace(OLD, NEW))
    print(f"{f}: {n} bump(s) -> {NEW}")
