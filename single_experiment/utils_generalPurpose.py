def block_words(message):    #  check if request reject by llm provider content filter, by checking if msg contains any phrases that indicate as such
    lowercaseMessage = str(message).lower()

    blocks = (                         # but thesee are guaranted to cover every provides error
        "content exists risk",
        "content_filter",
        "content_policy",
        "content policy"
    )  


    for phrase in blocks:
        if phrase in lowercaseMessage:
            return True

    return False


#------------------------------------------------

def tokenUsageInfo(tokens_in, tokens_out, reasoning=0):   #  put all token count in dict
    return {"in": tokens_in or 0,  "out": tokens_out or 0, "reasoning": reasoning or 0 }

#------------------------------------------------------------

def deepMergeDicts(baseDict, extraDict):         
    
    for key, value in extraDict.items():

        if key in baseDict:
            if isinstance(baseDict[key], dict) and isinstance(value, dict):
                deepMergeDicts(baseDict[key], value)                               #recursive call
            else:
                baseDict[key] = value
        else:
            baseDict[key] = value

    return baseDict