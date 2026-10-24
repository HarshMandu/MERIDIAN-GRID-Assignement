"""Print dossier answers prepared from the supplied dossier and scanned Appendix B memo."""
import json
from pathlib import Path

path = Path(__file__).with_name("answers.json")
answers = json.loads(path.read_text(encoding="utf-8"))
for number, item in answers.items():
    print(f"{number}. {item['answer']}\n   Source: {item['source']}\n")
