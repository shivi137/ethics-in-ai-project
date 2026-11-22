from runner_orchestrator import run_model
from api import call_openai_chat



import os


tag = "qwen"
extra = {"reasoning_effort": "none"}
model = "qwen-3.8-27b"
baseUrl = "https://api.cerebras.ai/v1"
keyEnv = "cerebras_api_key"




def modelSpecificCall(system, user, temperature): # will take 3 different arguments system, user, temperature

    return call_openai_chat(model, system, user, temperature, extra, baseUrl, os.environ[keyEnv])    # os.environ[keyEnv] is not a problem here, as in below code of run_model, we're just passing this function call, not actually calling it.




if __name__ == "__main__":
    run_model(tag, model, modelSpecificCall, extra, keyEnv)