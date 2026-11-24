from runner_orchestrator import runModel   #   import function run model from file runner orchestrator from project folder this runs models all 
from api import call_openai_chat   #   call oipen ai function give requests to llm api and also teke what it sends back 



import os


tag = "qwen"    # short form of the model
extra = {"reasoning_effort": "none", "max_completion_tokens": 1024}   #  tokens max 1024 in reply and no think or reason
modelname = "qwen-3.8-27b"   # actual official model nam e
baseUrl = "https://api.cerebras.ai/v1"  # base url link to add in api creation 
keyEnvVar = "cerebras_api_key"   # var store api key for the model run 




def modelSpecificCall(system, user, temperature):  #  funct takes prompt by system by useer and to control randomness the temperature of mofdel so that llm give and at fixed randomness not vary eith each run 

    return call_openai_chat(modelname, system, user, temperature, extra, baseUrl, os.environ[keyEnvVar])    

#  calling api help funct with all needed parametrs like name prompts temp url key password 



if __name__ == "__main__":   # only call if calling this filre directly and not if some other file imports it then block calling this file
    runModel(tag, modelname, modelSpecificCall, extra, keyEnvVar)    # tag is model identufy , name , extra setting , api , and model specific funvtion made in this file call to run 





 


