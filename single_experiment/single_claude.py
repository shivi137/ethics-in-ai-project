

from runner_orchestrator import runModel   #  run model function will be using to run models so import runner orchestra file 
import os
from utils_generalPurpose import deepMergeDicts, tokenUsageInfo   # import from file utils gen purpose to use 2 utility function token usgae info to find how many tokedn are being used in run call and deepmerger dicts to modify extra settings to base llm model 
from api import post   # use to send http post req to llm model provider api 



modelname = "claude-sonnet-5-5"   # name of specific model use in clayude family 
baseUrl = "https://api.anthropic.com/v1/messages"   # base link will add more to form api req link 
extraOptions = {"thinking": {"type": "between_tools"}}   #  aloow between tools context thinlkimg as there is no optionj to close thinking in this model 

keyEnvVar = "anthropic_api_key"   #  key to call  api  

versionNo = "2023-06-01"   # api version alos using while sedn api req 
tag = "claude"   #  identifierr model name 



def callClaude(modelName, system, user, temper, extra, baseUrl, version):   #   funct that will be directlky communuicate to calude model api no filke in between it takes model name of claude , max token claude aloow to use in this exp and also extra seetting think  mode etc also what sys instruction to give claude tro perform task 


    body = { "model": modelName, "max_tokens": 1024, "system": system, "messages": [{"role": "user", "content": user}] }   #   api scall sent to calude will have request and it is theh body of req mainly having theh task messsage sysy inst and msg tokens 

    
    if temper is not None:                      
        body["temperature"] = temper    #  if no temp given then fine else if temp given add that to body temp tells how random or fluactuating will be and of llm to a ques

    
    body = deepMergeDicts(body, extra)                  #    there are base setting and merge those base setting to extar specific  seettings for llm like think token etc 

    
    headers = {"x-api-key": os.environ[keyEnvVar], "anthropic-version": version }   #  https headers needed for sending api req have cruicla private info like api key 

    
    responseOfClaudeApi = post(baseUrl, headers, body)                     #   Send request to claude using post function of another file and also get raw resp saved in the variable 

    
    t = ""                                                                         

    for x in responseOfClaudeApi["content"]:                              #   claude sent mamy blocks in response loop over and select only which is text and not any othewr format  extract text from those blocks and add in dict t by keys 
        if x.get("type") == "text":
            t += x.get("text", "")

    
    u = responseOfClaudeApi.get("usage") or {}                         #    see how much token usage info take out from text 

    
    metaDataDict = {                                                 
        "finish": responseOfClaudeApi.get("stop_reason"),
        "blocked": responseOfClaudeApi.get("stop_reason") == "refusal",
        "usage": tokenUsageInfo(
            u.get("input_tokens"),
            u.get("output_tokens")
        ),
        "resp_model": responseOfClaudeApi.get("model")
}    #   about claude resp some maeta data finish tells why response ended blocks check that if claude not gave resp and said wont give resp model tells model name in resp to chacek if its thehsame model that sent in api req usgae receives and put in format the no of token use in input req and no in output reply 

    
    isThink = False   

    for block in responseOfClaudeApi["content"]:          #    see in all the block of content by calude that if there is some info about thinking howothinked about the ans and dec label also check if think is normal or redacred                                                  
        if block.get("type") == "thinking" or block.get("type") == "redacted_thinking":
            isThink = True

    return t, isThink, metaDataDict   # return text reply and think was there or not and other metadat like finish block etc 


def modelSpecificCall(system, user, temp):   #  funct runner ewill use to call to claude api takes theh sys prpmpt instructins and the user msg text that have to ask by claude and tem controls 

    return callClaude(modelname, system, user, temp, extraOptions, baseUrl, versionNo)



if __name__ == "__main__":   # run only if its call by this file direct not importing this file to other file 
    runModel(tag, modelname, modelSpecificCall, extraOptions, keyEnvVar)