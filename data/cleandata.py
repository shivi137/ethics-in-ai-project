
# What this file does is that it Cleans the google form data and reshapes it. The input provided to this file is an .xlsx file
#   Output is csv file 
# Needs libraries pandas, openpyxl to function
# Doesn't handle missing data as there was no missing data.
# Can we used like this cleandata.py data.xlsx -o cleaned.xlsx 


# These are the things it does, in order as listed---
# 1. Reads file and figures out which block each submission was answered in
# 2. Removes multiple times form fills by the same email - if an email answered form in more than one languages, then keeps the one with lowest resource language, with Bengali as the lowest resource, then Hinglish, then Hindi, Then English. Come entries can be kept like Manas Awasthi
# 3. Some people didn't provide number as age, but text, or date of birth or just invalid data. So this file also cleans all the messy age entries.
# 4. Also Flags Attention which is our proxy of if we think the participant was actually paying attention while filling form. 
# 5. Shapes data to long format with one row per participant and scenario ansered pair.
# 6. Also adds scenario set ccolumn and variant column

import argparse            # to parse arguments to script
import datetime as dt
import re
import sys

import numpy as np, pandas as pd
from openpyxl.styles import  Font


N_SCEN = 64                                     # below are all the settings such as no of scens, block start, ranking of languages with lowest resourse as most preffered
BLOCK_START = {"English": 5, "Hindi": 69, "Hinglish": 133, "Bengali": 197}  
LANG_RANK = {"Bengali": 1, "Hinglish": 2, "Hindi": 3, "English": 4}         
SHEET_ORDER = [ "Long_Data", "Respondents", "Scenarios", "Age_Corrections",
               "Dropped_Submissions", "Removed_Inattentive", "Attention_Check"]




scenGroups = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12, 13], [14], [15, 16],      # these are the scennarios which differ in just one variable (which is inferred through natural language), which is often enough to flip a decision. We call them as minimal pairs
                   [17, 18], [19, 20], [21, 22], [23, 24], [25, 26], [27, 28, 29], [30],       #   Inside a language block, numbers are one based positions
                   [31, 32], [33, 34], [35, 36], [37, 38], [39, 40], [41, 42], [43, 44],
                   [45], [46], [47, 48], [49], [50], [51, 52], [53], [54], [55, 56], [57],
                   [58], [59], [60], [61, 62], [63, 64]]


categoryPrefixes = [                                   # These are just list of labels in each languages
    ("Act", "Act"), ("कार्य", "Act"), ("কাজ", "Act"),
    ("Clarify", "Clarify"), ("स्पष्टीकरण", "Clarify"), ("স্পষ্টীকরণ", "Clarify"),
    ("Refuse", "Refuse"), ("मना", "Refuse"), ("প্রত্যাখ্যান", "Refuse"),
    ("Escalate", "Escalate"), ("मानव", "Escalate"), ("মানব", "Escalate"),
]


def category(text):  #  cconvert for each resp dec label to the label category in englsih 
    s = str(text)
    for prefix, cat in categoryPrefixes:
        if s.startswith(prefix):
            return cat
    return None



def read_export(path):                             # starts reading from here xlss fime checks if file is excel and if file has expected no of columns 
    if not path.lower().endswith(".xlsx"): 
        sys.exit("Input must be an .xlsx file.")
    df = pd.read_excel(path)
    if df.shape[1] != 5 + 4 * N_SCEN:
        sys.exit(f"Expected {5 + 4 * N_SCEN} columns, found {df.shape[1]}.")
    cols = list(df.columns)
    info = {"ts": cols[0], "email": cols[1], "age": cols[2], "gender": cols[3], "lang": cols[4]}
    df["src_row"] = df.index + 2                      # Excel row number in the input
    df["email_norm"] = df[info["email"]].astype(str).str.strip().str.lower()

    # sanity check: nobody should have answered outside theri language block ie. the language they chose
    for i, r in df.iterrows():
        s = BLOCK_START[r[info["lang"]]]
        own = r.iloc[s:s + N_SCEN].notna().sum()
        total = r.iloc[5:5 + 4 * N_SCEN].notna().sum()
        if own != total:
            print(f"WARNING: row {i + 2} has answers outside its language block", file=sys.stderr)
    df["n_answered"] = [
        df.iloc[i, BLOCK_START[df.iloc[i][info["lang"]]]:BLOCK_START[df.iloc[i][info["lang"]]] + N_SCEN].notna().sum()
        for i in range(len(df))]
    return df, cols, info


