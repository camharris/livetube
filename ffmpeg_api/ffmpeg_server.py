import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.logger import logger
from pydantic import BaseModel
import requests
import shlex 
import subprocess
import logging
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

logger.setLevel(logging.DEBUG)
IPFS_GW='https://ipfs.io/ipfs/{}'
API_KEY = os.getenv('LIVEPEER_API_KEY')
API_URL = 'https://livepeer.com/api/{}'
headers = {
    'content-type': 'application/json',
    'authorization': 'Bearer {}'.format(API_KEY)
}

db = []

app = FastAPI()

class Stream(BaseModel):
    name: str
    cid: str


profiles = [
  {
    'name': '720p',
    'bitrate': 2000000,
    'fps': 30,
    'width': 1280,
    'height': 720
  },
  {
    'name': '480p',
    'bitrate': 1000000,
    'fps': 30,
    'width': 854,
    'height': 480
  },
  {
    'name': '360p',
    'bitrate': 500000,
    'fps': 30,
    'width': 640,
    'height': 360
  }
]



def stream_video(stream_key, cid):
  ingest_endpoint = get_endpoints()[0]['ingest']
  
  logger.info("Preparing to stream video")

  #Run ffmpeg
  file_input = IPFS_GW.format(cid)
  stream_output = "{}/{}".format(ingest_endpoint,stream_key)

  ffmpeg_command = 'ffmpeg -re -i "{}" -c:v h264 -c:a aac -f flv {}'.format(file_input, stream_output)   

  process = subprocess.run(shlex.split(ffmpeg_command))

  return True



@app.get('/endpoints')
def get_endpoints():
  r = requests.get(
    API_URL.format('ingest'),
    headers=headers,
  )
  data = r.json()
  return data

  


@app.post('/streams/')
async def create_stream(stream: Stream, background_tasks: BackgroundTasks):

    r = requests.post(
        API_URL.format('stream'),
        headers=headers,
        json ={
            'name': stream.name,
            'profiles': profiles,
        })

    data = r.json()
    if r.status_code == 201:
        data = r.json()

        # Extract stream key
        stream_key = data['streamKey']

        background_tasks.add_task(stream_video, stream_key, stream.cid)

        return data
    
    else: 
        raise HTTPException(
          status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't reach livepeer api"
        )
    
    
