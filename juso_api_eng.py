import requests
import xmltodict
import json
import logging
import os
import yaml
import re
import time # time 라이브러리 import
import pandas as pd
from fastapi import HTTPException
import starlette.status as status


def translate_juso(text):
    url = "https://business.juso.go.kr/addrlink/addrEngApi.do"

    # Parameters  
    confmKey = "U01TX0FVVEgyMDIzMDcyMDIwMDkyNjExMzk0NzY="
    currentPage = 1
    countPerPage = 1
    keyword = text
    resultType = 'xml'

    # Construct the URL with encoded parameters
    params = {
        "confmKey": confmKey,
        "currentPage": currentPage,
        "countPerPage": countPerPage,
        "keyword": keyword,
        'resultType' : resultType
    }
    encoded_params = "&".join([f"{key}={value}" for key, value in params.items()])
    full_url = f"{url}?{encoded_params}"

    # Send the GET request
    response = requests.get(full_url)
    
    if response.status_code == 200:
        xml_data = response.text
        data_dict = xmltodict.parse(xml_data)
        json_data = json.dumps(data_dict, ensure_ascii=False)
        parsed_data = json.loads(json_data)
        #logger.info(json_data)
        totalCount = int(parsed_data['results']['common']['totalCount'])
        if totalCount > 0:
            road_addr = parsed_data['results']['juso']['korAddr']
            return road_addr
        else:
            return None

    else:
        raise HTTPException(status_code = 404)