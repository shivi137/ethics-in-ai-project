import urllib.request, urllib.error
import json
import time
from utils_generalPurpose import tokenUsageInfo

def post(url, headers, body, tries=5):    #   sending request to api of llm model. This is just standard  api calling codee, nothing new.


    for currentRetryNo in range(tries):   # try 5 times 
        try:
            req = urllib.request.Request(          # creates http request object
                url,                                   # the endpint to send request
                json.dumps(body).encode(),                   #python to json, and then encode to bytes (just suitalbe for network, notthing else)
                {"content-type": "application/json", **headers}       # **headers just pastes contents of headers dict
            )   

            resp = urllib.request.urlopen(req, timeout=120)    # calling api and then 120 sec wait for reply
            return json.load(resp)                      #json to python dict


        except urllib.error.HTTPError as error:   #  busy  or server problem
            retry = (429, 500, 502,  503, 504,  529)                           # list of errors which are worth retrying, I looked it up on google
            if error.code in retry and currentRetryNo < tries - 1:    # 
                time.sleep(2 ** currentRetryNo * 2)       # exponential backoff. wait 2 then 4 tne 8 and so on
                continue


            raise RuntimeError(error.read().decode()[:500])    #otherwise just throow an error, with first 500 chrs

        except (urllib.error.URLError, TimeoutError, ConnectionError):   # network-level problems (timeout, reset, DNS). HTTPError is a subclass of URLError, so it must stay above.
            if currentRetryNo < tries - 1:
                time.sleep(2 ** currentRetryNo * 2)
                continue
            raise


def call_openai_chat(model, system, user, temp, extraOptions, base, key):   #    sending   ques to  OpenAI-style API ( for Qwen via Cerebras,  DeepSeek) and returns model reply, extra info
    url = base.rstrip("/") + "/chat/completions"   #  removes end / and then add a string


    header = {
        "authorization": "Bearer " + key    #  api key 
    }
#    request that will send 
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        **({"temperature": temp} if temp is not None else {}),
        **extraOptions  # puts contents of extraOptions (which is a dictionary) here into the body.
    }



    reply = post(url, header, body)   #  sending 

    option = reply["choices"][0]
    msg = option["message"]
    use = reply.get("usage") or {}

    reasoning = (
        (use.get("completion_tokens_details") or {}).get("reasoning_tokens")
        or 0
    )   # while thinking usage


    metadata = {
        "finish": option.get("finish_reason"),
        "blocked": option.get("finish_reason") == "content_filter",
        "usage": tokenUsageInfo(
            use.get("prompt_tokens"),
            use.get("completion_tokens"),
            reasoning
        ),
        "resp_model": reply.get("model")
    }

    think = bool( msg.get("reasoning_content") or  msg.get("reasoning")  or reasoning > 0)

    return msg.get("content") or "", think, metadata