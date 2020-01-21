import pandas as pd
import glob, os, json
import datetime
import bisect

location_path = r'Data\GoogleData1-1-2020\Location History\Semantic Location History\2019'
all_files = glob.glob(os.path.join('', "*.json"))

full_location_json = []
for f in glob.glob(os.path.join(r'Data\GoogleData1-1-2020\Location History\Semantic Location History\2019', "*.json")):
    with open(f) as i:
        full_location_json.append(json.load(i))
        #full_location_json.append(json.load(i))

# Get just the activities for visited places
places_json = []
month = full_location_json[0]
for activity in month["timelineObjects"]:
    for n in activity:
        if(n == 'placeVisit'):
            places_json.append(activity)

# flatten json location to df
location_name_list = []
for place in places_json:
    temp_dict = {}
    temp_dict.update({'startTimestamp': ( float(place['placeVisit']['duration']['startTimestampMs'])/1000 ) })
    temp_dict.update({'endTimestamp': ( float(place['placeVisit']['duration']['endTimestampMs'])/1000 ) })
    temp_dict.update({'name': place['placeVisit']['location']['name']})
    location_name_list.append(temp_dict)

location_name_df = pd.DataFrame(location_name_list)
location_name_df = location_name_df.sort_values('startTimestamp')

# This claims the location_name_df still isn't sorted
# Maybe try one month??
print(location_name_df.index.is_monotonic)

music_df = pd.read_csv(r'Data\lastfm.csv', names=['artist', 'album', 'song', 'date'])

# Convert lastfm time string to timestamp like google has
music_df['timestamp'] = music_df['date'].apply(lambda date: datetime.datetime.timestamp(datetime.datetime.strptime(date, '%d %b %Y %H:%M')))

for index, song in music_df.iterrows():

    bi = bisect.bisect(location_name_df['startTimestamp'].tolist(), song['timestamp'])
    
    if ( (bi > 1) and (song['timestamp'] > location_name_df['startTimestamp'][bi - 1]) and (song['timestamp'] < location_name_df['endTimestamp'][bi - 1]) ):
        print(song)
        print(location_name_df['name'][bi - 1])


print(music_df)