# ------------------------------------------------------------------- dedupe
def deduplicate(df, info, keep_overrides):      #  finds if submit many times by email ids and give priority to low resource lang in many lang form filles if in same lang keep the one with most answered questions and ret 2 things seleected and removed submissions 
    df = df.copy()
    df["rank"] = df[info["lang"]].map(LANG_RANK)
    # an override pulls the chosen language to the front for that person
    for email, lang in keep_overrides.items():
        m = df.email_norm == email
        if not m.any():
            print(f"WARNING: override e-mail {email} not found", file=sys.stderr)
        df.loc[m, "rank"] = np.where(df.loc[m, info["lang"]] == lang, 0, 99)
    df = df.sort_values(["email_norm", "rank", "n_answered", info["ts"]],
                        ascending=[True, True, False, True])
    keep = df.drop_duplicates("email_norm", keep="first").copy()
    drop = df[~df.index.isin(keep.index)].copy()
    kmap = keep.set_index("email_norm")

    def why(r):   #   tells why submission drops by finding submission by mail and then checking lang override lang priority submission time and no of ans 
        k = kmap.loc[r.email_norm]
        if r.email_norm in keep_overrides and r[info["lang"]] != k[info["lang"]]:
            return f"Manual override: {k[info['lang']]} submission (row {k.src_row}) kept at user request"
        if r[info["lang"]] != k[info["lang"]]:
            return f"Higher-resource language ({r[info['lang']]}) than kept ({k[info['lang']]})"
        if r.n_answered != k.n_answered:
            return "Same language; fewer scenarios answered"
        return "Same language and completeness; later submission"

    drop["reason_dropped"] = drop.apply(why, axis=1)
    drop["kept_instead_src_row"] = drop.email_norm.map(kmap.src_row)
    drop["kept_language"] = drop.email_norm.map(kmap[info["lang"]])
    n_sub = df.groupby("email_norm").size()
    langs = df.groupby("email_norm")[info["lang"]].apply(
        lambda s: ", ".join(sorted(set(s), key=lambda x: LANG_RANK[x])))
    keep["n_submissions_original"] = keep.email_norm.map(n_sub)
    keep["languages_submitted"] = keep.email_norm.map(langs)
    return keep, drop


# --------------------------------------------------------------- age clean
def clean_age(raw, ts):   #   if age not in right format by respndent it cleans it .. check if it no and if its date of birth convert to age by calculating if date is not right messed up hadle that .gives clean age and tells what thing correct and note for that 
    
    s = str(raw).strip()
    if re.fullmatch(r"\d{1,3}", s):
        return int(s), "none", ""
    m = re.fullmatch(r"(\d{1,2})[ /\-.](\d{1,2})[ /\-.](\d{4})", s)
    if m:                                                # looks like a date of birth (D M YYYY)
        d, mo, y = map(int, m.groups())
        t = ts.date()
        try:
            b = dt.date(y, mo, d)
            age = t.year - b.year - ((t.month, t.day) < (b.month, b.day))
            return age, "dob_converted", f"Entry was a date of birth ({b.isoformat()}); age computed at submission date"
        except ValueError:                               # e.g. 30 Feb
            age = t.year - y if mo <= t.month else t.year - y - 1
            return age, "dob_invalid_estimated", (
                f'Entry "{s}" is not a valid date (day {d} does not exist in month {mo}); '
                f"age estimated from birth year {y} assuming birthday already passed in submission year")
    m = re.search(r"\d{1,3}", s)                         # stray text around a number
    if m:
        return int(m.group()), "stray_text_removed", f'Removed extra text from "{s}"'
    return None, "unparsed", f'Could not read "{s}"'


# ---------------------------------------------------------- attention check
def attention_table(df_all, info):   # each human ans check to find pattern telling human is not attentive while form filling for all submissions attention finding metrics calculate ..it checks most common ans share and no of diff ans alos lonest run of same ans ...combine all to table and give back dataframe 
    
    rows = []
    for _, r in df_all.iterrows():
        s = BLOCK_START[r[info["lang"]]]
        ans = [category(v) for v in r.iloc[s:s + N_SCEN] if pd.notna(v)]
        cnt = pd.Series(ans).value_counts()
        run = best = 0
        prev = None
        for a in ans:
            run = run + 1 if a == prev else 1
            prev = a
            best = max(best, run)
        top = cnt.iloc[0] / len(ans)
        rows.append(dict(src_row=r.src_row, email=r.email_norm, language=r[info["lang"]],
                         n_answered=len(ans), most_common_answer=cnt.index[0],
                         most_common_share=round(top, 3), distinct_answers=len(cnt),
                         longest_run=best))
    return pd.DataFrame(rows)


