from enum import Enum
from typing import List, Optional, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from juso_api_eng import translate_juso

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


@app.post('/process_request')
async def process_request(request: ClientRequest):
    body_data_list = []
    for individual_request in request.requestList:
        request_address = individual_request.requestAddress
        translated_juso = translate_juso(request_address)
        if not translated_juso:  
            # Return the FailureResponse
            failure_header = Header(RESULT_CODE=ResultCode.FAILURE, RESULT_MSG=f"seq {individual_request.seq} is failed to transfer")
            raise HTTPException(status_code=400, detail={"HEADER": failure_header.dict()})
        
        body_data_list.append(BodyData(seq=individual_request.seq, resultAddress=translated_juso))
        
    response_header = Header(RESULT_CODE=ResultCode.SUCCESS, RESULT_MSG="Success")  # Sample header
    return SuccessResponse(HEADER=response_header, Body=body_data_list)

if __name__ == "__main__":
    uvicorn.run("api:app",host="127.0.0.1",port=5000,log_level='info')