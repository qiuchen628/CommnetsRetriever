"""
retrive youtube information from provided youtube ID
"""
import os
import pickle
import time
import urllib
from datetime import datetime, timezone

from dateutil.parser import parse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import urllib.request as request
import json
import urllib3
import pandas as pd
import re

from system_logger import my_logger

CLIENT_SECRETS_FILE = "client_secret_232775461488-81656ltbgcc2g18gb8pkd8j9oegsgji1.apps.googleusercontent.com.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
API_KEY = ''
RAW_DATA = 'data/test_samples.csv'

logger_video_id = my_logger(log_name="get_video_id", level="debug".upper())
logger_video_analysis = my_logger(log_name="video_analysis", level="debug".upper())


def extend_short_url(short_url):
    return urllib3.urlopen(short_url)


def get_ad_age(ads_post_time):
    format = "%Y-%m-%dT%H:%M:%S%z"
    datetime_obj = datetime.strptime(ads_post_time, format)
    datetime_obj.strftime(format)
    now = datetime.now(timezone.utc)
    age = str(now - datetime_obj)
    words = age.split(" ")
    return words[0]


def is_weekend(week_num):
    if week_num <= 5:
        return 0
    else:
        return 1


def get_duration_seconds(raw_duration):
    minute = re.search('PT(.*)M', raw_duration)
    if 'M' in raw_duration:
        second = re.search('M(.*)S', raw_duration)
        total_sec = int(minute.group(1)) * 60 + int(second.group(1))
    else:
        matched_sec = re.search('PT(.*)S', raw_duration)
        total_sec = int(matched_sec.group(1))
    return total_sec


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


def get_video_id(url):
    try:
        if url.startswith("https://youtu.be"):
            video_id = url[17:]
            print('url', video_id)
            return video_id
        else:
            if type(url) is str:
                video_id = url.split("=")[1]
                logger_video_id.info(f"{url}, type: str, video_id: {video_id}")
            else:
                video_id = url.url.split("=")[1]
                logger_video_id.info(f"{url.url}, type: url obj, video_id: {video_id}")
            return video_id
    except Exception as e:
        logger_video_id.error(f"{e}, {url}, type of url: {type(url)}")
        return None


if __name__ == '__main__':
    df = pd.read_csv(RAW_DATA)
    list_of_youtubeID = list(df['Example_Youtube_Link'])
    list_size = len(list_of_youtubeID)
    tmp_dict = dict()
    res = "./files"
    for i in range(list_size):
        try:
            tmp_dict = dict()
            video_id = get_video_id(list_of_youtubeID[i])
            print("video id is: ", video_id)
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            print("https://www.youtube.com/watch?v=" + video_id)  # Here the videoID is printed
            service = get_authenticated_service()
            comments, like_count_temp = get_video_comments(service, part='snippet', videoId=video_id, textFormat='plainText')
            SpecificVideoID = video_id
            SpecificVideoUrl = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id=' + SpecificVideoID + '&key=' + API_KEY
            response = request.urlopen(SpecificVideoUrl)
            videos = json.load(response)  # decodes the response so we can work with it
            for video in videos['items']:
                try:
                   if video['kind'] == 'youtube#video':
                     print("video id: " + SpecificVideoID)
                     tmp_dict['videoID'] = SpecificVideoID
                     print("Number of views:    " + video['statistics']['viewCount'])
                     tmp_dict['viewCnt'] = video['statistics']['viewCount']
                     print("Number of likes:    " + video['statistics']['likeCount'])
                     tmp_dict['likeCount'] = video['statistics']['likeCount']
                     print("Number of dislikes: " + video['statistics']['dislikeCount'])
                     tmp_dict['dislikeCount'] = video['statistics']['dislikeCount']
                     print("Number of comments: " + video['statistics']['commentCount'])
                     tmp_dict['commentCount'] = video['statistics']['commentCount']
                     tmp_dict['comments'] = comments
                     # print("subscriberCount: " + video['statistics']['subscriberCount'])
                     # tmp_dict['subscriberCount'] = video['statistics']['subscriberCount']
                     print("Duration of video (sec): ", get_duration_seconds(video['contentDetails']['duration']))
                     tmp_dict['duration'] = get_duration_seconds(video['contentDetails']['duration'])
                     print("Posted date:" + video['snippet']['publishedAt'][:10])
                     tmp_dict['posted_date'] = video['snippet']['publishedAt'][:10]
                     print("Video age (day):", get_ad_age(video['snippet']['publishedAt']))
                     tmp_dict['video_age'] = get_ad_age(video['snippet']['publishedAt'])
                     tmp_date = video['snippet']['publishedAt'][:10]
                     get_date_obj = parse(tmp_date)
                     tmp_dict['weekend'] = is_weekend(get_date_obj.isoweekday())
                     print('Weekend:', is_weekend(get_date_obj.isoweekday()))

                     channel_id = video["snippet"]["channelId"]
                     tmp_dict["channel_id"] = channel_id

                     channel_url = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id="+f"{channel_id}&key="+f"{API_KEY}"
                     rep_channel = urllib.request.urlopen(channel_url).read().decode("utf-8")
                     rep_channel_json = json.loads(rep_channel)
                     subscriberCount = rep_channel_json["items"][0]["statistics"]["subscriberCount"]
                     print(f"subscriberCount: {subscriberCount}")
                     tmp_dict["subscriberCount"] = subscriberCount

                     if not os.path.isdir(res):
                         os.mkdir(res)
                     with open(os.path.join(res, SpecificVideoID + '.json'), 'w') as fp:
                         json.dump(tmp_dict, fp, indent=4)
                except Exception as e:
                    print(e)
                    pass
        except Exception as e:
            print(e)
            pass
    print(f"total url count: {list_size}, ")
