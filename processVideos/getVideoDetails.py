import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
import time
import pandas as pd
from ReadData.readData import IDFromLink
import os
from dotenv import load_dotenv
load_dotenv() 
import streamlit as st
formatter = JSONFormatter()

api_key = os.getenv("API_KEY")
#api_key = st.secrets["api_key"] # new api method
#api_key='AIzaSyCJvI_udalHYzy-qr7CcFYYOA6Rcqh_P2o'

def getVidDetails(video_id):
    """
    Fetches video metadata, statistics, and transcript from the YouTube Data API v3.
    
    Parameters:
    - video_id (str): The YouTube video ID.
    - api_key (str): The API key to authenticate with the YouTube API.
    
    Returns:
    - dict: A dictionary containing video details like title, publish date, statistics, 
            max resolution thumbnail, and the video transcript.
    """
    base_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics", # Fetches statistics
        "id": video_id, 
        "key": api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    
    # Check if the 'items' key exists in the API response
    if not data.get("items"):
        print("Error:", data)
        return None
    
    title = data["items"][0]["snippet"]["title"]
    published_at = data["items"][0]["snippet"]["publishedAt"]
    statistics = data["items"][0]["statistics"]
    
    # Get the max resolution thumbnail
    thumbnails = data["items"][0]["snippet"]["thumbnails"]
    maxres_thumbnail = thumbnails.get("maxres", {}).get("url")
    if not maxres_thumbnail:
        # Fallback to other resolutions if maxres is not available
        maxres_thumbnail = thumbnails.get("high", {}).get("url") or thumbnails.get("medium", {}).get("url")

    # Get the transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatted_transcript = formatter.format_transcript(transcript)
        print(formatted_transcript)
    except:
        formatted_transcript = None

    return {
        "videoId": video_id,
        "title": title,
        "publishedAt": published_at,
        "statistics": statistics,
        "maxresThumbnail": maxres_thumbnail,
        "transcript": formatted_transcript
    }

import time

def multipleVideoDetails(video_ids): #add your api key
    all_video_details = []
    failed_video_ids = []

    for video_id in video_ids:
        print(f"Processing video ID: {video_id}")
        try:
            details = getVidDetails(video_id)
            if details:  # Check if details is not None
                all_video_details.append(details)
        except Exception as e:
            print(f"Failed to retrieve details for video ID: {video_id}. Reason: {e}")
            failed_video_ids.append(video_id)
        time.sleep(2)

    # Convert the list of video details to a DataFrame
    df = pd.DataFrame(all_video_details)

    # Return the DataFrame and the list of failed video IDs
    return df, failed_video_ids

def flattenColumn(df, column = 'statistics'):
    statsDF = pd.json_normalize(df[column])
    # Merge the flattened DataFrame with the original DataFrame
    df = df.join(statsDF)
    df['publishedAt'] = pd.to_datetime(df['publishedAt']).dt.strftime('%d/%m/%Y')

    # Drop the original 'statistics' column
    df.drop('statistics', axis=1, inplace=True)
    return df



def videoMetaData(oneOrMoreLinks):
    if isinstance(oneOrMoreLinks, str):
        videoID = IDFromLink(oneOrMoreLinks)
        holderList = [videoID]
        videoData = multipleVideoDetails(holderList)[0]
        print(type(videoData))
        videoData = flattenColumn(videoData)
        return videoData
    elif isinstance(oneOrMoreLinks, list):
        linksToURL = []
        for i in oneOrMoreLinks:
            i = IDFromLink(i)
            linksToURL.append(i)
        print("links to urls", linksToURL)
        details = multipleVideoDetails(linksToURL)[0]
        print(type(details))
        details = flattenColumn(details)
        print(details)
        return details
