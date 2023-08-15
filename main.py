import time
import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import pandas as pd
import re
from re_check import extract_address_info



        
logger = logging.getLogger(name='MyLog')
logger.setLevel(logging.INFO) ## 경고 수준 설정

# log 의 format 
formatter = logging.Formatter('|%(asctime)s||%(name)s||%(levelname)s|\n%(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S'
                            )

stream_handler = logging.StreamHandler() ## 스트림 핸들러 생성
stream_handler.setFormatter(formatter) ## 텍스트 포맷 설정
logger.addHandler(stream_handler) ## 핸들러 등록

# log file 에 로그들을 모두 저장하고 싶을 때
logging.basicConfig(filename='myinfo.log',level=logging.INFO)



def juso_model(input_text):
    device = torch.device('mps:0' if torch.backends.mps.is_available() else 'cpu')
    model_ckpt = './model'
    model = AutoModelForSeq2SeqLM.from_pretrained(model_ckpt)
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
    
    text_cleaned = re.sub(r'[^\w\s()-]', '', input_text)
    
    inputs = tokenizer(text_cleaned, return_tensors="pt", max_length=64, padding='longest')
    koreans = model.generate(
        **inputs,
        max_length=64,
        num_beams=3,
    )

    preds = tokenizer.batch_decode( koreans, skip_special_tokens=True )
    output = preds[0]
    
    return output

def check_juso(ori_input, model_output):
    re_road_name,  re_city_name = extract_address_info(ori_input)
    #md_building_number, md_road_name, md_gil_name , md_city_name, md_si_name, md_province_name = extract_address_info(model_output)
    
    if re_road_name :
        result = model_output
    else:
        result = re.sub(r'\s*(\S+(로|대로|-ro|-daero)\b)','',model_output)


    if not re_city_name :
        result = re.sub(r'\s*(\S+(?:구)\b|\s*(\S+(?:gu)))','',result)
        
    if re_road_name and re_city_name:
        parts = model_output.split()
        new_parts = parts[1:]
        result = ' '.join(new_parts)
    return result

def fin_juso_model(input):
    model_output = juso_model(input)
    ori_input = input
    checked_juso = check_juso(ori_input,model_output)
    
    return checked_juso


if __name__ == '__main__':
            
    #input_text = list(pd.read_csv('sample_data.csv')['input'].str.replace(pat=r'[^\w\s()-]', repl=r'', regex=True))
    input_text = "111 Haneul-gil Gangseo-gu Seoul Domestic Parking 대기 Room"

    start = time.time()
    output = juso_model(input_text)
    checked_juso = fin_juso_model(input_text)
    re_road_name, re_city_name, result = check_juso(input_text, output)
    print(re_road_name, re_city_name)
    print(result)
    #print(checked_juso)
    end = time.time()
    sec = end - start
    print(f'{sec} sec')
