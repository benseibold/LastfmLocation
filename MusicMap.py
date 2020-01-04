import pandas as pd
import glob, os, json

location_path = r'GoogleData1-1-2020\Location History\Semantic Location History\2019'
all_files = glob.glob(os.path.join('', "*.json"))

full_location_json = []
for f in glob.glob(os.path.join(r'GoogleData1-1-2020\Location History\Semantic Location History\2019', "*.json")):
    print(f)
    with open(f) as i:
        full_location_json.append(json.load(i))

places_json = []
for month in full_location_json:
    for activity in month["timelineObjects"]:
        for n in activity:
            if(n == 'placeVisit'):
                places_json.append(activity)
                print(activity['placeVisit']['location']['name'], activity['placeVisit']['duration'])

music_df = pd.read_csv('lastfm.csv')




