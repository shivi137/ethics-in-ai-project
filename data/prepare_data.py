import pandas as pd
import os


import json


fp = os.path.dirname(os.path.abspath(__file__))   # finding  full path of excel sheet 



sheets = pd.read_excel(os.path.join(fp, "scenarios.xlsx"), sheet_name=None)

with open(os.path.join(fp, "scenarios.jsonl"), "w", encoding="utf-8") as file :
    for df in sheets.values():
        df = df.astype(object).where(df.notna(), None)
        for question in df.itertuples(index=False):
            scn_id = question[0].strip()



            row = {
                "id": scn_id,
                "pair": scn_id.rsplit("-", 1)[0],
                "variant": scn_id[-1],
                "domain": question[1],
                "language": question[2],
                "text": question[3].strip(),
                "options": list(question[4:8]),
            }



        
            file.write(json.dumps(row, ensure_ascii=False) + "\n")