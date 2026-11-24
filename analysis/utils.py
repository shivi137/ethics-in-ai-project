import json
import os
import numpy as np, pandas as pd


# Finding the paths of the required files  , get currnt path where this file is , curr foldewr above dir , make path to foldr having res of run , path to json of scnarios , path  to csv of human data , path to outp file foldr , and creaste folder oif not there 

currentPath = os.path.dirname(os.path.abspath(__file__))
rootPath = os.path.dirname(currentPath)

runsPath = os.path.join(rootPath, "single_experiment", "runs")
scenariosPath = os.path.join(rootPath, "data", "scenarios.jsonl")
humanPath = os.path.join(rootPath, "data", "human_responses.csv")

resultsPath = os.path.join(currentPath, "results")
os.makedirs(resultsPath, exist_ok=True)







modelNames = {
    "gpt-6-sol": "gpt",
    "claude-sonnet-5-5": "claude",
    "gemini-3.5-flash-lite": "gemini",
    "qwen-3.8-27b": "qwen",
    "deepseek-flash": "deepseek"
}   #   all model use in checkking llms ques of cases

options = ["Act", "Clarify", "Escalate", "Refuse"]   #   all decn options given to ans for each scene ques to human and to llm model 




models = ["gpt", "claude", "gemini", "qwen", "deepseek"]

languages = ["English", "Hindi", "Hinglish", "Bengali"]

# Bootstrap settings


randomSeed = 12345   # fixinh seed to get same random no all the time  run again 
bootstrapIterations = 5000    # for confid intrval  no of bootstap sample set 





def countDecisions(df):              #   no of time any decn  made by all modells for all ques case and all lang 
    counts = df.groupby(["model", "id", "language"])["label"].value_counts()   #  group all data by lang by model and by ques id and then will see in each sub grp case , how many each decn ans comes 

    counts = counts.unstack(fill_value=0)   #  decn no to cols and misisng to 0 add 

    counts = counts.reindex(columns=options, fill_value=0)  #          for all ques all decn options come in same order and no missimg to 0 



    result = {}    # dictn that will haev no of decn for all model ques lang 


    for group, row in counts.iterrows():    #   will go  through ach subgrap we ctrated amd and its row of no of decn happens   and store then no as nump aaray of decimal  by key 
        result[group] = row.values.astype(float)

    return result








def loadLLMData():     # loads all 5 llm data and combines into one dataframe. Also converts names to short names. duplicates also checked by this func and creates a pair column for each scn. Returns a pd dataframe.

    answers = []

    for model in models:       # 

        filePath = os.path.join(runsPath, model + "_single.jsonl")

        with open(filePath, encoding="utf-8-sig") as file:

            for line in file:

                if line.strip():          # this skips empty lines 

                    response = json.loads(line)

                    answers.append({                          # extract all fields and append to answers list
                        "model": modelNames[response["model"]],
                        "id": response["id"],
                        "language": response["language"],
                        "run": response["run"],
                        "label": response["label"],
                        "domain": response["domain"]
                    })

    df = pd.DataFrame(answers)

    if df.duplicated(["model", "id", "language", "run"]).any():     # just a duplicate check for responses, throws error if detects
        raise ValueError("duplicate")

    df["pair"] = df["id"].str[:-2]        # remove the last two chrs from sc id and create a pair identifier. 

    return df




def goldTable():   #   this is a gold function which make gold labvels given the human data in whuich human have selected each quest into one of four options given 

    human = loadHumanData()        #  loading human nrespinse data by calling a function in this file that loads human data 

    votes = human.groupby("id")["label"].value_counts()     #   grouping all rows of file by ids of ques case and we get by couting how many time any one option or each appear for each ques id 

    votes = votes.unstack(fill_value=0)   #   missing counts make to zero and arrange all in colms wise 

    votes = votes.reindex(columns=options, fill_value=0)

    totalVotes = votes.sum(axis=1)   #     for each ques scenarios id , add all labels numbers to find total no of heads 

    result = pd.DataFrame({
        "gold": votes.idxmax(axis=1),
        "gold_share": votes.max(axis=1) / totalVotes,
        "n_people": totalVotes
    })    # new panda frame that has final ans gold is label with most no of votes given by human for each id , n people is total no of votes got each ques , gold share is share of votes got by gold one label 

    for option in options:
        result["votes_" + option] = votes[option]   #   each given decision chooice option , add col that have vote number for that dec

    return result




def answersWithGold():   #   the calculated gold label added to each llm ans to knoeww if corrct ans llm 

    answers = loadLLMData()   #   loading llm resp data of all models all ques by helper function in thuis file 

    humanGold = goldTable()    #   getting all gold dec of each qyes scneario by calling gold label funct in this file 

    answers["gold"] = answers["id"].map(humanGold["gold"])    

    answers["correct"] = (answers["label"] == answers["gold"]).astype(float)     #  see human majorty and model ans to see nd give 1 if same 0 if not 

    return answers



