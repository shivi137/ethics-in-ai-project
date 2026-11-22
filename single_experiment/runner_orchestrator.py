from datetime import datetime, timezone

from util_prompts import systemPromptForLLM, labelOrder, promptHASH_firstTwelve, responseDesision
import sys, os
import argparse
import json
from utils_generalPurpose import block_words



def run_model(modelTag, modelName, callFunc, extraOptions, apiKeyEnvVariable):    #this is the most improtant fuc of theis script
    """Function For running  models. Its the entry point for this file.

    Argumens, what it takes:
        modelTag: used just to save output file, nothing else
        modelName: tells api which model to use
        callFunc: function that takes as input (system, user, temp) and returns these (text, thinking, metadata). Makes our run_model flexible with different apis.
        extraOptions: dictionary of extra parameters to pass into model request. 
        keyEnvVariable: its the env variable name for the API key of a particular mode.

    Returns what?
        Nothing, but saves a JSONL file with one line per run, each line containing the model's response and metadata.

    """
    
    scriptFolder = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(scriptFolder) # changes the workking directory to in which the script is present, to be able to findd scenarios.jsonl and save output in same directory.

    if not os.environ.get(apiKeyEnvVariable):    #if the api key doen't exist, stop program executin & print error.
            sys.exit(f'{apiKeyEnvVariable} is not set. Please set it before you run this script.')

    #-------------------------------------------
    
    parserObject = argparse.ArgumentParser() # creates a parser object for reading command line argumnts



  #  tells which argumens are allowed. Adds allowed arguments to parsen object
    parserObject.add_argument("--noOfRuns", type=int, default=4)
    parserObject.add_argument("--noOfWorkers", type=int, default=6)
    parserObject.add_argument("--temp", type=float, default=None)
    parserObject.add_argument("--noShuffle", action="store_true") # labels wont be shuffled if this is provided 
    parserObject.add_argument("--seedVal", type=int, default=0)
    parserObject.add_argument("--limitNoOfScenarios", type=int, default=None)
    parserObject.add_argument("--languages")
    parserObject.add_argument("--outputFile")

    

    arguments = parserObject.parse_args()   #argements object here contains teh actual arguments that we provide while calling script.



    output = arguments.outputFile        # code to decide wheree the otuput file will be saved

    if output is None:                   #if no output file arg provided by script executor, then do default
        output = f"runs/{modelTag}_single.jsonl"

    folder = os.path.dirname(output)   # get the folder name

    if folder:              
        os.makedirs(folder, exist_ok=True)

    #-------------------------------------------

    shuffleLabels = not arguments.noShuffle
    temperature = arguments.temp
    randomSeed = arguments.seedVal

    settings = {
        "temp": temperature,
        "extra": extraOptions,
        "shuffle": shuffleLabels,
        "seed": randomSeed
    }

    #-------------------------------------------

    scenarios = []

    with open("scenarios.jsonl", encoding="utf-8") as file:             # just opens the sceanarios jsonl file and appends all scenarios to a python list of questions
        for line in file:
            scenarios.append(json.loads(line))



    if arguments.languages:   # if languages are provided, filter the scenarios to only include those languages
        lang = arguments.languages.split(",")
        languageFilteredScenarios = []

        for s in scenarios:
            if s["language"] in lang:
                languageFilteredScenarios.append(s)

        scenarios = languageFilteredScenarios



    if arguments.limitNoOfScenarios:
        ids = []

        for s in scenarios:           # one by one collect all the unique ids
            if s["id"] not in ids:
                ids.append(s["id"])

        ids.sort()                    # just sort the unqie ids in asc order
        ids = ids[:arguments.limitNoOfScenarios]      # this keeps only the first n unique ids after sorting

        filteredScenarios = []         

        for s in scenarios:            # again one by one go through all scenarios but keep only sc with unique ids
            if s["id"] in ids:
                filteredScenarios.append(s)

        scenarios = filteredScenarios


    #-------------------------------------


    alreadyFinished = set()    #   empty set, which will remember  calls finished with no error 

    if os.path.exists(output):                                  # check if the output file already exists
        with open(output, encoding="utf-8") as file:             # open it
            for line in file:                                   # read line by line
                runResult = json.loads(line)                      # convert each line to python dictionary

                if not runResult.get("error"):                     # to cehck if the run was success
                    alreadyFinished.add((                              # store into set
                        runResult["model"],
                        runResult["id"],
                        runResult["language"],
                        runResult["run"]
                    ))


    #------------------------------------------------


    def work(run, row):   #   handle each run scenario for a run

        order = labelOrder(row["id"], run, not arguments.noShuffle, arguments.seedVal)  #  order labels 

        system = systemPromptForLLM(row["domain"], order)   #  instruction   to llm 

        base = {                  #dictionary conatining info about the run.
            "model": modelName,
            "condition": "single",
            "id": row["id"],
            "pair": row["pair"],
            "variant": row["variant"],
            "domain": row["domain"],
            "language": row["language"],
            "run": run,
            "order": order,
            "prompt_hash": promptHASH_firstTwelve,
            "settings": settings
        }



        times = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")  # standard code which returns current UTC (not IST) datee and timea as a string



        try:
            text, thinking, metaData = callFunc(
                system,
                row["text"],
                arguments.temp
            )   #  asking model ques 

        except Exception as error:
            if block_words(error):     # if blocked because of block phrases, then return this below
                return {
                    **base,               # base is expsnded for its key value pairs
                    "label": "blocked",
                    "reason": None,
                    "raw": str(error)[:500],     # limit too 500 characters of error message
                    "thinking_used": None,
                    "finish": "blocked_error",
                    "usage": None,
                    "resp_model": None,
                    "ts": times(),
                    "error": None
                } 



            return {          # if not contain any block phrases, then return this
                **base,               # base is expanded for its key value pairs
                "label": None,
                "reason": None,
                "raw": None,
                "thinking_used": None,
                "ts": times(),
                "error": str(error)
            }   #  other error 



        if metaData.get("blocked"):
            llmResult = { "label": "blocked", "reason": None}    # if llm api indicates response is blocked, so return this
        else:
            try:
                llmResult = responseDesision(text)   # change llm reply to label and reason
            except Exception:
                llmResult = { "label": "invalid_output",  "reason": None }



        return {
            **base,              # base is expanded for its key value pairss
            "label": llmResult["label"],
            "reason": llmResult["reason"],
            "raw": (text or "")[:500],    # if none or empty, use empty string and then chose 500 first character 
            "thinking_used": thinking,
            "finish": metaData.get("finish"),
            "usage": metaData.get("usage"),
            "resp_model": metaData.get("resp_model"),
            "ts": times(),       # just timestamp
            "error": None
        }  

    #----------------------------------------------------------------------------------------

    # creates a list of scenarios & runs which are not yet finished
    jobs = []

    for runVar in range(arguments.noOfRuns):
        for particularRow in scenarios:
            callJob = (modelName, particularRow["id"], particularRow["language"], runVar)    # creates a tuple for identifyng a particular job

            if callJob not in alreadyFinished:
                jobs.append((runVar, particularRow))        #just add the unfinished job to list



    print(len(jobs), " number of calls to make with workers =", arguments.noOfWorkers)   # print how many jobs are there to do and how many workers will be used

    #--------------------------------------------------------------------------

    #this code below runs multiple jobs simultaneously using threads
    from concurrent.futures import ThreadPoolExecutor                  # to run multiple funs in parallel
    from concurrent.futures import as_completed                 # to collect completed tasks one by one, but in the order they get finished


    with open(output, "a", encoding="utf-8") as file:            # a in arg here means append, so new reslts are appeded, and utf encoding supportes chars for many langs
        # output argument is defined at the beginnng of this run_model func
        with ThreadPoolExecutor(max_workers=arguments.noOfWorkers) as executor:   # run parallel 
            futures = [
                executor.submit(work, run, row)          # this just runs the work func with args as run and row.
                for run, row in jobs
            ]

            for number, future in enumerate(as_completed(futures), 1):       # get the results one by one as they cmplete
                file.write(
                    json.dumps(future.result(), ensure_ascii=False) + "\n"   # write to output file 
                )
                file.flush()

                if number % 25 == 0:     #   Progess msg every 25 results
                    print(f"  {number}/{len(jobs)}", flush=True)




    print("done")