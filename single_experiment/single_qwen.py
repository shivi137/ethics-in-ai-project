from runner_orchestrator import runModel
from api import call_openai_chat



import os


tag = "qwen"
extra = {"reasoning_effort": "none", "max_completion_tokens": 1024}
modelname = "qwen-3.8-27b"
baseUrl = "https://api.cerebras.ai/v1"
keyEnvVar = "cerebras_api_key"




def modelSpecificCall(system, user, temperature): # will take 3 different arguments system, user, temperature

    return call_openai_chat(modelname, system, user, temperature, extra, baseUrl, os.environ[keyEnvVar])    # os.environ[keyEnv] is not a problem here, as in below code of run_model, we're just passing this function call, not actually calling it.




if __name__ == "__main__":
    runModel(tag, modelname, modelSpecificCall, extra, keyEnvVar)