from fastapi import FastAPI
from pydantic import BaseModel
from llama_cpp import Llama
import uvicorn
import json
import re

llm = Llama(
    model_path="/home/robot/Documents/kd_ws/llama_ws/models/llama3/mistral-7b-openorca.Q5_K_S.gguf",
    n_gpu_layers=10,
    n_ctx=2048
)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

class Req(BaseModel):
    prompt: str


SYSTEM_PROMPT = """
            You are a robot task parser.

            Convert the user command into STRICT JSON ONLY.
            DO NOT explain.
            DO NOT add text outside JSON.

            Allowed actions:
            - pick
            - place
            - hold
            - none

            JSON FORMAT (MANDATORY):
            {
            "action": "<pick|place|hold|none>",
            "object": "<object name or none>",
            "place_location": "<location or none>"
            }

            Rules:
            - "object" = object being manipulated
            - "place_location" = where object should be placed
            - If place location is not mentioned, return "none"
            - If only pick is mentioned, place_location = "none"
            - If command is unclear, set fields to "none"

            Examples:
            User: "pick up the cup"
            Response:
            {"action":"pick","object":"cup","place_location":"none"}

            User: "pick the cup and place it on the table"
            Response:
            {"action":"pick","object":"cup","place_location":"table"}

            User: "move the bottle into the red container"
            Response:
            {"action":"place","object":"bottle","place_location":"red container"}

            User: "wait"
            Response:
            {"action":"hold","object":"none","place_location":"none"}
"""


def extract_json(text: str):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Safe fallback
    return {
        "action": "none",
        "object": "none",
        "place_location": "none"
    }


@app.post("/generate")
def generate(r: Req):
    prompt_text = f"""
### System:
{SYSTEM_PROMPT}

### User:
{r.prompt}

### Response:
"""

    output = llm(
        prompt=prompt_text,
        max_tokens=160,
        temperature=0.2,
        top_p=0.9,
        stop=["###"]
    )

    raw_text = output["choices"][0]["text"].strip()
    parsed = extract_json(raw_text)

    # Enforce keys always exist
    return {
        "action": parsed.get("action", "none"),
        "object": parsed.get("object", "none"),
        "place_location": parsed.get("place_location", "none")
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
