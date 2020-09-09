import json
import os
import pickle
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import urllib.request as request
import json #for decoding a JSON response

CLIENT_SECRETS_FILE = "/Users/chenqiu/PycharmProjects/youtube_crawl/credentials/client_secret_283593393384-frf5vkgvktm3um2lunjqqk0em0a9g7kd.apps.googleusercontent.com.json" # for more information  to create your credentials json please visit https://python.gotrained.com/youtube-api-extracting-comments/
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
API_KEY= 'AIzaSyBDn1hjcn0_P3AFP12IEeRScbPcFq5MnsI'

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
        print(results)
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
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    #service = get_authenticated_service()
    #videoId = input('Enter Video id : ') # video id here (the video id of https://www.youtube.com/watch?v=vedLpKXzZqE -> is vedLpKXzZqE)
    #comments, like_count_temp = get_video_comments(service, part='snippet', videoId=videoId, textFormat='plainText')

    #print(len(comments), comments)
    #print(len(like_count_temp), like_count_temp)


    print ("https://www.youtube.com/watch?v=" + 'YeX8uT0HOVk')  # Here the videoID is printed
    SpecificVideoID = 'YeX8uT0HOVk'
    SpecificVideoUrl = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id=' + SpecificVideoID + '&key=' + API_KEY
    response = request.urlopen(SpecificVideoUrl)

    videos = json.load(response)  # decodes the response so we can work with it
    videoMetadata = []  # declaring our list
    for video in videos['items']:
      if video['kind'] == 'youtube#video':
        print("Upload date:        " + video['snippet']['publishedAt'])  # Here the upload date of the specific video is listed
        print("Number of views:    " + video['statistics']['viewCount'])  # Here the number of views of the specific video is listed
        print("Number of likes:    " + video['statistics']['likeCount'])  # etc
        print("Number of dislikes: " + video['statistics']['dislikeCount'])
        print("Number of favorites:" + video['statistics']['favoriteCount'])
        print("Number of comments: " + video['statistics']['commentCount'])
        print ("\n")