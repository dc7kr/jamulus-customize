#!/usr/bin/env python3

import sys

import yaml
import base64

import os

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape

from yaml.loader import SafeLoader

import argparse

def encode_string(string):
  encoded = base64.b64encode(string.encode("utf-8"))
  b64str = str(encoded, "utf-8")
  return b64str

parser = argparse.ArgumentParser(description='Customize Jambox image.')
parser.add_argument('--instrument', help='instrument number Jamulus (11=mic, 40=guitar, 4=mandolin)', type=int,default=11)
parser.add_argument('--name', help='Real-name of the player')
parser.add_argument('--city', help='City the player lives in.')
parser.add_argument('--lang', help='UI language - default: de.', default="de")
parser.add_argument('--country', type=int, help='Country the player is located in (default=82 - Germany)', default=82)
parser.add_argument('--skill', type=int, help='Players skill level (0=none,1=Beginner,2=Intermediate,3=Expert) default=2', default=2)
parser.add_argument('--config', default="config.yml")

args = parser.parse_args()

env = Environment(
    loader=FileSystemLoader("templates/"),
    autoescape=select_autoescape()
)

with open('config.yml', 'r') as f:
    cfg = list(yaml.load_all(f, Loader=SafeLoader))
    cfg=cfg[0]

jamulus_start_tpl = env.get_template("jamulus_start.conf")
jamulus_config_tpl = env.get_template("Jamulus.ini")

city_b64 = encode_string(args.city)
name_b64 = encode_string(args.name)

render = jamulus_start_tpl.render(jamulus_autostart=cfg["jamulus"]["autostart"], jamulus_server=cfg["jamulus"]["server"], jamulus_timeout=cfg["jamulus"]["timeout"])

mountpoint = cfg["image"]["mountpoint"]
image = cfg["image"]["path"]

res = os.system(f'mount -o loop,offset=4194304 {image} {mountpoint}')

if res != 0:
  print(f"Error mounting: {res}")
  sys.exit(1)

timezone = cfg["general"]["timezone"]+"\n"
with open(f'{mountpoint}/payload/etc/timezone',"w") as f:
  f.write(timezone)

with open(f'{mountpoint}/payload/home/pi/.config/Jamulus/jamulus_start.conf',"w") as f:
  f.write(render)

render = jamulus_config_tpl.render(name_b64=name_b64, instrument=args.instrument, country=args.country, city_b64=city_b64,skill=args.skill,lang=args.lang)

with open(f'{mountpoint}/payload/home/pi/.config/Jamulus/Jamulus.ini',"w") as f:
  f.write(render)


res = os.system(f'umount {mountpoint}')

# <name_base64>{{name_b64}}</name_base64>
# <city_base64>{{city_b64}}</city_base64>
# <instrument>{{instrument}}</instrument>
# <country>{{country}}</country>
# <skill>0</skill>

