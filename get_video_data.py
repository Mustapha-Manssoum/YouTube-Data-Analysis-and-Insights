import config
import logging
import json
import requests
from urllib.parse import unquote
import math
import re


url_videos = 'https://www.googleapis.com/youtube/v3/videos'
google_api_key = config.google_api_key


def get_id_video(url_video):
    # decode the url 
    decoded_video_url = unquote(url_video)
    # define a regEx to match the video id
    pattern = r'v=([A-Za-z0-9_-]+)'
    match = re.search(pattern, decoded_video_url)

    if match:
        return match.group(1)
    else:
        print('Video ID not found in the URL') 
        return 0


def fetch_videos_page(google_api_key, video_id, Page_token=None):

    params = {'key': google_api_key, 'id': video_id, 
              'part': 'snippet, statistics, contentDetails, topicDetails', 'pageToken': Page_token}
    response = requests.get(url_videos, params=params)
    payload = json.loads(response.text)
  
    logging.debug(f'Got {response.text}')

    return payload

def iso8601_to_minutes(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    
    if match:
        hours = int(match.group(1) or 0)
        # print(f'hours : {hours}')
        minutes = int(match.group(2) or 0)
        # print(f'minutes : {minutes}')
        seconds = int(match.group(3) or 0)
        # print(f'seconds : {seconds}')
        
        # Calculate total minutes
        total_minutes = (hours * 60) + minutes + (seconds / 60)
        return total_minutes
    
    return None


def get_important_video_data(video_url):
    # print(video_url)
    video_id = get_id_video(video_url)
    video_data = fetch_videos_page(google_api_key, video_id)
    if len(video_data['items']) == 0:
        return math.nan
    

    content_details = video_data['items'][0].get('contentDetails', {})
    # duration of the video
    duration = content_details.get('duration', 'Duration Not Available')
    duration = iso8601_to_minutes(duration)
    # title of the video
    title = video_data['items'][0]['snippet'].get('title', {})
    # tags of the video
    tags = video_data['items'][0]['snippet'].get('tags', {})
    # topic of the video
    topic_category = video_data['items'][0].get('topicDetails', {})

    if len(topic_category) == 0:
        topic_url = {}
    else:
        topic_url = topic_category.get('topicCategories', {})
        topic_url = video_data['items'][0]['topicDetails'].get('topicCategories', {})

    pattern = r'([^/]+)$'
    topic_list = [re.search(pattern, item).group() for item in topic_url if re.search(pattern, item)]

    return duration, title, tags, topic_list



