import pandas as pd
import glob, os, json
import datetime
import bisect

# Generate list of songs that's played the number of times specified
def on_repeat(times_played, music_df):
    last_song = ""
    count = 0
    repeat_list = []

    times_played -= 2
    for song in music_df["song"]:
        if count >= times_played and last_song == song and song not in repeat_list:
            print(count, times_played)
            repeat_list.append(song)
            count = 0

        if last_song != song:
            count = 0
        else:
            count += 1

        last_song = song

    print(repeat_list)


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

# Sort months chronologically.  NOT SURE IF THIS IS WORKING NOV 19th 
places_json = sorted(places_json, key = lambda i: i['placeVisit']['duration']['startTimestampMs'] )


# flatten json location to df
location_name_list = []
for place in places_json:
    temp_dict = {}
    temp_dict.update({'startTimestamp': ( float(place['placeVisit']['duration']['startTimestampMs'])/1000 ) })
    temp_dict.update({'endTimestamp': ( float(place['placeVisit']['duration']['endTimestampMs'])/1000 ) })
    temp_dict.update({'name': place['placeVisit']['location']['name']})
    location_name_list.append(temp_dict)

location_name_df = pd.DataFrame(location_name_list)
location_name_df.sort_values(['startTimestamp'], inplace=True)
# This changes the df, but doesn't actually completly sort it

music_df = pd.read_csv(r'Data\lastfm.csv', names=['artist', 'album', 'song', 'date'])

# Convert lastfm time string to timestamp like google has
music_df['timestamp'] = music_df['date'].apply(lambda date: datetime.datetime.timestamp(datetime.datetime.strptime(date, '%d %b %Y %H:%M')))

# Call this to get repeated songs
# on_repeat(2, music_df)

# Sorts songs by place listened
songsInPlace = {}
for index, song in music_df.iterrows():
    bi = bisect.bisect(location_name_df['startTimestamp'].tolist(), song['timestamp'])

    if ( (bi > 1) and (song['timestamp'] > location_name_df['startTimestamp'][bi-1]) and (song['timestamp'] < location_name_df['endTimestamp'][bi-1]) ):
        
        if location_name_df['name'][bi - 1] not in songsInPlace:
            songsInPlace[location_name_df['name'][bi - 1]] = [song]
        else:
            # Append song to existing dict value list
            songsInPlace[location_name_df['name'][bi - 1]].append(song)

# Ranks songs in each place
for place_key in songsInPlace:
    print("##################################")
    print(place_key)
    played_in_place_counter = {}
    top_songs_in_place = []
    for song in songsInPlace[place_key]:
        if song['song'] in played_in_place_counter.keys():
            played_in_place_counter[song['song']] += 1
        else:
            played_in_place_counter[song['song']] = 1
        ordered_played_in_place_counter = sorted(played_in_place_counter.items(), key=lambda x: x[1], reverse=True)
        top_songs_in_place.append(ordered_played_in_place_counter)
    
    for i in range(0,5):
        if i < len(ordered_played_in_place_counter):
            print(ordered_played_in_place_counter[i])


# TODO: as of nov 19 2020, get this working for all years and not just 2019, 
# I also have a suspician that sumething isn't working right with the songs in the locations so figure out if that is working correctly, bring in new data from lastfm and google













