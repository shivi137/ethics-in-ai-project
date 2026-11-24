from runner_orchestrator import runModel   #   import function run model from file runner orchestrator from project folder this runs models all 
import os

from api import call_openai_chat   #   call oipen ai function give requests to llm api and also teke what it sends back 


tag = "deepseek"   #  identifier like short form of the model in which request will be send 
modelname = "deepseek-flash"   #  its the actual name of model and will be using same name in api while seding 
keyEnvVar = "deepseek_api_key"   # var that will store they api key needed to call api 
baseUrl = "https://api.deepseek.com"  #   base link for sending will add more thins in base url to make request complete correct
extra = {"thinking":  {"type":"disabled"}, "max_tokens": 1024}   # response will be not more than 1024 tokens and any extra extended think is off for this model and also some more paramateres for api 



def modelSpecificCall(system, user, temperature): #  funct takes prompt by system by useer and to control randomness the temperature of mofdel so that llm give and at fixed randomness not vary eith each run 

    return call_openai_chat(modelname,  system, user, temperature, extra, baseUrl, os.environ[keyEnvVar])   
#  calling api help funct with all needed parametrs like name prompts temp url key password 


if __name__ == "__main__":   # only call if calling this filre directly and not if some other file imports it then block calling this flld 
    runModel(tag, modelname, modelSpecificCall, extra, keyEnvVar)  # tag is model identufy , name , extra setting , api , and model specific funvtion made in this file call to run 
    