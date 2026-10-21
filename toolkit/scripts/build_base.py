"""Build a base version: dist/mobility-sense-base_<v>.geolibre (full, Drive) + .web.geolibre.json (slim).
Usage: python scripts/build_base.py v3"""
import os,sys; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
bv=sys.argv[1]; write_outputs(compose(bv),f"mobility-sense-base_{bv}")
