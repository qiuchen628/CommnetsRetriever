"""
retrive youtube information from provided youtube ID
"""

import os
import pickle
from dateutil.parser import parse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import urllib.request as request
import json
import urllib3
import pandas as pd

CLIENT_SECRETS_FILE = "credentials/client_secret_283593393384-frf5vkgvktm3um2lunjqqk0em0a9g7kd.apps.googleusercontent.com.json" # for more information  to create your credentials json please visit https://python.gotrained.com/youtube-api-extracting-comments/
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
API_KEY = 'AIzaSyBDn1hjcn0_P3AFP12IEeRScbPcFq5MnsI'
RAW_DATA = 'data/raw_table.csv'

def extend_short_url(short_url):
    return urllib3.urlopen(short_url)


def is_weekend(week_num):
    if week_num <= 5:
        return False
    else:
        return True


def get_authenticated_service():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)


def get_video_comments(service, **kwargs):
    comments = []
    comment_id_temp = []
    reply_count_temp = []
    like_count_temp = []
    results = service.commentThreads().list(**kwargs).execute()
    while results:
        for item in results['items']:
          comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
          comment_id_temp.append(item['snippet']['topLevelComment']['id'])
          reply_count_temp.append(item['snippet']['totalReplyCount'])
          like_count_temp.append(item['snippet']['topLevelComment']['snippet']['likeCount'])
        # Check if another page exists
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.commentThreads().list(**kwargs).execute()
        else:
            break
    return comments, like_count_temp


if __name__ == '__main__':
    df = pd.read_csv(RAW_DATA)
    list_of_youtubeID = list(df['Example_Youtube_Link'])
    list_size = len(list_of_youtubeID)
    tmp_dict = dict()
    for i in range(list_size):
        try:
            tmp_dict[i] = dict()
            video_id = list_of_youtubeID[i][17:]
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            print ("https://www.youtube.com/watch?v=" + video_id)  # Here the videoID is printed
            service = get_authenticated_service()
            comments, like_count_temp = get_video_comments(service, part='snippet', videoId= video_id, textFormat='plainText')
            SpecificVideoID = video_id
            SpecificVideoUrl = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id=' + SpecificVideoID + '&key=' + API_KEY
            response = request.urlopen(SpecificVideoUrl)
            videos = json.load(response)  # decodes the response so we can work with it
            for video in videos['items']:
              try:
                  if video['kind'] == 'youtube#video':
                    print("Number of views:    " + video['statistics']['viewCount'])
                    tmp_dict[i]['viewCnt'] = video['statistics']['viewCount']
                    print("Number of likes:    " + video['statistics']['likeCount'])
                    tmp_dict[i]['likeCount'] = video['statistics']['likeCount']
                    print("Number of dislikes: " + video['statistics']['dislikeCount'])
                    tmp_dict[i]['dislikeCount'] = video['statistics']['dislikeCount']
                    print("Number of comments: " + video['statistics']['commentCount'])
                    tmp_dict[i]['commentCount'] = video['statistics']['commentCount']
                    tmp_dict[i]['comments'] = comments
                    print("Duration of video: " + video['contentDetails']['duration'])
                    tmp_dict[i]['duration'] = video['contentDetails']['duration']
                    print("posted date:" + video['snippet']['publishedAt'][:10])
                    tmp_dict[i]['posted_date'] = video['snippet']['publishedAt'][:10]
                    tmp_date = video['snippet']['publishedAt'][:10]
                    get_date_obj = parse(tmp_date)
                    tmp_dict[i]['weekend'] = is_weekend(get_date_obj.isoweekday())
                    print('Weekend:', is_weekend(get_date_obj.isoweekday()))
                    print ("\n")
              except:
                  pass
        except:
            pass
        print(tmp_dict)
    with open('process_data.json', 'w') as fp:
        json.dump(tmp_dict, fp)