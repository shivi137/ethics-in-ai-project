

from  runner_orchestrator import runModel
import os
from utils_generalPurpose import  deepMergeDicts, tokenUsageInfo
from  api import post


tag = "gpt"
modelname = "gpt-6-sol"
keyEnvVar = "openai_api_key"
extraOptions = {"reasoning": {"effort": "none"}}
baseUrl = "https://api.openai.com/v1"

def getResponseGpt(modelname, system, user, temp, extraOptions, baseUrl):         # this can be refactored, i will change if i get time.

    body = {
           "model": modelname,
        "instructions": system,
          "input": user,
           "max_output_tokens": 1024
    }

    if temp is not None:
        body["temperature"] = temp

    
    body = deepMergeDicts(body, extraOptions)                  # Add some more settings to the request body by calling deepMergeDicts()

    
    url = baseUrl.rstrip("/") + "/responses"           #rstrip removes / at end
    headers = {"authorization": "Bearer " + os.environ[keyEnvVar]}

    resp = post(url, headers, body)                    # Send request

    responseOutput = resp.get("output") or []              #get output

    
    ans = []

    for o in responseOutput:                           # append to ans list all the message content
        if o.get("type") == "message":
            content = o.get("content") or []

            for c in content:
                ans.append(c)

    
    t = ""

    for c in ans:                                        # from ans, extract all text
        if c.get("type") == "output_text":
            t += c.get("text", "")

    used = resp.get("usage") or {}                     #gives token usage info

    rt = used.get("output_tokens_details") or {}
    rt = rt.get("reasoning_tokens") or 0

    
    st = resp.get("incomplete_details") or {}           # to get reason for incomple resonse
    st = st.get("reason")


    metad = {                                                 # creates the metadata
        "finish": resp.get("status"),
        "blocked": False,
        "usage": tokenUsageInfo(
            used.get("input_tokens"),
            used.get("output_tokens"),
            rt
        ),
        "resp_model": resp.get("model")
    }

    
    if resp.get("status") == "incomplete":                    # to handle the incomplete response
        metad["finish"] = "incomplete:" + str(st)

   
    if st == "content_filter":                                 # check for blocked phrase used or not
        metad["blocked"] = True

    for x in ans:
        if x.get("type") == "refusal":
            metad["blocked"] = True

    
    thinking = False                                         # below code checks if reasoning was used

    if rt > 0:
        thinking = True

    for o in responseOutput:
        if o.get("type") == "reasoning" and o.get("summary"):
            thinking = True

    return t, thinking, metad





def modelSpecificCall(system, user, temp): # will take 3 different arguments system, user, temperature
    return getResponseGpt(modelname, system, user, temp, extraOptions, baseUrl)


if __name__ == "__main__":
    runModel(tag, modelname, modelSpecificCall, extraOptions, keyEnvVar)