from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns

api_key = 'AIzaSyAV8jYStWCSe6hM1qXk9rHs1Z6km0InkQU'
#channel_id = 'UCNU_lfiiWBdtULKOw6X0Dig'
channel_ids = ['UCNU_lfiiWBdtULKOw6X0Dig', #Krish Naik
             'UC59K-uG2A5ogwIrHw4bmlEg', #Telusko
              'UCkGS_3D0HEzfflFnG0bD24A', #My Sirji
             'UCb1GdqUqArXMQ3RS86lqqOw'] #iNeuron channel

youtube = build('youtube', 'v3', developerKey=api_key)

##Function to get channel statistics

def get_channel_stats(youtube, channel_ids):
    all_data = []
    requests = youtube.channels().list(
        part='snippet, contentDetails,statistics',
        id=','.join(channel_ids))
    response = requests.execute()

    for i in range(len(response['items'])):
        data = dict(channel_Name=response['items'][i]['snippet']['title'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_Videos=response['items'][i]['statistics']['videoCount'],
                    playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])

        all_data.append(data)

    return all_data

get_channel_stats(youtube,channel_ids)

#def get_videos_ids(youtube,playlist_id):

channel_statistics= get_channel_stats(youtube,channel_ids)

channel_data = pd.DataFrame(channel_statistics)

playlist_id = channel_data.loc[channel_data['channel_Name']=='Telusko', 'playlist_id'].iloc[0]

def get_videos_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50)

    response = request.execute()

    videos_ids = []

    for i in range(len(response['items'])):
        videos_ids.append(response['items'][i]['contentDetails']['videoId'])

    next_page_token = response['nextPageToken']
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)

            response = request.execute()

            for i in range(len(response['items'])):
                videos_ids.append(response['items'][i]['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')

    return videos_ids

video_ids = get_videos_ids(youtube,playlist_id)



#Function To get Video Details

def get_video_details(youtube, video_ids):
    all_video_stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i + 50]))
        response = request.execute()

        for video in response['items']:
            video_stats = dict(Title=video['snippet']['title'],
                               Publised_date=video['snippet']['publishedAt'],
                               Views=video['statistics']['viewCount'],
                               Likes=video['statistics']['likeCount'],
                               Comments=video['statistics']['commentCount']
                               )

            all_video_stats.append(video_stats)

    return all_video_stats

video_details=get_video_details(youtube, video_ids)

video_data = pd.DataFrame(video_details)

video_data['Publised_date'] = pd.to_datetime(video_data['Publised_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])


video_data.to_csv('Video_Details(Telusko).csv')