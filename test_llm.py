from llm.llm_wrapper import generate_script_api
from pathlib import Path
from datetime import datetime

# test with a topic
script = generate_script_api("Photosynthesis", duration_seconds=50, audience="middle school")

# save to runs/
out_dir = Path("runs") / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
out_dir.mkdir(parents=True, exist_ok=True)

with open(out_dir / "script.txt", "w", encoding="utf-8") as f:
    f.write(script)

print("=== GENERATED SCRIPT ===\n")
print(script)
print("\nSaved at:", out_dir / "script.txt")
