import pandas as pd
import glob, os, json
import datetime

location_path = r'Data\GoogleData1-1-2020\Location History\Semantic Location History\2019'
all_files = glob.glob(os.path.join('', "*.json"))

full_location_json = []
for f in glob.glob(os.path.join(r'Data\GoogleData1-1-2020\Location History\Semantic Location History\2019', "*.json")):
    with open(f) as i:
        full_location_json.append(json.load(i))

# Get just the activities for visited places
places_json = []
for month in full_location_json:
    for activity in month["timelineObjects"]:
        for n in activity:
            if(n == 'placeVisit'):
                places_json.append(activity)

music_df = pd.read_csv(r'Data\lastfm.csv', names=['artist', 'album', 'song', 'date'])

# Convert lastfm time string to timestamp like google has
music_df['timestamp'] = music_df['date'].apply(lambda date: datetime.datetime.timestamp(datetime.datetime.strptime(date, '%d %b %Y %H:%M')))

# flatten json location to df
location_name_list = []
for place in places_json:
    temp_dict = {}
    temp_dict.update({'startTimestamp': place['placeVisit']['duration']['startTimestampMs']})
    temp_dict.update({'endTimestamp': place['placeVisit']['duration']['endTimestampMs']})
    temp_dict.update({'name': place['placeVisit']['location']['name']})
    location_name_list.append(temp_dict)

location_name_df = pd.DataFrame(location_name_list)
location_name_df.sort_values(by=['startTimestamp'])


print(location_name_df)

# print(music_df)







