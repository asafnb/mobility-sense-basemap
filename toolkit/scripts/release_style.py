"""Freeze style/style.json as an immutable style version (style/versions/style_<style_version>.json).
Usage: python scripts/release_style.py
Workflow: edit style/style.json -> bump "style_version" (s1 -> s2) -> run this -> make_base.py."""
import os,sys,json; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
S=load_json(f"{ROOT}/style/style.json"); v=S['style_version']; p=f"{ROOT}/style/versions/style_{v}.json"
if os.path.exists(p):
    if load_json(p)==S: sys.exit(f"style {v} already released, no changes")
    sys.exit(f"style {v} already released and style.json differs – bump style_version (e.g. s{int(v[1:])+1}) and rerun")
save_json(p,S); print("released",p)
