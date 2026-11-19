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

def mapping(pair, tool, idx=(1,)):    # funct to write tool in dictionary for each quest
    d[pair + "-A"] = {tool: list(idx)}
    d[pair + "-B"] = {tool: list(idx)}

