from enum import Enum
from typing import List, Optional, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from juso_api_kor import find_juso_kor
# from main import fin_juso_model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from re_check import extract_address_info
import re

#device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_ckpt = './model'
model = AutoModelForSeq2SeqLM.from_pretrained(model_ckpt)
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)

def juso_model(input_text):    
    text_cleaned = re.sub(r'[^\w\s()%-]', '', input_text)

    inputs = tokenizer(text_cleaned, return_tensors="pt", max_length=64, padding='longest')
    koreans = model.generate(
        **inputs,
        max_length=64,
        num_beams=2,
    )

    preds = tokenizer.batch_decode( koreans, skip_special_tokens=True )
    output = preds[0]
    
    return output

def check_juso(ori_input, model_output):
    re_road_name,  re_city_name = extract_address_info(ori_input)
    #md_building_number, md_road_name, md_gil_name , md_city_name, md_si_name, md_province_name = extract_address_info(model_output)
    yes_or_no = False
    if re.findall(r'\d', ori_input):
        pass
    else:
        result = ''

    if re_road_name :
        result = model_output
    else:
        yes_or_no = True
        result = re.sub(r'(\S+(?:로|대로|길)\b)','',model_output)
    
    if re_city_name :
        pass
    else:
        yes_or_no = True
        result = re.sub(r'\s*(\S+(?:구|군)\b)| \S+(?:시)\b','',result)
        
    if re_road_name and re_city_name:
        parts = model_output.split()
        new_parts = parts[1:]
        result = ' '.join(new_parts)

    return result, yes_or_no

def fin_juso_model(input):
    model_output = juso_model(input)
    ori_input = input
    checked_juso, yes_or_no = check_juso(ori_input, model_output)
    
    return checked_juso, yes_or_no


app = FastAPI(
    title = "CJ API by DSL"
)

#* Request
class ResultCode(str, Enum):
    SUCCESS = "S"
    FAILURE = "F"
    def __str__(self):
        return str(self.value)

class Header(BaseModel):
    RESULT_CODE: ResultCode
    RESULT_MSG: str
    
class IndividualRequest(BaseModel):
    seq: str
    requestAddress: str

class ClientRequest(BaseModel):
    requestList: List[IndividualRequest]

#* Response
class IndividualResponse(BaseModel):
    seq : str
    resultAddress : str

class BodyData(BaseModel):
    seq: str
    resultAddress: str
    
class SuccessResponse(BaseModel):
    HEADER : Header
    Body : List[BodyData]
    
    
class FailureResponse(BaseModel):
    HEADER : Header


@app.post('/request')
async def process_request(request: ClientRequest):
    body_data_list = []
    for individual_request in request.requestList:
        request_address = individual_request.requestAddress
        juso_model_output, yes_or_no = fin_juso_model(request_address)
        real_juso, num = find_juso_kor(juso_model_output)
        if not real_juso:  
            # Return the FailureResponse
            """ failure_header = Header(RESULT_CODE=ResultCode.FAILURE, RESULT_MSG=f"seq {individual_request.seq} is failed to transfer")
            raise HTTPException(status_code=400, detail={"HEADER": failure_header.dict()}) """
            real_juso = '답 없음'
            body_data_list.append(BodyData(seq=individual_request.seq, resultAddress=real_juso))
        elif yes_or_no and num>1:
            real_juso = '답 없음'
            body_data_list.append(BodyData(seq=individual_request.seq, resultAddress=real_juso))
        else:
            body_data_list.append(BodyData(seq=individual_request.seq, resultAddress=real_juso))
        
    response_header = Header(RESULT_CODE=ResultCode.SUCCESS, RESULT_MSG="Success")  # Sample header
    return SuccessResponse(HEADER=response_header, Body=body_data_list)

if __name__ == "__main__":
    #uvicorn.run("api:app",host="15.165.156.212",port=5000,log_level='info')
    uvicorn.run("api:app",host="127.0.0.1",port=5000,log_level='info')