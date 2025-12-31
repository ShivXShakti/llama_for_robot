import requests
import json
import re

LLAMA_URL = "http://0.0.0.0:5000/generate"

user_instruction = "Pick up the red cube using the left arm and place it into the blue bin."
scene_objects_json = {
  "objects": [
    {
      "id": "red_cube",
      "type": "cube",
      "pose": [0.45, 0.20, 0.75, 0.0, 0.0, 0.0, 1.0],
      "size": [0.05, 0.05, 0.05]
    },
    {
      "id": "blue_bin",
      "type": "container",
      "pose": [0.65, -0.25, 0.70, 0.0, 0.0, 0.0, 1.0],
      "size": [0.30, 0.25, 0.20]
    },
    {
      "id": "table",
      "type": "surface",
      "pose": [0.50, 0.00, 0.65, 0.0, 0.0, 0.0, 1.0]
    }
  ]
}
arm_limits = {
  "left_arm": {
    "x_range": [0.2, 0.7],
    "y_range": [0.0, 0.6],
    "z_range": [0.6, 1.2]
  },
  "right_arm": {
    "x_range": [0.2, 0.7],
    "y_range": [-0.6, 0.0],
    "z_range": [0.6, 1.2]
  }
}
collision_zones = {
  "zones": [
    {
      "name": "table_surface",
      "bounds": {
        "x": [0.2, 0.8],
        "y": [-0.5, 0.5],
        "z": [0.6, 0.7]
      }
    }
  ]
}




prompt = f"""
You are a task planning agent for a dual-arm robot.

You MUST output ONLY valid JSON.
DO NOT include explanations, comments, or markdown.
DO NOT include text before or after the JSON.

The robot has:
- Two arms: LEFT and RIGHT
- Each arm can pick, place, push, and hold objects

Input:
Instruction: "{user_instruction}"

Scene objects:
{json.dumps(scene_objects_json, indent=2)}

Robot constraints:
Reachable workspace:
{json.dumps(arm_limits, indent=2)}

Collision zones:
{json.dumps(collision_zones, indent=2)}

Your task:
Generate a plan as JSON with this schema:

{{
  "steps": [
    {{
      "arm": "left | right",
      "action": "move_to | pick | place | handoff | wait",
      "target_object": "string",
      "pose": [x, y, z, qx, qy, qz, qw],
      "dependencies": [int]
    }}
  ]
}}

Rules:
- Output ONLY JSON.
- Use minimal steps.
- Respect reachability limits.
- Avoid collision zones.
- If task is impossible, output exactly:
  {{ "status": "INFEASIBLE", "reason": "..." }}

Begin.
"""


payload = {
    "prompt": prompt,
    "max_new_tokens": 200,
    "temperature": 0.0
}

response = requests.post(LLAMA_URL, json=payload, timeout=10)

if response.status_code != 200:
    print("Server error:", response.text)
    exit(1)

data = response.json()

if "status" in data and data["status"] == "ERROR":
    print("LLM ERROR:")
    print(data["reason"])
    print("Raw output:", data.get("raw_output", ""))
    exit(1)

# Valid plan
print(json.dumps(data, indent=2))
