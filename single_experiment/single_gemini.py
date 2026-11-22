

from runner_orchestrator import runModel
import os
from utils_generalPurpose import deepMergeDicts, tokenUsageInfo
import json
from api import post



tag = "gemini"
keyEnvVar = "gemini_api_key"
modelname = "gemini-3.5-flash-lite"
baseUrl = "https://generativelanguage.googleapis.com/v1beta"
extraOptions = {"generationConfig": {"thinkingConfig": {"thinkingLevel": "minimal"}}}            # reasoning setting, merged into the request body



blockedDict = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "RECITATION", "IMAGE_SAFETY"}


def callGemini(model, system, user, temp, extra, base):

    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": 1024}
    }

    if temp is not None:
        body["generationConfig"]["temperature"] = temp

    body = deepMergeDicts(body, extra)

   
    r = post(
        f"{base.rstrip('/')}/models/{model}:generateContent",
        {"x-goog-api-key": os.environ[keyEnvVar]},
        body
    )

  
    um = r.get("usageMetadata") or {}
    thoughts = um.get("thoughtsTokenCount") or 0

    usage = tokenUsageInfo(
        um.get("promptTokenCount"),
        (um.get("candidatesTokenCount") or 0) + thoughts,
        thoughts
    )

   
    candidates = r.get("candidates") or []

    if not candidates:
        block = (r.get("promptFeedback") or {}).get("blockReason")

        if block:
            return "", False, {
                "finish": "blocked:" + str(block),
                "blocked": True,
                "usage": usage,
                "resp_model": r.get("modelVersion")
            }

        raise RuntimeError("no candidates: " + json.dumps(r)[:300])

    
    parts = (candidates[0].get("content") or {}).get("parts") or []
    finish = candidates[0].get("finishReason")

    
    text = ""
    thinkingUsed = bool(thoughts)

    for p in parts:
        if p.get("thought"):
            thinkingUsed = True
        else:
            text += p.get("text", "")

    return text, thinkingUsed, {
        "finish": finish,
        "blocked": finish in blockedDict,
        "usage": usage,
        "resp_model": r.get("modelVersion")
    }

def modelSpecificCall(system, user, temp): # will take 3 different arguments system, user, temperature

    return callGemini(modelname, system, user, temp, extraOptions, baseUrl)


if __name__ == "__main__":
    runModel(tag, modelname, modelSpecificCall, extraOptions, keyEnvVar)