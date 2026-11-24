
# 
from runner_orchestrator import runModel
import os
from utils_generalPurpose import deepMergeDicts, tokenUsageInfo
from api import post



modelname = "claude-sonnet-5-5"
baseUrl = "https://api.anthropic.com/v1/messages"
extraOptions = {"thinking": {"type": "between_tools"}}

keyEnvVar = "anthropic_api_key"

versionNo = "2023-06-01"
tag = "claude"



def callClaude(modelName, system, user, temper, extra, baseUrl, version):


    body = { "model": modelName, "max_tokens": 1024, "system": system, "messages": [{"role": "user", "content": user}] }

    
    if temper is not None:                      
        body["temperature"] = temper

    
    body = deepMergeDicts(body, extra)                  # Add some more settings to the request body by calling deepMergeDicts()

    
    headers = {"x-api-key": os.environ[keyEnvVar], "anthropic-version": version }

    
    responseOfClaudeApi = post(baseUrl, headers, body)                     # Send request

    
    t = ""                                                                         

    for x in responseOfClaudeApi["content"]:                              # Extract the text from respoonse
        if x.get("type") == "text":
            t += x.get("text", "")

    
    u = responseOfClaudeApi.get("usage") or {}                         # Get token usage from response we got

    
    metaDataDict = {                                                 
        "finish": responseOfClaudeApi.get("stop_reason"),
        "blocked": responseOfClaudeApi.get("stop_reason") == "refusal",
        "usage": tokenUsageInfo(
            u.get("input_tokens"),
            u.get("output_tokens")
        ),
        "resp_model": responseOfClaudeApi.get("model")
    }

    
    isThink = False

    for block in responseOfClaudeApi["content"]:                                                           # Check if thinking
        if block.get("type") == "thinking" or block.get("type") == "redacted_thinking":
            isThink = True

    return t, isThink, metaDataDict


def modelSpecificCall(system, user, temp): # will take 3 different arguments system, user, temperature

    return callClaude(modelname, system, user, temp, extraOptions, baseUrl, versionNo)



if __name__ == "__main__":
    runModel(tag, modelname, modelSpecificCall, extraOptions, keyEnvVar)