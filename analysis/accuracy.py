from utils import *  #   import utils.py file from sam efolder and all of its functions will get use there 

df = answersWithGold()  #     load all the ans given by all the models llms and also given whwt theri human guiven gold label is also given there 



def accPair(d):   #   funct that will find acuuracy for each apir of ques  it will grp rows of same pair an dthen their average and also check correct hopw much it is correct is 1 or 0 only so taking avg will give the accuracy 

    return d.groupby("pair")["correct"].mean().sort_index().values



rows = []  #  list empty it will have result sabe for all lang and all model each by each 

for model in models + ["ALL 5 MODELS"]:   #  check through all the models we used for responsee and add all 5 models to tell its accuracy for all combined 5 models 

    for lang in languages + ["ALL"]:   #  here check through all lang now used for data questions and add all languages to tell its for all lang combined accuracy 

        
        d = df[
            ((df["model"] == model) | (model == "ALL 5 MODELS")) 
            & ((df["language"] == lang) | (lang == "ALL"))       
        ]   # data filter to select rows that we need select one any model or all model or seleect one any language or all languages if need

        lo, hi = bootstrapCI(accPair(d))   #   bootsrapt confid interval funct from utils python file cqall that funct to find lower upper confid interval values 95 percent , first caklculate accuracy of each pair by calling accpauir funct and then bootstrp resamples pairaccuracies so find estimate how uncertain

        
        rows.append({

            "model": model,  
            "language": lang,  

            "n_answers": len(d),

            "accuracy_pct": percentage(d["correct"].mean()), 

            "ci_lo_pct": percentage(lo),  

            "ci_hi_pct": percentage(hi)  
        })    #    the calculated results will be as dict inside row list model have model name and language have lang name n answers have how mnay rows of ans  select , accuracy pct find total accuracy and convert to percent ci lo pct and ci hi pct change lower upper confid limit to percnetage value 


accuracyResults = pd.DataFrame(rows)   #    chnage   to list of all dict to a panada data frame and then each dict becomes one row and keys of dict become the nam eof cols 


saveResults(accuracyResults, "accuracy.csv")   #    saving resulta of all acuuracy in accuracy.csv file in the results folder created in analysisi folder



def gap(modelList, name):   #  funct gap finds accuracy gap of lang in comapre with english lang input parameter is list of models to analysze and name label use in output 

    rows = [] 

    for lang in languages[1:]:   #   each lang in list start from 2nd beacuse 1st one is englidh in list that comapring with othe rlamng so no need to comapre ehglsh with englsh comapring englsh with other lang 

        # Select answers produced by the specified models in English
        dEn = df[
            df["model"].isin(modelList)  
            & (df["language"] == "English")  
        ]   #  choose ans by chosen specific models in englsh keep only model that are named in model list and only englsh lang ans not other lang ones 

        # Select answers produced by the same models in the current language
        dLang = df[
            df["model"].isin(modelList)  # Keep only the specified models
            & (df["language"] == lang)  # Keep only answers in the current language
        ]

        diffs = accPair(dLang) - accPair(dEn)  #   diffs first find accurcy in curr iteration lang for all each pairs and then accuracy in english lamng for all pairs then  minus englsh from currnt   if diff pos so curr lang did better difg neg then englsh did brttr 


        lo, hi = bootstrapCI(diffs)   #  they are lower upper of 95 percent confid intrval of pair by pair accuracuy diff  resample 32 pair diffinstead of each each row of ans 

        
        rows.append({

            "model": name,  

            "language": lang, 

            "english_accuracy_pct": percentage(dEn["correct"].mean()),  

            "language_accuracy_pct": percentage(dLang["correct"].mean()),  

            "gap_pct": percentage(diffs.mean(), 2),  

            "ci_lo_pct": percentage(lo, 2),  

            "ci_hi_pct": percentage(hi, 2)  
        })   #  in dict save all values found for curr iteration lang   model name , lang that comapre with engl  , english accuracy pct is english lang accuracy in percentag , lang accuracy pct is currnt iteation  lang accuracy in percentag gap pct is percnetage difference in avg accuracy along all pairs , ci lo pct ci hi pct are lower upper confidence limits of gaps 


    return pd.DataFrame(rows)   #   change all results store into panada data frame and return that 

perModel = pd.concat(
    [gap([model], model) for model in models],
    ignore_index=True
)   #   find lang gap for each model separate gap model , model send to gap funct one model at one time and concat combines all in one frame result of all 5 models used and also create a new indeing for row index 


pooled = gap(models, "ALL 5 MODELS")   #   find lang gap by all 5 models tpogether 

out = pd.concat([perModel, pooled], ignore_index=True)  #   combine add all 5 models reslut with total resiults combined and new frame will have resul;ts for all model and combine  model 

out["interval_excludes_zero"] = (
    (out["ci_lo_pct"] > 0) | (out["ci_hi_pct"] < 0)
)   #   check if confid interval have 0 or not inside it confid interval id full positive if lower limit is more thn 0 and funn neg if upper lmt is less thn 0 in both cases no 0 in interval 


out = out.round(4)   #  round off to 4 dec places all numericl values in panda dataframe out 


saveResults(out, "gaplang.csv")   #   save all lang gap calculated in a file gap lang .csv in results folder of analysis folder 