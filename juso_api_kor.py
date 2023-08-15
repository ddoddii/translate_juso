import requests
import xmltodict
import json
import logging
import os
import yaml
import re
import time 
import pandas as pd
import csv
from main import fin_juso_model, check_juso

start = time.time() # 시작


logger = logging.getLogger(name='MyLog')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('|%(asctime)s||%(name)s||%(levelname)s|\n%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S'
                            )

stream_handler = logging.StreamHandler() 
stream_handler.setFormatter(formatter) 
logger.addHandler(stream_handler) 

logging.basicConfig(filename='myinfo.log',level=logging.INFO)

def find_juso_kor(text):
    
    url = "https://business.juso.go.kr/addrlink/addrLinkApiJsonp.do"

    # Parameters  
    confmKey = "devU01TX0FVVEgyMDIzMDcxODE0MDUxNDExMzkzODk="
    currentPage = 1
    countPerPage = 1
    keyword = text
    resultType = 'json'

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
        json_data = response.text
        json_str = json_data[json_data.index('(') + 1: -1]
        parsed_data = json.loads(json_str)
        
        totalCount = int(parsed_data['results']['common']['totalCount'])
        if totalCount > 0:
            road_addr = parsed_data['results']['juso'][0]['roadAddr']
            return road_addr 
        else:
            return None 
    else:
        print('No mathching result')
        return None 

def process_csv_file(file_path, start, output_file_path = None):
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        header1, header2 = next(csv_reader)
        print(f"Header 1: {header1}, Header 2: {header2}")  
        lines = [(row[0], row[1]) for row in csv_reader]

    num_lines = len(lines)
    print(f"Total number of lines: {num_lines}")

    translations = [] 
    batch_size = 500
    batch = lines[start : start + batch_size]

    for line in batch:
        ori_line, model_out = line
        checked_juso = check_juso(ori_line,model_out)
        #real_juso = check_juso(line)
        translated_text , totalCount= find_juso_kor(checked_juso)
        translations.append([ori_line, model_out,checked_juso, translated_text, totalCount])

    print(f"Processed {min(start, num_lines)} lines out of {num_lines}")
    df_translations = pd.DataFrame(translations, columns=['Original_Text','Model_output','Checked_juso' ,'Juso_API_result','TotalCount'])
    
    #파일 존재하면 아래 추가 
    if output_file_path:
        df_translations.to_csv(output_file_path, mode='a', header=not os.path.exists(output_file_path), index=False, encoding='utf-8-sig')
    else:
        df_translations.to_csv(output_file_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    input_file = 'test8.csv'
    process_csv_file(input_file, start=0, output_file_path='model_kor_output.csv')
