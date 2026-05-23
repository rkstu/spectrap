"""Generate specs from LLMs under pressure conditions."""
import json
import os
import time
from pathlib import Path
from typing import Optional

from openai import OpenAI

from .prompts import CONDITIONS, FUNCTION_CONTEXT


def get_client(model: str) -> OpenAI:
    if "claude" in model.lower():
        return OpenAI(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            base_url="https://api.anthropic.com/v1/",
        )
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def generate_spec(
    function_key: str,
    condition_key: str,
    model: str = "gpt-4o-mini",
    output_dir: Path = Path("generated"),
    epoch: int = 0,
) -> dict:
    """Generate a spec under a given pressure condition.

    Returns dict with: model, function, condition, epoch, raw_response, output_path, timestamp
    """
    func_ctx = FUNCTION_CONTEXT[function_key]
    condition = CONDITIONS[condition_key]

    prompt = condition["user_template"].format(**func_ctx)

    base_url = os.environ.get("OPENAI_BASE_URL")
    client_kwargs = {"api_key": os.environ.get("OPENAI_API_KEY")}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    messages = [{"role": "user", "content": prompt}]
    if condition["system"]:
        messages.insert(0, {"role": "system", "content": condition["system"]})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1.0,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content

    # Extract code block if wrapped in markdown
    code = extract_code(raw)

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{function_key}__{condition_key}__{model.replace('/', '_')}__{epoch}.py"
    output_path = output_dir / filename
    output_path.write_text(code)

    meta = {
        "model": model,
        "function": function_key,
        "condition": condition_key,
        "condition_name": condition["name"],
        "pressure_level": condition["pressure_level"],
        "epoch": epoch,
        "output_path": str(output_path),
        "timestamp": time.time(),
        "raw_response": raw,
    }

    meta_path = output_dir / f"{filename}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))

    return meta


def extract_code(response: str) -> str:
    """Extract Python code from a markdown-wrapped response."""
    if "```python" in response:
        parts = response.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")[0]
            return code.strip()
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 2:
            code = parts[1]
            if code.startswith("\n"):
                code = code[1:]
            return code.strip()
    return response.strip()


def run_pilot(
    function_key: str = "json_roundtrip",
    conditions: Optional[list] = None,
    model: str = "gpt-4o-mini",
    output_dir: Path = Path("generated"),
    epochs: int = 1,
) -> list[dict]:
    """Run a pilot: one function, selected conditions, one model."""
    if conditions is None:
        conditions = ["D", "G3"]

    results = []
    for condition in conditions:
        for epoch in range(epochs):
            print(f"  Generating: {function_key} | {condition} | {model} | epoch {epoch}")
            meta = generate_spec(function_key, condition, model, output_dir, epoch)
            results.append(meta)
            time.sleep(1)  # Rate limit courtesy

    return results
