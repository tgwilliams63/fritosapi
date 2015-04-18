from pymongo import MongoClient
import requests
import json
from pprint import pprint
from ConfigParser import RawConfigParser
import time
import sys


api_url 		= "https://na.api.pvp.net"
match_api_url 	= "/api/lol/na/v2.2/match/"
limit 			= 1

###### Read from config file ######
config			= RawConfigParser()
config.read("frito.conf")
api_key 		= "api_key=" + config.get("api details", "api_key")
mongo_address	= config.get("mongo details", "mongo_address")
mongo_user		= config.get("mongo details", "mongo_user")
mongo_pass		= config.get("mongo details", "mongo_pass")
mongo_port		= config.getint("mongo details", "mongo_port")
mongo_db		= config.get("mongo details", "mongo_db")

#Requests session object allows up to keep the connection alive and avoid
#creating new objects for each request, giving a massive speedup
req_session		= requests.Session()
start = time.time()

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


###############################################################################

def fetch_match(match_id):
	req = req_session.get(api_url + match_api_url + str(match_id) \
						+ "?includeTimeline=true&"  + api_key)
	return json.loads(req.text)


###############################################################################

def process_match(match):
	#First we need to grab the item event data and create a data entry for each one
	db_information = []
	#iterating over the frames and events...
	for i in range(1, len(match["timeline"]["frames"])):
		for event in match["timeline"]["frames"][i]["events"]:
			#if the event is buying an item we care about, we're going to grab stats about it
			if (event["eventType"] == "ITEM_PURCHASED") and (event["itemId"] in complete_item_ids): 
				timestamp 		= event["timestamp"]
				player_id 		= event["participantId"]
				item_id 		= event["itemId"]
				match_id		= match["matchId"]
				game_won		= int(match["participants"][player_id - 1]["stats"]["winner"])
				team_id			= match["participants"][player_id - 1]["teamId"]
				champ_id		= match["participants"][player_id - 1]["championId"]
				game_duration	= match["matchDuration"] * 1000
				game_version	= match["matchVersion"]

				#these are set to zero so we can just increment later
				bldgs_before	= 0
				bldgs_after		= 0
				assists_before	= 0
				assists_after	= 0
				kills_before	= 0
				kills_after		= 0
				deaths_before	= 0
				deaths_after	= 0


				#iterate through all the events again to grab the before/after stats -_-
				for j in range(1, len(match["timeline"]["frames"])):
					for event2 in match["timeline"]["frames"][j]["events"]:

						#if the event is a building and the killer is on the player's team
						if 	(event2["eventType"] == "BUILDING_KILL") and \
							(match["participants"][event2["killerId"] - 1]["teamId"] == team_id):
							if(event2["killerId"] == player_id):
								if(event2["timestamp"] <= timestamp):
									bldgs_before += 1
								else:
									bldgs_after += 1
							else:
								try:	#gotta have the try block here, because if there isn't an assisting players tag, it throws errors
									if(player_id in event2["assistingParticipantIds"]):
										if (event2["timestamp"] <= timestamp):
											bldgs_before += 1
										else:
											bldgs_after += 1	
								except:
									pass
						#if the event is a kill...
						elif (event2["eventType"] == "CHAMPION_KILL"):

							#and is the death of the owner
							if event2["victimId"] == player_id:
								if event2["timestamp"] <= timestamp:
									deaths_before += 1
								else:
									deaths_after += 1
							#or the kill is done by the owner's team....
							elif (match["participants"][event2["killerId"] - 1]["teamId"] == team_id):
								#if the owner did the deed....
								if(event2["killerId"] == player_id):
									if(event2["timestamp"] <= timestamp):
										kills_before += 1
									else:
										kills_after += 1
								#if the owner only assisted
								else:
									try:	#gotta have the try block here, because if there isn't an assisting players tag, it throws errors
										if(player_id in event2["assistingParticipantIds"]):
											if (event2["timestamp"] <= timestamp):
												assists_before += 1
											else:
												assists_after += 1	
									except:
										pass
				#for statement ends here

				#calculate the per minute values
				minutes_before 	= float(int(timestamp / 60000))
				minutes_after 	= float(int((game_duration - timestamp) / 60000))

				if minutes_before > 0:
					bldgs_before 	= bldgs_before / minutes_before
					kills_before	= kills_before / minutes_before
					deaths_before	= deaths_before / minutes_before 
					assists_before	= assists_before / minutes_before
				else:
					bldgs_before 	= 0
					kills_before	= 0
					deaths_before	= 0
					assists_before	= 0

				if minutes_after > 0:
					bldgs_after		= bldgs_after / minutes_after
					kills_after		= kills_after / minutes_after
					deaths_after	= deaths_after / minutes_after
					assists_after	= assists_after / minutes_after
				else:
					bldgs_after		= 0
					kills_after		= 0
					deaths_after	= 0
					assists_after	= 0

				#stick all the collected data into a dictionary that matches the database layout (simplifies things later)
				db_information.append({	"timestamp" 	: timestamp,
										"minute_bought"	: int(minutes_before), #this works because the minutes before the item is the minute the item was bought
										"player_id" 	: player_id,
										"item_id"		: item_id,
										"champ_id"		: champ_id,
										"match_id"		: match_id,
										"game_won"		: game_won,
										"bldg_before"	: bldgs_before,
										"bldg_after"	: bldgs_after,
										"kills_before"	: kills_before,
										"kills_after"	: kills_after,
										"deaths_before"	: deaths_before,
										"deaths_after"	: deaths_after,
										"assists_before": assists_before,
										"assists_after" : assists_after,
										"game_duration"	: game_duration,
										"game_version"	: game_version})
	return db_information

