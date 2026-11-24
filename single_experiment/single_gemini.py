

from runner_orchestrator import runModel   #  run model function will be using to run models so import runner orchestra file 
import os
from utils_generalPurpose import deepMergeDicts, tokenUsageInfo   # import from file utils gen purpose to use 2 utility function token usgae info to find how many tokedn are being used in run call and deepmerger dicts to modify extra settings to base llm model 
import json
from api import post    # use to send http post req to llm model provider api



tag = "gemini"    # identfier model tag
keyEnvVar = "gemini_api_key"     #  key to call  api 
modelname = "gemini-3.5-flash-lite"   # name of specific model use in google gemini  family 
baseUrl = "https://generativelanguage.googleapis.com/v1beta"   # base link will add more to form api req link  
extraOptions = {"generationConfig": {"thinkingConfig": {"thinkingLevel": "minimal"}}}    #  aloow minimumm thinlkimg as there is no optionj to close thinking in this model 



blockedDict = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "RECITATION", "IMAGE_SAFETY"}    # may be some words appear in reply taht telles why gemini has if block the reply if not given response that list if block words  or finish reason


def callGemini(model, system, user, temp, extra, base):    #   funct that will be directlky communuicate to gemini model api no filke in between it takes model name of geminiu ,  and also extra seetting think  mode etc also what sys instruction to give gemini to o perform task 

    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": 1024}
    }   #   api scall sent to gemini will have request and it is theh body of req mainly having theh task messsage sysy inst and mx tokens for output response user msg syst msg 

    if temp is not None:
        body["generationConfig"]["temperature"] = temp      #  if no temp given then fine else if temp given add that to body temp tells how random or fluactuating will be and of llm to a ques

    body = deepMergeDicts(body, extra)    #    there are base setting and merge those base setting to extar specific  seettings for llm like think token etc 

   
    r = post(
        f"{base.rstrip('/')}/models/{model}:generateContent",
        {"x-goog-api-key": os.environ[keyEnvVar]},
        body
    )   #   send post req to gem api model name and content added header has api key and body has user sys msgs remove slash and save reply in r 

  
    um = r.get("usageMetadata") or {}   #   get from reply info about how much tokens used and also in that how many tokend used to think about answer 
    thoughts = um.get("thoughtsTokenCount") or 0

    usage = tokenUsageInfo(
        um.get("promptTokenCount"),
        (um.get("candidatesTokenCount") or 0) + thoughts,
        thoughts
    )   #  token usgae full info total usage and how much tokens used in iput msg and how much tokens used in replying from llm also how much tokesn of thinking added to output token counts only 

   
    candidates = r.get("candidates") or []   #   check if no reponose or emplty respon returned

    if not candidates:   # know why prompt got block by api llm provider the reason or feedback 
        block = (r.get("promptFeedback") or {}).get("blockReason")

        if block:   # if there is reason got from llm why its blocked in dict tell req was blocked and alos mention usagew no think done and finish have theh reason why it ended also mention name of model 
            return "", False, {
                "finish": "blocked:" + str(block),
                "blocked": True,
                "usage": usage,
                "resp_model": r.get("modelVersion")
            }

        raise RuntimeError("no candidates: " + json.dumps(r)[:300])   #   raise error if no block reason only 300 char of that error msg dict to string in json 

    
    parts = (candidates[0].get("content") or {}).get("parts") or []
    finish = candidates[0].get("finishReason")      #  parts of response where it is textr content answer or thinking reasoing in text also finidh reason telling normal or some safetyguard

    
    text = ""
    thinkingUsed = bool(thoughts)    # if toten in thinking more than 0 tehn thinkimng is used by gemini 

    for p in parts:   #  go through reply each part see if think parts or normal parts if think set think true if not then add in text content string i
        if p.get("thought"):
            thinkingUsed = True
        else:
            text += p.get("text", "")

    return text, thinkingUsed, {
        "finish": finish,
        "blocked": finish in blockedDict,
        "usage": usage,
        "resp_model": r.get("modelVersion")
    }   #   give back final text reply , if use thinkng , metadata dict that has use tokens and namme of model to cross verify , reason to finish and if finshed and if blocked and blocking reason  

def modelSpecificCall(system, user, temp):   #  funct runner ewill use to call to gemini api takes theh sys prpmpt instructins and the user msg text that have to ask by gemini and temp controls ste 

    return callGemini(modelname, system, user, temp, extraOptions, baseUrl)    


if __name__ == "__main__":
    runModel(tag, modelname, modelSpecificCall, extraOptions, keyEnvVar)    # run only if its call by this file direct not importing this file to other file 