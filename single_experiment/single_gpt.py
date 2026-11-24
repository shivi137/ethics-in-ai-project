

from  runner_orchestrator import runModel   #  run model function will be using to run models so import runner orchestra file 
import os
from utils_generalPurpose import  deepMergeDicts, tokenUsageInfo   # import from file utils gen purpose to use 2 utility function token usgae info to find how many tokedn are being used in run call and deepmerger dicts to modify extra settings to base llm model 
from  api import post   # use to send http post req to llm model provider api


tag = "gpt"   # identfier model tag
modelname = "gpt-6-sol"        # name of specific model use in openai gpt   family 
keyEnvVar = "openai_api_key"      #  key to call  api
extraOptions = {"reasoning": {"effort": "none"}}      #  no effort thinking  as 
baseUrl = "https://api.openai.com/v1"    # base link will add more to form api req link 

def getResponseGpt(modelname, system, user, temp, extraOptions, baseUrl):         #   funct that will be directlky communuicate to gpt model api no filke in between it takes model name of gpt ,  and also extra seetting think  mode etc also what sys instruction to give gpt to o perform task 

    body = {
           "model": modelname,
        "instructions": system,
          "input": user,
           "max_output_tokens": 1024
    }  #   api scall sent to gpt will have request and it is then body of req mainly having theh task messsage sysy inst and mx tokens for output response user msg syst msg model name also 

    if temp is not None:
        body["temperature"] = temp   #  if no temp given then fine else if temp given add that to body temp tells how random or fluactuating will be and of llm to a ques

    
    body = deepMergeDicts(body, extraOptions)              #    there are base setting and merge those base setting to extar specific  seettings for llm like think token etc 

    
    url = baseUrl.rstrip("/") + "/responses"           #  full endpoint of api create strip / create request header api expect format for authenticate its in bearer api key is in authoriztion 
    headers = {"authorization": "Bearer " + os.environ[keyEnvVar]}

    resp = post(url, headers, body)                    # Send post req to openai api endpoint header metadata nd body have all model and ques info

    responseOutput = resp.get("output") or []              #  from api response find output list 

    
    ans = []    # will have blocks taken out from output reply msg given by model api 

    for o in responseOutput:                          #   go through all blocs see which  msgs or content or other if msg type then add in content list 
        if o.get("type") == "message":
            content = o.get("content") or []

            for c in content:   #   loop ovewr all content bloclks in msg and add content block to ans to extract text repnse
                ans.append(c)

    
    t = ""

    for c in ans:                                        #  all content blks in ans list take out only those have text check if it has output text type and add to str t 
        if c.get("type") == "output_text":
            t += c.get("text", "")

    used = resp.get("usage") or {}                     #  get use info from resp if no info then empty dict extract token used in reasoning and output tokenns combined used 0 if no think 

    rt = used.get("output_tokens_details") or {}
    rt = rt.get("reasoning_tokens") or 0

    
    st = resp.get("incomplete_details") or {}           #   incomplete resp details if resp not completeed whats the reason for it 
    st = st.get("reason")


    metad = {                                                
        "finish": resp.get("status"),
        "blocked": False,
        "usage": tokenUsageInfo(
            used.get("input_tokens"),
            used.get("output_tokens"),
            rt
        ),
        "resp_model": resp.get("model")
    }   #   replys metadata finish has if its complted full use details find token used in input and output tokemns no how much reason tokend to think for ans model name to verify with req

    
    if resp.get("status") == "incomplete":                    
        metad["finish"] = "incomplete:" + str(st)  #  if incmplete reply finish to complete add to finish metdata reason for not to finish and get incomplete

   
    if st == "content_filter":                                
        metad["blocked"] = True   #  incmplete reason is content filter if its block filed sets true req get filter out by provider of model api not gone to llm even 

    for x in ans:
        if x.get("type") == "refusal":
            metad["blocked"] = True   #  looping over all content bloclk see if it has refusal blck as type refusal 

    
    thinking = False                                         

    if rt > 0:
        thinking = True   # reason token no more than 0 token used in thinking so thinking true used 

    for o in responseOutput:  # for  all resp outpt blcks see if reasoning type blocks and check if it  has summary yes then reasom is true 
        if o.get("type") == "reasoning" and o.get("summary"):
            thinking = True

    return t, thinking, metad   # give back text respnsee by model , id did thinking , metadat usage model name , block etc 





def modelSpecificCall(system, user, temp):   #  funct runner will use to call to gemini api takes theh sys prpmpt instructins and the user msg text that have to ask by gemini and temp controls sett
    return getResponseGpt(modelname, system, user, temp, extraOptions, baseUrl)


if __name__ == "__main__":    # run only if its call by this file direct not importing this file to other file
    runModel(tag, modelname, modelSpecificCall, extraOptions, keyEnvVar)