def flag(row, thr):   # seeing ans pattern give a attention label to any human who respond ... cheking most given ans and also longest run of that ans if the share of that ans is least the threshold set it does  clear but if most common ans is min 70 percent or consecutive run is min 30 then its borderline else its okay ... 3 lbls clear borderline ok
    if row.most_common_share >= thr:
        return "clear"
    if row.most_common_share >= 0.70 or row.longest_run >= 30:
        return "borderline"
    return "ok"


def consensus_agreement(long):    #  chekcs how much people who filled form agrees with each other on same ques it converts long xls file people by ques table . for each repondent check ans with all other respondent on each ques they ans ..find avg portion of other people who give same ans across all questions ...gives back series of consensus agreement scores 3 dec place round off 
   
    P = long.pivot(index="respondent_id", columns="scenario_id", values="response_category")
    out = {}
    for rid in P.index:
        others = P.drop(rid)
        out[rid] = np.mean([(others[s].dropna() == P.loc[rid, s]).mean()
                            for s in P.columns if pd.notna(P.loc[rid, s])])
    return pd.Series(out).round(3)


# -------------------------------------------------------------------- main
def main():    # main funct calling all functions and use 
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)  #  aceept by cmmnd line parser inputs 
    ap.add_argument("input")
    ap.add_argument("-o", "--out", default="cleaned_long.xlsx")
    ap.add_argument("--keep", action="append", default=[], metavar="EMAIL=LANGUAGE",
                    help="force which language to keep for one person (repeatable)")
    ap.add_argument("--straightline-threshold", type=float, default=0.9)
    ap.add_argument("--no-remove", action="store_true", help="flag straight-liners but keep them")
    a = ap.parse_args()  # read and store
    overrides = {}
    for item in a.keep:  #  check if lang select is valid 
        e, l = item.split("=")
        if l not in LANG_RANK:
            sys.exit(f"Unknown language {l}")
        overrides[e.strip().lower()] = l

    df, cols, info = read_export(a.input)    # read excel file verify structure prepar data for more processing 

    # 1. de-duplicate  remove duplicate if people submitted
    keep, drop = deduplicate(df, info, overrides)

    # 2. ages   #  age in right format cleaning 
    res = keep.apply(lambda r: clean_age(r[info["age"]], r[info["ts"]]), axis=1)
    keep["age_clean"] = [x[0] for x in res]
    keep["age_fix_type"] = [x[1] for x in res]
    keep["age_fix_note"] = [x[2] for x in res]

    # 3. ids (by submission time of the kept row; not renumbered after removals)  assignning independent ids to each person who filled form 
    keep = keep.sort_values(info["ts"]).reset_index(drop=True)
    keep["respondent_id"] = ["R%03d" % (i + 1) for i in range(len(keep))]

    # 4. scenario table + groups  create dict to save each ques variant group and size ..craeet all scenario data frame with id grp id size variant quesr test in all 4 lang 
    setmap = {}
    for gi, g in enumerate(scenGroups, 1):
        for vi, s in enumerate(g):
            setmap["S%02d" % s] = ("SET%02d" % gi, "single" if len(g) == 1 else "ABC"[vi], len(g))
    scen = pd.DataFrame([{
        "scenario_id": "S%02d" % (k + 1), "position": k + 1,
        "scenario_set": setmap["S%02d" % (k + 1)][0], "variant": setmap["S%02d" % (k + 1)][1],
        "variants_in_set": setmap["S%02d" % (k + 1)][2],
        **{f"text_{lg}": cols[st + k] for lg, st in BLOCK_START.items()}} for k in range(N_SCEN)])

    # 5. long format, language-matched text, exact response text   
    long_rows = []
    for _, r in keep.iterrows():
        lg = r[info["lang"]]
        st = BLOCK_START[lg]
        for k in range(N_SCEN):  #  keep scenes which are answered skip if missing respons dont fill or assume 
            v = r[cols[st + k]]
            if pd.isna(v):
                continue                                  
            sid = "S%02d" % (k + 1)
            long_rows.append(dict(respondent_id=r.respondent_id, language=lg, age=r.age_clean,
                                  gender=r[info["gender"]], scenario_id=sid,
                                  scenario_set=setmap[sid][0], variant=setmap[sid][1],
                                  scenario_text=cols[st + k], response=v,
                                  response_category=category(v)))
    long = pd.DataFrame(long_rows)  #   save ques and people who answered details each row will have human respondent id lang age gendeer scenario id set varinat text response and categpry convert all that to dataframe long
    assert long.response_category.notna().all(), "unrecognised answer label"

    resp = keep[["respondent_id", "email_norm", info["ts"], info["lang"], info["gender"], info["age"],
                 "age_clean", "age_fix_type", "age_fix_note", "n_answered",
                 "n_submissions_original", "languages_submitted", "src_row"]].copy()
    resp.columns = ["respondent_id", "email", "timestamp", "language", "gender", "age_original",
                    "age_clean", "age_fix_type", "age_fix_note", "n_answered",
                    "n_submissions_original", "languages_submitted", "source_row_in_original"]   #   create table one rwo per human with data demographics etc 
    resp["complete_64"] = resp.n_answered == N_SCEN

    # 6. attention check on every submission, summarised per person
    att = attention_table(df, info)  #  calc attention metrics attention table on each humann origianl reponse to find patterns and chose threhold to classify clear border ok   check which submission are reatined find worst attention flag per person and gives numerical prioritysorts by email flag priorty and share of ans that give most times 
    att["attention_flag"] = att.apply(lambda r: flag(r, a.straightline_threshold), axis=1)
    att["kept_in_cleaned"] = att.src_row.isin(resp.source_row_in_original)
    order = {"clear": 2, "borderline": 1, "ok": 0}
    worst = (att.assign(o=att.attention_flag.map(order))
             .sort_values(["email", "o", "most_common_share"], ascending=[True, False, False])
             .groupby("email").attention_flag.first())
    resp["attention_flag"] = resp.email.map(worst)
    resp["consensus_agreement"] = resp.respondent_id.map(consensus_agreement(long))

    removed = pd.DataFrame()   #  remove people ans who was not giving attention while submitting ans record which people got remove and why reason then make new index correct age thing 
    if not a.no_remove:
        gone = resp[resp.attention_flag == "clear"]
        removed = gone[["respondent_id", "email", "language", "n_answered", "source_row_in_original"]].copy()
        removed["reason"] = f"Attention check: one answer on >= {a.straightline_threshold:.0%} of scenarios"
        resp = resp[~resp.respondent_id.isin(gone.respondent_id)]
        long = long[~long.respondent_id.isin(gone.respondent_id)]
    resp = resp.reset_index(drop=True)
    long = long.reset_index(drop=True)
    ages = resp[resp.age_fix_type != "none"][["respondent_id", "email", "age_original", "age_clean",
                                              "age_fix_type", "age_fix_note", "source_row_in_original"]]
    dropped = drop[["src_row", "email_norm", info["ts"], info["lang"], info["age"], "n_answered",
                    "reason_dropped", "kept_instead_src_row", "kept_language"]].copy()
    dropped.columns = ["source_row_in_original", "email", "timestamp", "language", "age_original",
                       "n_answered", "reason_dropped", "kept_instead_src_row", "kept_language"]
    dropped = dropped.sort_values(["email", "timestamp"])

    
    sheets = { "Long_Data": long, "Respondents": resp, "Scenarios": scen,
              "Age_Corrections": ages, "Dropped_Submissions": dropped,
              "Removed_Inattentive": removed, "Attention_Check": att.drop(columns=[])}  # dict   store all dataframes write all data to excl file formats excel file first row bold all sheets and adjust widths of cols 
    with pd.ExcelWriter(a.out, engine="openpyxl") as w:
        for name in SHEET_ORDER:
            sheets[name].to_excel(w, name, index=False)
        for ws in w.book:
            for c in ws[1]:
                c.font = Font(bold=True)
            ws.freeze_panes = "A2"
            for col in ws.columns:
                width = max(len(str(v.value or "")) for v in col[:200]) + 2
                ws.column_dimensions[col[0].column_letter].width = min(max(10, width), 60)
            
    csv_path = re.sub(r"\.xlsx$", "", a.out) + ".csv"
    long.to_csv(csv_path, index=False, encoding="utf-8-sig")  
#  create csv file and long dataframe export also prints summary nd output details 
    print(f"{len(df)} submissions -> {len(keep)} unique people -> {len(resp)} after attention removal")
    print(f"long rows: {len(long)}   incomplete respondents: {int((~resp.complete_64).sum())}")
    print(f"wrote {a.out} and {csv_path}")


if __name__ == "__main__":   # dont call if its imported  to another file and called from there 
    main()
