"""Freeze style/style.json as an immutable style version (style/versions/style_<style_version>.json).
Usage: python scripts/release_style.py
Naming: s<major>.<minor>. Minor (s2.0 -> s2.1) = colour / width / label tweaks, same layer ids.
Major (s2.x -> s3.0) = new/split/derived layer ids or schema changes. Legacy 's1' == 's1.0'.
Workflow: edit style/style.json -> bump "style_version" -> run this -> render_release.py (before/after PNGs) -> make_base.py."""
import os,sys,json; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
S=load_json(f"{ROOT}/style/style.json"); v=S['style_version']; style_key(v)
if '.' not in v: sys.exit(f"style_version {v}: use s<major>.<minor> (e.g. s2.0)")
p=style_file(v)
if p:
    if load_json(p)==S: sys.exit(f"style {v} already released, no changes")
    M,m=style_key(v); sys.exit(f"style {v} already released and style.json differs – bump style_version (s{M}.{m+1} for tweaks, s{M+1}.0 for layer/schema changes)")
prev=released_styles()
if prev and style_key(v)<=style_key(prev[-1]): sys.exit(f"{v} is not newer than the latest release {prev[-1]}")
p=f"{ROOT}/style/versions/style_{v}.json"; save_json(p,S); print("released",p)
print(f"next: python scripts/render_release.py {v}   # before/after PNGs into style/releases/{v}/")
