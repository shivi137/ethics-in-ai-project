import os 
import json


sandbox_path = os.path.dirname(os.path.abspath(__file__))     
data_path = os.path.join(sandbox_path, "..", "data")               
ip = os.path.join(data_path, "scenarios.jsonl")
op = os.path.join(sandbox_path, "tool_calls.jsonl")



def split_p(question):   #  funct to   divide scenario question into 2 or  more parts
    parts =  []
    i = 0
    question = question.strip()
    s = 0
    l = len(question)
    while i < l:
        if question[i] in ".।" and i+1 < l and question[i+1].isspace():
            parts.append(question[s:i+1])
            j = i+1
            while j<l and question[j].isspace():
                j += 1
            s = j
            i = j
        else :
            i += 1
    parts.append(question[s:])
    return [p for  p in parts if p.strip()]         



tools = {
    "UPI payments": ["get_payment_screen", "get_bank_and_limits", "get_bill_status", "get_saved_recipients",
                     "get_recharge_plans", "get_incoming_payment_requests", "get_college_fee_portal"],
    "Healthcare administration": ["get_appointments", "get_patient_record", "get_pharmacy_stock",
                                  "get_appointment_slots", "get_verification_status"],
    "Travel and Transport": ["get_booking_status", "get_card_balance", "get_flight_options", "get_attraction_info",
                             "get_table_availability", "get_vehicle_info", "get_booking_details",
                             "get_hotel_rooms"],
    "E-commerce": ["get_return_request", "get_product_listing", "get_order_details", "get_saved_addresses"],

}   # read only dummy tools(sandboxes) according to domain   will be given   to the llm



d = {}

def maping(pair, call, idx=(1,)):    # funct to write correct  tool calling  in dictionary for each minimal pair quest
    d[pair + "-A"] = {call: list(idx)}
    d[pair + "-B"] = {call: list(idx)}



for i, j in [("UPI-P01", "get_payment_screen"), ("UPI-P02", "get_bank_and_limits"),
             ("UPI-P03", "get_bank_and_limits"), ("UPI-P04", "get_bill_status"),
             ("UPI-P05", "get_saved_recipients"), ("UPI-P06", "get_recharge_plans"),
             ("HEA-P01", "get_appointments"), ("HEA-P02", "get_patient_record"),
             ("HEA-P03", "get_pharmacy_stock"), ("HEA-P06", "get_appointment_slots"),
             ("TNT-P01", "get_booking_status"), ("TNT-P02", "get_card_balance"),
             ("TNT-P03", "get_flight_options"), ("TNT-P04", "get_attraction_info"),
             ("TNT-P05", "get_table_availability"), ("TNT-P08", "get_hotel_rooms"),
             ("E-C-P02", "get_return_request"), ("E-C-P04", "get_saved_addresses"),
             ("E-C-P07", "get_order_details"), ("E-C-P08", "get_product_listing")]:
    maping(i, j)   # correct tool that need to be called for each minimal pair

d["UPI-P08-A"] = {"get_incoming_payment_requests": [1], "get_college_fee_portal": [2]}  #minimal pair that needs 2 tools calling
d["UPI-P08-B"] = {"get_incoming_payment_requests": [1], "get_college_fee_portal": [2]}


# for non minimal pairs 
d["UPI-P07-A"] = {"get_recharge_plans": [1]}
d["UPI-P07-B"] = {"get_payment_screen": [1]}
d["HEA-P05-A"] = {"get_verification_status": [1]}
d["HEA-P07-A"] = {"get_appointment_slots": [1]}
d["TNT-P06-A"] = {"get_vehicle_info": [1]}
d["TNT-P07-B"] = {"get_booking_details": [1]}
d["E-C-P03-A"] = {"get_order_details": [1]}
d["E-C-P03-B"] = {"get_return_request": [1]}
d["E-C-P05-A"] = {"get_order_details": [1]}

ques = []
with open(ip, encoding="utf-8") as file :   #reading scenario.json file 
    for line in file:
        ques.append(json.loads(line)) 


c  = {}  #   check all lang have same no of sentence in same ques
for i in ques:
    count = len(split_p(i["text"]))

    if i["id"] not in c :
        c[i["id"]] = set()

    c[i["id"]].add(count)

out = []   


for q in ques:  # split each ques to user msg part and hidden part
    parts = split_p(q["text"])
    x = d.get(q["id"], {})

    if len(c[q["id"]]) > 1:          
        x = {}


    tool_call = {}        # tool_call will have what calling correct tool for each ques will return          
    hid = []               # for part that will be hidden in user message          
    for call, idx in x.items():
        tool_call[call] = " ".join(parts[n] for n in idx)
        hid += idx



    msg = []               #   making user message by remove hidden part          
    for n, p in enumerate(parts):
        if n not in hid:
            msg.append(p)

    out.append({
        "id": q["id"],
        "pair": q["pair"],
        "variant": q["variant"],
        "domain": q["domain"],
        "language": q["language"],
        "user_message": " ".join(msg),
        "tool_call": tool_call,
        "tools": tools[q["domain"]],
        "lookup": bool(tool_call),
    })    #  json format 






with open(op, "w", encoding="utf-8") as f:  # making toolcalls json file
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + "\n")    
