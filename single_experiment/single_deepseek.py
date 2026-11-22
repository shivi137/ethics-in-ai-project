from runner_orchestrator import runModel
import os

from api import call_openai_chat


tag = "deepseek"
modelname = "deepseek-flash"
keyEnvVar = "deepseek_api_key"
baseUrl = "https://api.deepseek.com"
extra = {"thinking":  {"type":"disabled"}}



def modelSpecificCall(system, user, temperature): # will take 3 different arguments system, user, temperature

    return call_openai_chat(modelname,  system, user, temperature, extra, baseUrl, os.environ[keyEnvVar])    # os.environ[keyEnv] is not a problem here, as in below code of run_model, we're just passing this function call, not actually calling it.





if __name__ == "__main__":
    runModel(tag, modelname, modelSpecificCall, extra, keyEnvVar)