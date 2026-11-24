import itertools   #  library to get tools for working with collections more for permutaions and combnations genarating with data 
from utils import *   # imported the utils file of the foldeer to use funct 


# Load all answers given by the models across the 10 runs
df = loadLLMData()   #  calling load llm functin of utils python file to get the data of llm models 5 responses to every 64 ques in exp of analysyis 


counts = countDecisions(df)   #    times  each decn label has been made for each of 5 models and 64 scenarios and 4 langauges so 4 tupe of count on efor each of act ref escalte and clrify


ids = sorted(df.id.unique())   #   getting all the ids of scnerios but ll unique ones only not duploicate ones and also sort them in order 


pairs = sorted({i[:-2] for i in ids})  #  will have to find id sof origianl pair opf scenatios jsonl remove  2 char from last A/B  so will get the 32 oroiginal scenes id not added pair informtionn



rows = []   # list to hav eto find noise floor whivch mean that if i run a moderl many times ghere 10 tikes giving or asking sam etask or ques how much ans differ is because of noise random noise in model because model harness questn envrironment provider all are sam eso onlyu noise causeed that difference 

# Go through each model one by one
for m in models:  # looping over eacjh of 5 models one by one 

    # Calculate noise separately for each language and also for all languages together
    for lang in languages + ["ALL"]:  #  find noise for each of lang and all lang combined too

        langs = languages if lang == "ALL" else [lang]   #    only when calc for all lang and not speicifically one lang 

        
        noise = np.mean([
            probabilityDifferentWithin(counts[(m, i, l)])
            for i in ids
            for l in langs
        ])  #  probability within differeent is funt of utils py calling here to find prob that same ques of running same model randomly got but given diff decn also avg this fpor all lang and quetions ids is scn id and langs is all langauge 

        # Store the model name, language and calculated noise percentage
        rows.append({
            "model": m,
            "language": lang,
            "noise_floor_pct": percentage(noise)
        })   # in each row have model name lang and noise percent for each case of that runs

# Convert all the stored results into a dataframe and save them to a CSV file
saveResults(pd.DataFrame(rows), "noise.csv")  # csv file noise in sam eresult foldewer will have dataframe for all the saved resyltrs calcutaed 




rows = []   # minimal pair diff have to find and that too beyond noise bcoz random noise run can cause diff 


for m in models:
    for lang in languages + ["ALL"]:
        langs = languages if lang == "ALL" else [lang]

      
        twin = []   # list will save the prpb of 2 minimal pair same id but A/B diff ans for each pair 

        # Store the normal run to run variation of A and B for each pair
        noise = []   # to have normal npise coz of run many run sto model 

        
        for p in pairs:   # for all pairs

           
            twin.append(np.mean([
                probabilityDifferentBetween(
                    counts[(m, p + "-A", l)],
                    counts[(m, p + "-B", l)]
                )
                for l in langs
            ]))  #   find prpb one run for scene A nd sam efor scene B give diff diff ans select and avg over all of sucvh acorss selected langauges .. will know how much changing the scenarios A to B will change the decn label ans noise leave

            noise.append(np.mean([
                (
                    probabilityDifferentWithin(counts[(m, p + "-A", l)])
                    + probabilityDifferentWithin(counts[(m, p + "-B", l)])
                ) / 2
                for l in langs
            ]))  #  calc run over run s disagreement for scene A and scene B and avg over to get base noise for that given pair id will be useful to remove effect of chneg A to B and model random beheve over runs 


        extra = np.array(twin) - np.array(noise)   #   minus norml run over disgrrment from AVB disgree to get hoe much approx addition diagree happen by changing a to b or b to a find this separete for each pair 

        lo, hi = bootstrapCI(extra)   # bootstrp confid intrvla 95 % lower an dupper limitys for minimasl pair thing value

        rows.append({
            "model": m,
            "language": lang,
            "twin_differ_pct": percentage(np.mean(twin)),
            "noise_pct": percentage(np.mean(noise)),
            "twin_minus_noise_pct": percentage(extra.mean()),
            "ci_lo_pct": percentage(lo),
            "ci_hi_pct": percentage(hi)
        })  #  seaparte row save model and lang and avd percent of minimal pair dffernce cause nad nois epewrcent avg cause by modle randomness of manhy runs and other additionakl differnece in minus pct and also lower upopwr limits of confid intrval


saveResults(pd.DataFrame(rows), "minimal.csv") # dataframe to csv in same folder dsave file 



rows = []   # acroos lang disgrrememt removing noise cause compmnent digreement list to have thst results for all model and lang 


for m in models:


    for a, b in itertools.combinations(languages, 2):   # for 2 lang find all possible combinatioms possible nd have 4 lang so total 6 lang pairs diff pairs possible and for each model loop over

        cross = {
            i: probabilityDifferentBetween(
                counts[(m, i, a)],
                counts[(m, i, b)]
            )
            for i in ids
        }  #   id are scebnarios ques id and for each of that ques find for each 6 lang apir that prob that model ans differ in 2 lang used in that paiur  will measyre digreemnegt caused by those 2 lang 

 
        noise = {
            i: (
                probabilityDifferentWithin(counts[(m, i, a)])
                + probabilityDifferentWithin(counts[(m, i, b)])
            ) / 2
            for i in ids
        }    # for each id in scene ids of questiomns find avg run to run model noise in both pair lang a and b due to running so much time will give base disagrrment expected from random of model 

  
        excess = {
            i: cross[i] - noise[i]
            for i in ids
        }   #   minus noise normal run to runs from disagree cause between 2 languages  to know how much additional disagree caused with lang only 

        lo, hi = bootstrapCI(averagePerPair(excess))  #  calling boostrap funct of utils file find avg per pair of A,B version of each seven cluuubbed  will get one value for each pair and then calculate the 95 pwrcebt confid interval 

        
        rows.append({
            "model": m,
            "language_pair": a + " vs " + b,
            "disagree_pct": percentage(np.mean(list(cross.values()))),
            "noise_pct": percentage(np.mean(list(noise.values()))),
            "beyond_noise_pct": percentage(np.mean(list(excess.values())), 2),
            "ci_lo_pct": percentage(lo, 2),
            "ci_hi_pct": percentage(hi, 2)
        })  #  fsave in a row overall disgreement at many aspects of random run noise and excess ones disagree 

# Convert all the stored results into a dataframe and save them to a CSV file
saveResults(pd.DataFrame(rows), "crosslang.csv")