def probabilityDifferentWithin(counts):   #   its to find prob that when same grp runs 2 times , it gets diff ans 

    total = counts.sum()  #     summing all choice labels to get total 

    same = (counts * (counts - 1)).sum()   #  finding no of ways  so 2 diff runs give same ans 

    return 1.0 - same / (total * (total - 1))    #  div  same ans by all  no of pairs and minus 1 get prob of diff ans 




def probabilityDifferentBetween(countsA, countsB):   #   find prob that 2 diff grp give 2 diff dec 

    same = np.dot(countsA, countsB)   #   mult same dec counts and add to get matchiig dec combint of 2 grps 

    total = countsA.sum() * countsB.sum()   #   total dec in 2 grps mult to give total posiible comintn

    return 1.0 - same / total   #  div by total an minus 1 to get prob 







def averagePerPair(valuesByID):    #    find avg values of ques A nd B for each pair of ques case

    pairs = sorted({scenarioID[:-2] for scenarioID in valuesByID})    #  from scenariod id    take out common pair id by remove last char A,B     duplicate remove     soring all ids of pair 

    averages = []    #    list to have each paiir of ques avg value 

    for pair in pairs:   #  go through all paird of A B

        valueA = valuesByID[pair + "-A"]   #   have to get value that if of scnerio A of the pair in loop 
        valueB = valuesByID[pair + "-B"]   #   of B 

        average = (valueA + valueB) / 2   #   avg 

        averages.append(average)   #  average list 

    return np.array(averages)




def bootstrapCI(valuesPerPair):   #   it is a function to find confidence interval bootsrap 95  % form every pair values 

    values = np.asarray(valuesPerPair, dtype=float)  #  input values getting change to NumPy array of floats 
    rng = np.random.default_rng(randomSeed)   #  fixed seed for random no generator so taht every time  generate same  randomly giving same ramdom nos

    samples = rng.integers(
        0,
        len(values),
        size=(bootstrapIterations, len(values))
    )   #  samples have stsrt index value 0  and upper linit  to values avaialble no  

    sampleMeans = values[samples].mean(axis=1)    #  to compuate  mean of each sample that is sbootstapped  

    lower = np.percentile(sampleMeans, 2.5)  #  lower limit of confid intrval  2.5 percentile of bootstap 
    upper = np.percentile(sampleMeans, 97.5)   #  upper limit of confid intrval  97.5 percentile of bootstap 

    return float(lower), float(upper)   #  lower upper mimits of confid intrval return 




def percentage(value, digits=1):   #  its a helper funct that change decimal value to percnt and round off too with given no of places

    return round(100.0 * value, digits)   #   round off after multiplyimng with 100 



def saveResults(df, name):   #    its is a function to save the result given by dataframe from the calling function as csv file not panda dataframe 

    filePath = os.path.join(resultsPath, name)   #  making path to save result by combine path of result folder and name of the file 

    df.to_csv(filePath, index=False, encoding="utf-8")   #   save csv file use utf 8 encoding and no indexing of row 

    print("Result written/" + name, f"({len(df)} rows)")   #   print that result has written and name of file and rows number that saved 


def loadHumanData():                         #   its a funct   that  loads  human collected responses data by human csv file loading  from folder   

    human = pd.read_csv(humanPath, encoding="utf-8-sig")    #  reading file of human data csv and storing it it pandaadataframe 

    scenarios = []   #   list to store all ques scenaes of human csv file 

    with open(scenariosPath, encoding="utf-8") as file:   #  opening as file and seeing every line in file firdt that every line is filled not blank and tyen every linen json fomrat is chnaged to pythpn dict and after making dict add it to scneario lost 
        for line in file:
            if line.strip():
                scenarios.append(json.loads(line))



    engScenID = {}    #   empty  dict to have text of englisdh ques and their scenario ids 

    for scenario in scenarios:   #    go through  all ques in the scen list and checking if that currnt scene is in english or any other langusge and then  saving the text of eng ques as key and id of thet que sceanriod if as value 
        if scenario["language"] == "English":
            engScenID[scenario["text"].strip()] = scenario["id"]

    engHuman = human[human["language"] == "English"]    #     only  select humana data response to english questns 


    engHuman = engHuman.drop_duplicates("scenario_id")     #   take out  the repeted scen ids  so thqat englsh scn ids appear one tikme only 

    humanIDToScenarioID = {}   #  dictr to mapping of hum,an scn ids to origianl scn ids in the dataset 

    for humanID, text in zip(
        engHuman["scenario_id"],
        engHuman["scenario_text"]
    ):   #   going through all englidh human scnes ids and their text and get human scn ids fromt english answers and also english scnerio tetxt form human anss
        humanIDToScenarioID[humanID] = engScenID[text.strip()]   #   find matching ids of scenes by englsh text and save that mapping 

    human["id"] = human["scenario_id"].map(humanIDToScenarioID)   

    human = human.rename(columns={
        "language": "resp_language",
        "response_category": "label"
    })   #  cols in panda datagrame re named to resp_language and to tell lang of perosn whol filled the form for data collection and response_category  to telll which optuin it chose

    return human[["respondent_id", "resp_language", "id", "label"]]    #  return the needed cols for ananalysis labels ids and the human who filled the form those langungs and id 
    
