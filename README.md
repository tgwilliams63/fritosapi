# Book of Doubleswords
League API Contest Project
Analyzing items and thowing stats at people

## Requirements
1. Python 2.7
  * pymongo
  * Django 1.8
  * requests

2. Mongodb

3. Websever able to serve Django apps

## Setup

### Configuration files
Doubleswords needs two configuration files to work: a frito.conf file in the processing directory, and a mongo.py file in the same directory as views.py (default is ./apisite/apisite/mongo.py). These configuration files are pretty easy to set up- just make a new text file, paste in the templates, then insert your own database info and api keys.

#### mongo.py
``` python
class mongo_conn:
	mongo_address = 'example.com'
	mongo_port = 27017
	mongo_user = 'username'
	mongo_pass = 'password'
	mongo_db = 'league_api'
```

#### frito.conf
```
[api details]
api_key = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

[mongo details]
mongo_address = example.com
mongo_port = 27017
mongo_user = username
mongo_pass = password
mongo_db = league_api

```

### Getting Match IDs
Because this was made with the API contest in mind, we assume you can pull a random list of match IDs from the API. We merely set up a cron job to run the ```grabUrf.py``` script once every five minutes. If you want to do something more fancy, just stick in the match IDs into the mongodb under the "unprocessed_matches" collection- the processing script will then process those IDs.

### Processing the Matches
For processing the matches and inserting the information into the database, we hve two scripts: ```processMatches.py``` and ```processThreaded.py```. They can be called manually, but we have them called by a cron job after querying the API for the match IDs for simplicity. 
#### Script Differences
You have two options when you need to process the raw match IDs- ```ProcessMatches.py``` and ```ProcessThreaded.py```. These two scripts do the same thing- ```ProcessThreaded.py```, however, passes the API requests into a processing pool. This gives us a massive speed boost compared to ```processMatches.py```, but comes at a cost- retrieving more than a few thousand matches at a time takes a large amount of RAM. ```processMatches.py```, on the other hand, has a much more modest memory requirement, but takes orders of magnitude more time to run. 
To illustrate: ```processThreaded.py``` takes 103 seconds and over 300 mB to process 1000 matches, while processMatches.py takes 405 seconds and only 88 mB of RAM

#### Modifying the Scripts
The scripts are limited to an arbitrary number of matches, defined by the ```limit``` variable. The limit variable is at the top of the file in ```processMatches.py```, but is in the middle of the file for ```processThreaded.py``` due to quirks of the multiprocessing library. The number of worker processes is defined by the ```worker``` variable in ```processThreaded.py``` and the Riot API locations are stored in ```api_url```. The location for querying the API for a specific match is contained in ```match_api_url```.

## Database Layout Information
We use 6 different collections in the database, listed here:
* ```errored_matches``` - list of matches unable to be retrieved for processing
* ```item_avg``` - the average statistics for each item; Has two indexes on the winrate key to sort it by ascending and descending order
* ```item_buy_time``` - the count and winrate average of each item, separated by the minute it was bought
* ```item_buys``` - the collection of the raw information contained in the timeline events of the matches. Don't drop this database. 
* ```item_static``` - the item names and descriptions for the items we care about; makes it quicker to query than the Riot API
* ```unprocessed_matches``` - the queue for keeping track of the match IDs we haven't worked with yet

The entire database is constructed on the fly, with the exception of the two indexes. After running one of the processing scripts, run these two commands in your mongodb database:

db.item_avg.createIndex( { "winrate": 1 } )
db.item_avg.createIndex( { "winrate": -1} )

## Checklist for installing
1. Install the requirements
2. Set up mongodb with a user/password combo
3. Edit the configuration files ```mongo.py``` and ```frito.conf```
4. Configure your web server to use django apps
5. Run ```grabUrf.py```, then run the ```processMatches.py``` or ```processThreaded.py``` scripts once
6. Run the two indexing commands on the mongodb install
7. Start the django app
8. Good to go 