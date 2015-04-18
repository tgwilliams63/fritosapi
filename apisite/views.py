from django.shortcuts import render_to_response
from mongo import mongo_conn as mc
from pymongo import MongoClient
import operator

item_ids = [3001,3003,3048,3504,3174,3060,3102,3071,3153,3072,3137,3184,3508,3401,3092,3110,3022,3159,3026,2051,3124,3146,3187,3025,3031,3035,3151,3100,3185,3190,3104,3004,3042,3156,3041,3139,3222,3170,3165,3115,3180,3056,3112,3084,3046,3089,3143,3074,3800,3027,2045,3085,3116,3181,3065,3087,3068,3141,3069,3075,3078,3023,3290,3135,3083,3152,3091,3090,3142,3050,3172,3157,3512]

def index(request):
	mc.mongo_address
	m_client = MongoClient(mc.mongo_address, mc.mongo_port)
	m_client[mc.mongo_db].authenticate(mc.mongo_user, mc.mongo_pass, mechanism="SCRAM-SHA-1")
	m_db = m_client[mc.mongo_db]
	db_list = m_db.item_avg.find().sort([('winrate',-1)])
	#item_desc_db = dict([(int(x['_id']), x['item_desc']) for x in m_db.item_static.find({}, {"_id" : 1, "item_desc" : 1})])
	item_desc_db = {int(x['_id']): {'desc':x['item_desc'], 'name':x['item_name'] }for x in m_db.item_static.find({}, {"_id" : 1, "item_desc" : 1, "item_name": 1})}
	winrates = [(int(x['_id']), int(x['winrate']*100)) for x in db_list]
	m_client.close()

	# sorted_winrates = sorted(winrates.items(), key=operator.itemgetter(1), reverse=True)
			
	return render_to_response('apisite/index.html', {'item_list':winrates, 'item_desc':item_desc_db})


def item_details(request,item_id):
	if int(item_id) not in item_ids:
		return render_to_response('apisite/item_details.html')

	####Calculations####

	m_client = MongoClient(mc.mongo_address, mc.mongo_port)
	m_client[mc.mongo_db].authenticate(mc.mongo_user, mc.mongo_pass, mechanism="SCRAM-SHA-1")
	m_db = m_client[mc.mongo_db]
	result = m_db.item_avg.find_one({'_id' : int(item_id)})
	kpmbb=result['kills_before']
	kpmab=result['kills_after']
	apmbb=result['assists_before']
	apmab=result['assists_after']
	dpmbb=result['deaths_before']
	dpmab=result['deaths_after']
	bpmbb=result['bldg_before']
	bpmab=result['bldg_after']

	item_name = m_db.item_static.find_one({'_id' : int(item_id)})['item_name']


	buys_by_minute = [0] * 71
	winrate_by_minute = [0] * 71
	buys_by_minute[0] = 'bpm'		# number of items bought by the minute
	winrate_by_minute[0] = 'wrbm'	# the winrate of the item if bought at the specified minute

	for x in m_db.item_buy_time.find({'item_id' : int(item_id)}):
		buys_by_minute[(int(x['minute_bought']) + 1)] = x['count']
		winrate_by_minute[(int(x['minute_bought']) + 1)] = x['winrate']*100

	m_client.close()

	#minutes = ['Minutes']
	#for x in range(71):
	#	minutes.append(x)
	####End Calculations####


	stats = {	'kpmbb':kpmbb,'kpmab':kpmab,'apmbb':apmbb,'apmab':apmab,'dpmbb':dpmbb,'dpmab':dpmab,'bpmbb':bpmbb,'bpmab':bpmab, 'item_name' : item_name,
				'buys_by_minute': buys_by_minute, 'winrate_by_minute' : winrate_by_minute, 'dkpm' : (kpmab - kpmbb), 'dapm' : (apmab - apmbb), 
				'ddpm' : (dpmab - dpmbb), 'dbpm' : (bpmab - bpmbb), 'item_id': item_id}

	return render_to_response('apisite/item_details.html', stats)