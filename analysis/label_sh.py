from utils import *  #    import file utils.py created in sam e folder nad also  will get  all of ots functions usable in this file  

df = loadLLMData()  #    loading ans given by all llm model responses by calling funct load llm datat in utils file   


def share(d):  # finding which per cent hoe much which label out pf asll lavel repopnse 
    counts = d["label"].value_counts().reindex(options, fill_value=0)  #    count how many times each label has came and also fill the missing values to n0 

    result = {"n_answers": len(d)}  #   result will hae totla no of ans all the labels repsomse 

    for l in options:  #   for all the label option decn choice avaliable go woth each of them   and find the per cent of them by theri count divide by total 
        result["pct_" + l] = percentage(counts[l] / len(d))  

    return result  #    ret the all label percents and total answers 


rows = []  #   empty list rows is list that will have all the rsults 

for m in models:  #   looping over each  model gpt claude gmini qwen deepseek for caclutaing the result and then through each of language english hindi hing;ish bengali 
    for lang in languages + ["ALL"]:  

        if lang == "ALL":  #  see if all language results arfe needed and needed for any specific lang eng hindi bengali etc 
            d = df[df["model"] == m]  #    from that model lllm select alll the lang ans 
        else:
            d = df[(df["model"] == m) & (df["language"] == lang)]  # else if need for any specific lang then select that lang and that model onlyu 

        rows.append({  # Store the results for this model and language
            "model": m,
            "language": lang,
            **share(d)
        })    #   saving the results needed for that model and that language and the share prcent 

saveResults(pd.DataFrame(rows), "labelsharebylang.csv")    #   in a file label share by lang csv in a foldeer save all the results of percent by lang


rows = []  # Create an empty list to store domain results

for m in models:  # loop over each model used gpt claude gemini qwen deepsk we had responses with 
    for domain in sorted(df["domain"].unique()):  #   loop over each avalible domin in data upi payment e commerce  healthcare and travel trasnport 

        d = df[(df["model"] == m) & (df["domain"] == domain)]  #  responses select with only that mode;l and that domiain that is in loop iteration for current

        rows.append({ 
            "model": m,
            "domain": domain,
            **share(d)
        })    #    saving resilt by appenidng ion that format for model name and domian name and the percent shate 

saveResults(pd.DataFrame(rows), "labelsharebydomain.csv")  #   save all resulta of percent by domin in a file share label by domaincsv in that folder 