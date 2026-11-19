import os 
import json


sandbox_path = os.path.dirname(os.path.abspath(__file__))     
data_path = os.path.join(sandbox_path, "..", "data")               
ip = os.path.join(data_path, "scenarios.jsonl")
op = os.path.join(sandbox_path, "tool_calls.jsonl")

