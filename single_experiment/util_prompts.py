from config import systemPromptString, labelDefinitions, Four_Labels
import hashlib
import random
import json

promptText = systemPromptString + json.dumps(labelDefinitions, sort_keys=True)
promptBytes = promptText.encode()
promptHash = hashlib.sha256(promptBytes).hexdigest()

promptHASH_firstTwelve = promptHash[:12]    #    creating hash  for prompt so same will go to all llm 

#---------------------------------------------


def labelOrder(item_id, run, toShuffle=True, seed=0):
    FourLabels_copy = ["Act", "Clarify", "Escalate", "Refuse"]

    if toShuffle:
        randomNumbGeneratorr = random.Random(f"{seed}|{item_id}|{run}")
        randomNumbGeneratorr.shuffle(FourLabels_copy)


    return FourLabels_copy  #  shuffling order of labels same for same ques in all lang 

#--------------------------------------------------------------------------------


def systemPromptForLLM(domain, orderOfLabel):          # creates the system prompt for llms
    policyLinesList = []         #empty list which will store each policy line

    for aLabel in orderOfLabel:
        line = f"- {aLabel}: {labelDefinitions[aLabel]}"
        policyLinesList.append(line)

    policy = "\n".join(policyLinesList)
    labels = "|".join(orderOfLabel)

    return systemPromptString.format( domain=domain,  policy=policy,   labels=labels )

#------------------------------------------------------------------

def responseDesision(res):     
    """Takes llm response to extract json, returns label and a reson.

    Argumants which it takes:
        res: string which is the response from the llm

    Returns what?:
        dictionary with keys label and reason,
    
    """
    
    if res is None:
        res = ""
    res = res.strip()

    jsonStart = res.find("{")  
    jsonEnd = res.rfind("}")   # rfind searches from end, just efficient.


    if jsonStart == -1 or jsonEnd < jsonStart:        #to check if json exists or not, throws error otherwise
        raise ValueError("json object not found")
    decision = json.loads(res[jsonStart:jsonEnd + 1])       #  extract json into a python dict

    decisionlabel = str(decision.get("label", "")).strip()
    for lab in Four_Labels:
        if lab.lower() == decisionlabel.lower():
            decisionlabel = lab
            break
    else:
        decisionlabel = None

    if decisionlabel is None:
        label = decision.get("label", "")
        raise ValueError(f"bad label: {label}")



    return {"label": decisionlabel, "reason": str(decision.get("reason", "")) }