###############################################################################

#db connection stuff
m_client = MongoClient(mongo_address, mongo_port)
m_client[mongo_db].authenticate(mongo_user, mongo_pass, mechanism="SCRAM-SHA-1")
m_db = m_client[mongo_db]

#grab the unprocessed match ids 
unprocessed = m_db.unprocessed_matches.find(limit = limit)

#set up arrays and a progress tracker
games_data = []
match_ids = [] #here so we don't have to requery the database with .rewind()
errored = []
progress = 0

for record in unprocessed:
	progress += 1
	#just a status message
	print "Processing match: " + str(record["match_id"]) + " " + str(progress) + "/" + str(limit)

	#append the match_id here so we don't have to requery the database
	match_ids.append(record["match_id"])
	try:

		#since process_match gives us an array of dictionaries, and we want to end up with an array of 
		#dictionaries for mongo to process for us, we have to go into the returned array and append
		#the event dictionaries to the master games_data array
		for event in process_match(fetch_match(record["match_id"])):
			games_data.append(event)
	except:
		#you have fucked up now: log it into the database
		print "ERROR: " + str(record["match_id"])
		print sys.exc_info()[0]
		errored.append({"match_id" : record["match_id"]})


##inset the item data
#if len(games_data) > 0:
#	m_db.item_buys.insert(games_data)
#
##insert the errors
#if len(errored) > 0:
#	m_db.errored_matches.insert(errored)
#
##remove the processed matches from the queue
#for mid in match_ids:
#	m_db.unprocessed_matches.remove({"match_id":mid})


#Data crunching time


item_avg = []
item_buy_time = []

pipeline = [{	"$group" : {"_id": "$item_id", 
							"winrate": {"$avg" : "$game_won"},
							"kills_before": {"$avg": "$kills_before"},
							"deaths_before": {"$avg": "$deaths_before"},
							"assists_before": {"$avg": "$assists_before"},
							"bldg_before": {"$avg": "$bldg_before"},
							"kills_after": {"$avg": "$kills_after"},
							"deaths_after": {"$avg": "$deaths_after"},
							"assists_after": {"$avg": "$assists_after"},
							"bldg_after": {"$avg": "$bldg_after"},
							"times_bought" : {"$sum" : 1}
						   }
			}]

print "Creating item_avg collection"
for x in m_db.item_buys.aggregate(pipeline):
	item_avg.append(x)

pipeline = [{	"$group" : {"_id": {"item_id": "$item_id", "minute_bought" : "$minute_bought"}, 
							"count": {"$sum": 1},
							"winrate": {"$avg" : "$game_won"},
							"item_id": {"$avg" : "$item_id"},
							"minute_bought": {"$avg" : "$minute_bought"}}
			}]

print "Creating item_buy_time collection"
for x in m_db.item_buys.aggregate(pipeline):
	item_buy_time.append(x)
	
#drop item_avg databases
print "Inserting into item_avg"
m_db.item_avg.remove({})
m_db.item_avg.insert(item_avg)


print "Inserting into item_buy_time"
m_db.item_buy_time.remove({})
m_db.item_buy_time.insert(item_buy_time)


#tell us how much time we just wasted compared to the threaded version
print "Done " + str(time.time() - start)
m_client.close()

