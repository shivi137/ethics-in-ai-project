import pandas as pd   # for reading ecl files nd table data work on 
import os


import json   # for chnage of dict to json format jsonl files 


fp = os.path.dirname(os.path.abspath(__file__))   # have to get full path to reach a dir where there this code is there 



sheets = pd.read_excel(os.path.join(fp, "scenarios.xlsx"), sheet_name=None)   # in excel sfile there are many sheets for each lang eng hindi and more so to read each sheet and pandadata frame 

with open(os.path.join(fp, "scenarios.jsonl"), "w", encoding="utf-8") as file : 
    
      # open secanrio jsonl file and if not present then create and then open this file which will have json 


    for df in sheets.values(): #   go through each of the data frame of eng hindi and hinglish and benglai and values will have content of sheet withouit their nam eof sheet 
        df = df.astype(object).where(df.notna(), None)  #   empty cells become none


        for question in df.itertuples(index=False):  #   for each of the lang sheet loop pover all of the questions one by one each scebnario of all lang and have to not inclde index in that row tuple 
            scn_id = question[0].strip()   # remove extra forward backwrd spaces 



            row = {
                "id": scn_id,
                "pair": scn_id.rsplit("-", 1)[0],
                "variant": scn_id[-1],
                "domain": question[1],
                "language": question[2],
                "text": question[3].strip(),
                "options": list(question[4:8]),
            } # pyth dict have info about each ques in each of its row , id is the ques id of each scenario variant is the paitr A/B extracted fromm id  pair is remanining fdrom id after rmove variant , domain is the ques tyoe upi payment trealted or heakth or e commnerce shopping or travelkling public transport  text uis the actrual ques text and language is eng hindi hinglish  bhngali options are dec chooicve avalibale like act clrify regfuse escalate 



        
            file.write(json.dumps(row, ensure_ascii=False) + "\n")   # convert each row of dict to json object and then each new line new json object corrsponding to new scenario and then convert them to json file and write in scenarios . jsonl 