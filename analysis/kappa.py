from utils import *  #   import utils py file from same folder and use its functions 


g = goldTable()  # load huamam response gold lavbels for each ques and human responsees total and counts 


english = {}  #   dict to save ques of english by their ids as key 


with open(scenariosPath, encoding="utf-8") as f:   #  open the file that have all scenarios of experiment 

    for line in f:  #  read all lines of file one by one and change each currnt line to pyth dict from json text rows and check if lang of ques in engloish or not if english thenn only continue 

        s = json.loads(line)
        if s["language"] == "English":
            english[s["id"]] = s      # if ques in englsh lang then saave englsh scene ques by it key id in dict so can find it later by ket any ques case 



perQ = g.copy()   #  making a diplicte cpy of human dec tables so add new cols and not changing original cols and table strctyure 
perQ.insert(0, "id", perQ.index)  # new col for ques id at 0 pos 

perQ["domain"] = [english[i]["domain"] for i in perQ["id"]] #     take ques id and find it domain as per english scenes in dictnry and make a col which will be colum for domain of that ques


perQ["text"] = [english[i]["text"] for i in perQ["id"]]   #  take ques id and by dict find its text as in original engls text and make column of taht text as colmn


perQ["gold_share_pct"] = (perQ["gold_share"] * 100).round(1)  #  chnage the majority count of any decn votes  to percent initallly was decimal and round off 1 dec plce 

saveResults(  #   saving per quest human agreement in csv
    perQ[["id", "domain", "text", "gold", "gold_share_pct", "n_people"] + ["votes_" + l for l in options]],  #   needed cols in csv ques id domain ques  no of peoppe its gold and gold percent share , vote cnt for each decn
    "perques.csv"  #  save per quest csv  file in results folder it will tell that for each of 64 questions for each ques how human chose decision which dec got majorty ans .. one row for each ques in csv file 
)




votes = g[["votes_" + l for l in options]].values.astype(float)  #   choose cols   that have all 4 dec option act clarify refuse escalate from datafrme to numpy arry  cant perform numerical on dataframe easy to have numerical calcultions on numpy


n = votes[0].sum()  #   add resp conuts for 1st ques so that can find total people no who responded fpr each ques case scenario


pairAgree = (votes * (votes - 1)).sum(axis=1) / (n * (n - 1))  #     take one each ques find portion of pairs of humans who took same decn v(v-1)  does no of pairs that agree for each decn optn then for each ques sum up agreeing pairs for all decn optns   divide by n n-1   to get no of human pairs 


labelShare = votes.sum(axis=0) / votes.sum()   #  suming  for each decn option all resp votes across all ques cases

luckAgree = (labelShare ** 2).sum()   #   each decn option overall share in total do square of that and add all will tell estimae how much by chnace agremnet   by how frequently choose each decn optn 


kappa = (pairAgree.mean() - luckAgree) / (1 - luckAgree)   #  fleiss kappa tells how much humasn agreee with each other removing by chance agreemnt find by comapre agreement happens acutual and agreemnet by chance  0 value tell all by chnace 1 tells real high agreemnet 


saveResults(  #  all human agrrrement disagreememt statts result store in one csv sepaarte file in folder results
    pd.DataFrame([{  #   panda datfram  that haves row with all statst 
        "n_people": int(n),  
        "n_questions": len(g),  
        "average_pct_choosing_most_common": round(100 * g["gold_share"].mean(), 1),  
        "fleiss_kappa": round(float(kappa), 3)  
    }]),  #  one dataframe row have n people that tells how many humans answered each question case scene n questions tell no of total questins of scenarios include in analysisi of data , average pct choosing most common finds avg percent of people who chose for all ques the majoritry label fleisss kappa contain kappa to round off 3 dec places 
    "fleisskappa.csv"  #  file fleiss kappa will have agreement disagrrememt of human statst 
)   