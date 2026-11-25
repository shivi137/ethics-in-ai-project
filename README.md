# A Study on Human Escalation decision by LLM Agents under Different Indian Languages

### Owners:
Shivi Awsthi, Pranjal Sisodia


### Folder Structure 
```
ETHICS-IN-AI-PROJECT/

|--data/
  |-cleandata.py       cleans human resp sheet data change to csv
  |-prepare_data.py      convertts scenarios sheet to json lines 
  |-scenarios.xlsx    64 questions  in 4 language in excel file
  |-scenarios.jsonl     all question in specific jsonl format
  |-human_responses.csv  cleaned human responses for analysis of metrcs

|--single_experiment/
  |-api.py              send api req ,read model response    
  |-config.py           have labels,what they mean,sys prompt 
  |-runner_orchestrator.py  runs each secnario 10 time in paralel
  |-util_prompts.py       build prompt for request,get responlabel
  |-utils_generalPurpose.py  helper functions count,detect block
  |-single_gpt.py        build request as per gpt api format 
  |-single_claude.py        build  request as per claude api format  
  |-single_qwen.py         build request  as per qwen api format  
  |-single_gemini.py     build  requesst as per gemini api format  
  |-single_deepseek.py     build request as pe deepseek api format 
  |-scenarios.jsonl      copy of data/scenarios.jsonl 
  |-runs/
    |-qwen_single.jsonl   qwen's responses for all ques 10 run each
    |-gpt_single.jsonl    gpt's responses to all ques 10 run
    |-gemini_single.jsonl  gemini responses of all ques 10 runs 
    |-claude_single.jsonl  claude responses   for all ques 10 runs each 
    |-all_models_single.jsonl  all model all modelrun combined 

|--analysis/
  |-utils.py           loading,saving,calc helper funct
  |-accuracy.py      save model acc against humman and gap
  |-errmetrics.py        metrics  prec,recal,f1,conf mat
  |-kappa.py          save  fleiss kappa for human   agreement
  |-label_sh.py     saves label share   by domain loang modl
  |-modelnoise.py       run noise , corsslang disagree
  |-results/
    |-accuracy.csv      all model and languages accuracy for ques
    |-noise.csv           random noise of each model in itself  
    |-crosslang.csv     across  languages disagreement 
    |-confusion_matrix.csv  confusion matrix for each model/lang
    |-error_rates.csv    error rates for escalation,safety etc
    |-fleisskappa.csv       humans agreement among themselves 
    |-gaplang.csv        each lang accuracy gap   against eng
    |-labelsharebylang.csv   label percentshare by lang and model
    |-labelsharebydomain.csv  label    share by domain
    |-perques.csv          gold labels   per ques from humans
    |-precision_recall_f1.csv  prec,recall,f1 for each label
    |-minimal.csv         difference due to minimal pairs

|--sandbox/
  |-create_tool_env.py      builds dummy tools  for all scenearios 
  |-tool_calls.jsonl         tools and o/p of tool calling in jsonl

|--requirements.txt       python libraries   needed to install  
|--README.md                 folder   structure and files describe

    

    



     

