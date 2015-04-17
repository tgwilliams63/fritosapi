import requests
import time
import json
import sys
from pymongo import MongoClient
from ConfigParser import RawConfigParser


#read api key from config files
config = RawConfigParser()
config.read("frito.conf")

api_key = "api_key=" + config.get("api details", "api_key")
#hard coded because this is for urf games only
api_url = "https://na.api.pvp.net/api/lol/na/v4.1/game/ids?beginDate="
mongo_address	= config.get("mongo details", "mongo_address")
mongo_user		= config.get("mongo details", "mongo_user")
mongo_pass		= config.get("mongo details", "mongo_pass")
mongo_port		= config.getint("mongo details", "mongo_port")
mongo_db		= config.get("mongo details", "mongo_db")


closest_five_mins = int(time.time()/300)*300-300 #five minutes ago, just because we don't want to hit any race conditions for giggles

#grab the match_ids from riotapi
match_ids_json = json.loads(requests.get(api_url + str(closest_five_mins)\
				 + "&" + api_key).text)

print("logging matches...")

#try to insert into the database
try:
	m_client = MongoClient(mongo_address, mongo_port)
	m_client[mongo_db].authenticate(mongo_user, mongo_pass, mechanism="SCRAM-SHA-1")
	m_db = m_client[mongo_db]

	print match_ids_json
	for match in match_ids_json:
		m_db.unprocessed_matches.insert({"match_id":match})

except:
	print("Error: " + str(sys.exc_info()))

finally:
	m_client.close()