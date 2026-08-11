from ai_quality.evaluation.datasets import export_promptfoo, load_jsonl

if __name__ == "__main__":
    export_promptfoo(
        load_jsonl("datasets/golden/golden.jsonl"), "datasets/generated/promptfoo-golden.json"
    )
