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



# bisect sucks, this needs to work with dataframes
def binarySearch(df, item):
    first = 0
    last = df['startTimestamp'].size -1
    found = False

    while first<=last and not found:
        midpoint = (first + last)//2
        # print(df['startTimestamp'][midpoint], item)
        # print(midpoint + 1 >= len(df['startTimestamp']), midpoint < 1)

        
        # if(not(midpoint + 1 >= len(df['startTimestamp']) or midpoint < 1)):
            # print(df['startTimestamp'][midpoint + 1] > item, df['startTimestamp'][midpoint - 1] < item)
            # print("It happened!!", df['startTimestamp'][midpoint + 1], item, df['startTimestamp'][midpoint - 1])

        if not(midpoint + 1 >= len(df['startTimestamp']) or midpoint < 1) and df['startTimestamp'][midpoint + 1] > item and df['startTimestamp'][midpoint - 1] < item:
            print ("MIDPOINT FOUND: ", midpoint, len(df['startTimestamp']), df[midpoint + 1], item )
            return midpoint
        else:
            if item < df['startTimestamp'][midpoint]:
                last = midpoint-1
            else:
                first = midpoint+1

    return 0





location_path = r'Data\GoogleData1-1-2020\Location History\Semantic Location History\2019'
all_files = glob.glob(os.path.join('', "*.json"))

full_location_json = []
for f in glob.glob(os.path.join(r'Data\GoogleData1-1-2020\Location History\Semantic Location History\2019', "*.json")):
    with open(f) as i:
        print(f)
        full_location_json.append(json.load(i))

# Get just the activities for visited places
places_json = []
for month in full_location_json:
    for activity in month["timelineObjects"]:
        for n in activity:
            if(n == 'placeVisit'):
                places_json.append(activity)

# month = full_location_json[1]
# for activity in month["timelineObjects"]:
#     for n in activity:
#         if(n == 'placeVisit'):
#             places_json.append(activity)


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

# Sanity check to see if sorted
# n = 0
# for i in range(location_name_df.shape[0]-2):
#     if not (location_name_df['startTimestamp'][i] < location_name_df['startTimestamp'][i + 1]):
#         n += 1
#         print("ITS ALL FUCKED UP!!!!!!!!!!!!!!!!!!!!!!", location_name_df['startTimestamp'][i], location_name_df['startTimestamp'][i + 1], i)
#         print(location_name_df['startTimestamp'][i -3])
#         print(location_name_df['startTimestamp'][i -2])
#         print(location_name_df['startTimestamp'][i -1])
#         print(location_name_df['startTimestamp'][i])
#         print(location_name_df['startTimestamp'][i + 1])
#         print(location_name_df['startTimestamp'][i + 2])
#         print(location_name_df['startTimestamp'][i + 3])

# print("DONE WITH THE FUCK UPS")

music_df = pd.read_csv(r'Data\lastfm.csv', names=['artist', 'album', 'song', 'date'])

# Convert lastfm time string to timestamp like google has
music_df['timestamp'] = music_df['date'].apply(lambda date: datetime.datetime.timestamp(datetime.datetime.strptime(date, '%d %b %Y %H:%M')))

# on_repeat(2, music_df)

# Sorts songs by place listened
songsInPlace = {}
for index, song in music_df.iterrows():
    bi = bisect.bisect(location_name_df['startTimestamp'].tolist(), song['timestamp'])
    # bi = binarySearch(location_name_df, song['timestamp'])
    # bi = location_name_df['startTimestamp'].searchsorted(song['timestamp'])

    # print(bi, location_name_df['startTimestamp'][bi], song['timestamp'])




    # print(bi, song['timestamp'], location_name_df['startTimestamp'][bi])
    ######################################## DEMONSTRATING HOW FUCKED BISECT IS ###################################
    # if(len(location_name_df['startTimestamp']) > bi + 1 and bi != 0):
    #     print(bi, song['timestamp'], location_name_df['startTimestamp'][bi+1], location_name_df['endTimestamp'][bi+1])
    # if song['timestamp'] == 1554005640:
    #     print(bi)
    # if(location_name_df['startTimestamp'][bi-1] < 1554005640 and location_name_df['endTimestamp'][bi-1] > 1554005640):
    #     print(location_name_df['startTimestamp'][bi-1], location_name_df['endTimestamp'][bi-1], bi -1 )

    ###############################################################################################################


    if bi > 1 and bi < len(location_name_df['startTimestamp']):
        print((song['timestamp'] > location_name_df['startTimestamp'][bi-1]), (song['timestamp'] < location_name_df['endTimestamp'][bi-1]))
        print(location_name_df['startTimestamp'][bi], song["timestamp"], location_name_df['endTimestamp'][bi])

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


# TODO: tolist on a dataframe doesn't maintain order, and I need to stay in a data frame, so I need to bisect it.  Bisect only works on lists and 
# I couldn't get searchsorted working.  Need to get my custom bin search function working with dataframes.  Now, it's returning a bisect of 0 for everything

# Update as of nov 19 2020 - Not sure if the above sorting is working.  Trying to get that fixed then will fix bisect.  Maybe pandas bisect does work and it's just failing bc its not sorted???













