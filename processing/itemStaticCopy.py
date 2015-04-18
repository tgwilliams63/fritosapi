from pymongo import MongoClient
import requests
import json
from pprint import pprint
from ConfigParser import RawConfigParser
import time
import sys


api_url 		= "https://global.api.pvp.net/api/lol/static-data/na/v1.2/item/"
api_options		= "?itemData=sanitizedDescription&"

###### Read from config file ######
config			= RawConfigParser()
config.read("frito.conf")
api_key 		= "api_key=" + config.get("api details", "api_key")
mongo_address	= config.get("mongo details", "mongo_address")
mongo_user		= config.get("mongo details", "mongo_user")
mongo_pass		= config.get("mongo details", "mongo_pass")
mongo_port		= config.getint("mongo details", "mongo_port")
mongo_db		= config.get("mongo details", "mongo_db")

#db connection stuff
m_client = MongoClient(mongo_address, mongo_port)
m_client[mongo_db].authenticate(mongo_user, mongo_pass, mechanism="SCRAM-SHA-1")
m_db = m_client[mongo_db]


req = requests.Session()

#There doesn't seem to be a good way to extract the "final build" items from the api. Bleh. So we have to do this manually.
complete_item_ids = [	
						3001, #abyssal septer
						3003, #archangel staff
						3048, #seraph's embrace
						3504, #ardent censor
						3174, #athene's unholy grail
						3060, #banner of command
						3102, #banshee's veil
						3071, #black cleaver
						3153, #blade of the ruined king
						3072, #bloodthirster
						3137, #dervish bladepid
						3184, #entropy
						3508, #essence reaver
						3401, #face of the mountain
						3092, #frost queen's claim
						3110, #frozen heart
						3022, #frozen mallet
						3159, #grez's spectral lantern
						3026, #guardian angel
						2051, #guardian's horn
						3124, #guinsoo's rageblade
						3146, #hextech gunblade
						3187, #hextech sweeper
						3025, #iceborn guantlet
						3031, #infinity edge
						3035, #last whisper
						3151, #liandry's torment
						3100, #lich bane
						3185, #lightbringer
						3190, #locket of the iron solari
						3104, #lord van damm's pillager
						3004, #MANAMUNE!
						3042, #muramana
						3156, #maw of malmortius
						3041, #mejai's soulstealer
						3139, #mercurial scimitar
						3222, #mikael's crucible
						3170, #moonflair spellblade
						3165, #morellonomicon
						3115, #nashor's tooth
						3180, #odyn's veil
						3056, #ohmwrecker
						3112, #orb of winter
						3084, #overlord's bloodmail
						3046, #phantom dancer
						3089, #rabadon's deathcap
						3143, #randuin's omen
						3074, #ravenous hydra
						3800, #rightous glory
						3027, #rod of ages
						2045, #ruby sightstone
						3085, #runaan's hurricane
						3116, #rylai's crystal scepter
						3181, #sanguine blade
						3065, #spirit visage
						3087, #statikk shiv
						3068, #funfire cape
						3141, #sword of the occult
						3069, #talisman of ascension
						3075, #thornmail
						3078, #trinity force
						3023, #twin shadows (sr/aram)
						3290, #twin shadows (tt/dom)
						3135, #void staff
						3083, #warmog's armor
						3152, #will of the ancients
						3091, #wit's end
						3090, #wooglet's witchcap
						3142, #youmuu's ghostblade
						3050, #zeke's herald
						3172, #zephyr
						3157, #zhonya's hourglass
						3512, #zz'rot portal
					]

db_data = []

for iid in complete_item_ids:
	result = json.loads(req.get(api_url + str(iid) + api_options + api_key).text)
	db_data.append({"_id" : iid, "item_name" : result["name"], "item_desc" : result["sanitizedDescription"]})

m_db.item_static.remove({})
m_db.item_static.insert(db_data)
m_client.close()