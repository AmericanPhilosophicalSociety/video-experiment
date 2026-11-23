import csv
import requests
import time
import os
from requests.auth import HTTPBasicAuth

"""
Script for taking video node IDs and getting associated service file URLs. Needs Diglib credentials to query media API, but not get-service-files API as of 4/13/26. Put these in your .env file as DIGLIB_USERNAME and DIGLIB_PASSWORD.

This will run on every node ID in videos.csv. Outputs a file named urls.txt. Copy/paste the contents of this file into the service_file column in videos.csv and spot check a few to verify that matches are correct.
"""

def connect_drupal():
    username = os.environ.get('DIGLIB_USERNAME')
    password = os.environ.get('DIGLIB_PASSWORD')

    # print(username)

    auth = HTTPBasicAuth(username, password)
    
    s = requests.session()
    s.auth = auth

    return s

def query_api(nid, session):
    time.sleep(1)

    r_mid = requests.get(f'https://diglib.amphilsoc.org/admin/get-service-files/{nid}')
    # print("Response from get-service-files API:")
    # print(r_mid.text) # Print the response text
    r_mid.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    mid = r_mid.json()[0]['mid']
    # print(f"mid: {mid}")

    time.sleep(1)

    r_service = session.get(f'https://diglib.amphilsoc.org/media/{mid}?_format=json')
    
    # print("Response from media API:")
    # print(r_service)
    # print(r_service.text) # Print the response text
    r_service.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    data = r_service.json()
    service_url = data['field_media_video_file'][0]['url']

    time.sleep(1)

    return service_url

# output list of service files
def get_service():
    with open('videos.csv', encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile)
        service_urls = []
        for row in reader:
            url = ""
            if row['node']:
                try:
                    session = connect_drupal()
                    url = query_api(row['node'], session)
                    print(f"Match found: video {row['title']}")
                except Exception as e:
                    print(f"an exception occurred: video {row['title']}")
                    print(e)
                    # print("an exception occurred")
                service_urls.append(url)

    with open('urls.txt', 'a') as textfile:
        for url in service_urls:
            textfile.write(f'{url}\n')

if __name__ == "__main__":
    get_service()