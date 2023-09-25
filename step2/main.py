import socket

from fastapi import FastAPI
import requests
import json
from redis import Redis
import uvicorn
from pydantic import BaseModel


class URL(BaseModel):
    url: str


with open('config.json') as json_config_file:
    config_data = json.load(json_config_file)

project_host = config_data['PROJECT_HOST']
project_port = config_data['PROJECT_PORT']
time = config_data['TIME']
api_route = config_data['API_ROUTE']
redis_host = config_data['REDIS_HOST']
redis_port = config_data['REDIS_PORT']
api_key = config_data['API_KEY']
workspace = config_data['WORKSPACE']

app = FastAPI()
redis = Redis(host=redis_host, port=redis_port)


def send_request_to_rebrandly(link):
    is_cached = True
    # async def send_request_to_rebrandly(link):
    if not redis.exists(link):
        is_cached = False
        link_request = {
            "destination": link
            , "domain": {"fullName": "rebrand.ly"}
        }

        request_headers = {
            "Content-type": "application/json",
            "apikey": api_key,
            "workspace": workspace
        }

        resp = requests.post(api_route,
                             data=json.dumps(link_request),
                             headers=request_headers)
        if resp.status_code == requests.codes.ok:
            link = resp.json()
            redis.setex(link["destination"], time, link["shortUrl"])
            print("Long URL was %s, short URL is %s" % (link["destination"], link["shortUrl"]))
            shorted_url = redis.get(link["destination"]).decode('utf-8')
            return {'longUrl': link["destination"], 'shortUrl': shorted_url, 'isCached': is_cached,
                    'hostname': socket.gethostname()}

    shorted_url = redis.get(link).decode('utf-8')
    return {'longUrl': link, 'shortUrl': shorted_url, 'isCached': is_cached,
            'hostname': socket.gethostname()}


@app.post('/')
async def post_link(url: str):
    resp_json = send_request_to_rebrandly(url)
    # resp_json = await send_request_to_rebrandly(link)

    # send_request_to_rebrandly(link)

    return resp_json


@app.get("/flush_cache")
async def flush():
    redis.flushdb()


if __name__ == '__main__':
    uvicorn.run("main:app", host=project_host, port=project_port)
