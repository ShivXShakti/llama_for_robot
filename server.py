# llm_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from llama_cpp import Llama
import json
import uvicorn

# ------------------------------
# 1️⃣ Define Request Model
# ------------------------------
class Req(BaseModel):
    prompt: str
    scene_objects: Dict[str, Any]  # e.g., {"red_cube": [...], "blue_bin": [...]}


# ------------------------------
# 2️⃣ Initialize LLaMA Model
# ------------------------------
llm = Llama(
    model_path="/home/cstar/llama_ws/models/llama3/llama-7b.Q4_K_M.gguf",
    n_gpu_layers=10,  # adjust based on your GPU/CPU
    n_ctx=2048
)

# ------------------------------
# 3️⃣ Create FastAPI App
# ------------------------------
app = FastAPI()

# ------------------------------
# 4️⃣ Health Check
# ------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------
# 5️⃣ Generate Plan Endpoint
# ------------------------------
@app.post("/generate")
def generate(req: Req):
    # 5a️⃣ System Prompt / Rules
    system_prompt = """
You are a robotics task planner for a dual-arm robot.

- Output ONLY valid JSON. Do NOT include text or markdown.
- Your JSON must be:
{
  "steps": [
    {
      "arm": "left or right",
      "action": "move_to, pick, place, handoff, wait",
      "target_object": "object id",
      "pose": [x,y,z,qx,qy,qz,qw],
      "dependencies": [int]
    }
  ]
}

Rules:
- Use minimal steps.
- Respect reachability and collision constraints.
- If a step is impossible, output exactly:
{ "status": "INFEASIBLE", "reason": "..." }
"""

    # 5b️⃣ User Instruction + Scene Objects
    user_instruction_block = f"""
Now, based on the following instruction and scene objects, generate a plan:

Instruction: "{req.prompt}"

Objects:
{json.dumps(req.scene_objects, indent=2)}
"""

    # 5c️⃣ Full Prompt
    full_prompt = f"{system_prompt}\n{user_instruction_block}\n"

    # 5d️⃣ Call LLaMA
    output = llm(
        prompt=full_prompt,
        max_tokens=400,
        temperature=0.0,
        stop=["###", "</s>"]
    )

    raw_text = output["choices"][0]["text"].strip()

    # 5e️⃣ Safely extract JSON
    try:
        start = raw_text.index("{")
        end = raw_text.rindex("}") + 1
        plan = json.loads(raw_text[start:end])
        return plan
    except Exception:
        return {
            "status": "INFEASIBLE",
            "reason": "Model did not produce valid JSON",
            "raw_output": raw_text
        }


# ------------------------------
# 6️⃣ Main
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info",
        timeout_keep_alive=120  # allow slow LLaMA generation
    )
