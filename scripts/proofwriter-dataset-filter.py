# Filters the OWA depth-1 ProofWriter files for the binding experiment.
#
# For each theory:
#   - The allProofs, proofDetails and maxD fields are removed.
#   - Rules without "someone"/"something" (named-entity rules) are removed.
#     NRule and theory are updated to match the remaining rules.
#   - Only questions with QDep = 1 and answer True or False are kept.
#   - Inside each kept question, only proofs that
#       1. take exactly one step, and
#       2. use a rule whose variable also appears in its conclusion
#     are kept, in both proofs and proofsWithIntermediates.
#     QLen is recomputed from the shortest remaining proof.
#     A question with no proof left is removed.
#   - A theory is kept only if both of its depth-1 questions are left,
#     and the False question is the negation of the True one.
# Everything else is copied as it is.
#
# Run from the repository root:
#   python scripts/proofwriter-dataset-filter.py

import json
import re
from pathlib import Path

# Where the original files are, and where the filtered files are written.
INPUT_FOLDER = Path("data/proofwriter-dataset-V2020.12.3/OWA/depth-1")
OUTPUT_FOLDER = Path("data/proofwriter-subset")

# The two words the dataset uses for a variable in a rule's representation.
VARIABLE_WORDS = ['"someone"', '"something"']


# Returns True if the text contains "someone" or "something".
def has_variable(text):
    return any(word in text for word in VARIABLE_WORDS)


# Returns True if a rule's variable appears in its conclusion.
# A representation looks like: (((condition) (condition)) -> (conclusion))
# so the part after "->" is the conclusion.
def variable_in_conclusion(rule):
    conclusion = rule["representation"].split("->")[1]
    return has_variable(conclusion)


# Returns True if a single proof should be kept.
# A one-step proof looks like: ((triple8 triple6) -> rule3)
# so it contains exactly one "->", and the rule name comes after it.
def keep_proof(proof, rules):
    # More than one "->" means more than one step.
    if proof.count("->") != 1:
        return False

    rule_name = proof.split("->")[1].strip(" )")

    # The rule was removed because it names an entity.
    if rule_name not in rules:
        return False

    return variable_in_conclusion(rules[rule_name])


# Filters one theory. Returns None if nothing is left in it.
def filter_theory(theory):
    # Remove the fields that list every proof in the theory,
    # including proofs through rules removed below.
    del theory["allProofs"]
    del theory["proofDetails"]

    # Remove maxD: it is the depth of the deepest statement the original
    # theory can prove, and it may be wrong once rules are removed.
    del theory["maxD"]

    # Keep only rules that contain "someone" or "something".
    theory["rules"] = {
        name: rule
        for name, rule in theory["rules"].items()
        if has_variable(rule["representation"])
    }

    # Update the rule count to the remaining rules.
    theory["NRule"] = len(theory["rules"])

    # Rebuild the theory text: facts first, then the remaining rules,
    # joined with spaces, the same way the original dataset builds it.
    fact_texts = [fact["text"] for fact in theory["triples"].values()]
    rule_texts = [rule["text"] for rule in theory["rules"].values()]
    theory["theory"] = " ".join(fact_texts + rule_texts)

    kept_questions = {}

    for name, question in theory["questions"].items():
        # Drop depth-0 questions and "Unknown" answers.
        if question["QDep"] != 1 or question["answer"] == "Unknown":
            continue

        # The proofs field looks like: [(proof1 OR proof2)]
        # Remove the outer "[(" and ")]", then split on " OR ".
        proofs = question["proofs"][2:-2].split(" OR ")

        # proofsWithIntermediates has one entry per proof, in the same order.
        details = question["proofsWithIntermediates"]

        # Keep a proof and its entry in proofsWithIntermediates together.
        kept_proofs = []
        kept_details = []
        for proof, detail in zip(proofs, details):
            if keep_proof(proof, theory["rules"]):
                kept_proofs.append(proof)
                kept_details.append(detail)

        # No proof left: drop the question.
        if not kept_proofs:
            continue

        # Put the remaining proofs back in the same format.
        question["proofs"] = "[(" + " OR ".join(kept_proofs) + ")]"
        question["proofsWithIntermediates"] = kept_details

        # QLen is the number of facts and rules in the shortest proof,
        # e.g. ((triple8 triple6) -> rule3) has 3.
        question["QLen"] = min(
            len(re.findall(r"triple\d+|rule\d+", proof)) for proof in kept_proofs
        )

        kept_questions[name] = question

    # Keep the theory only if both of its depth-1 questions are left
    # (one True, one False).
    if len(kept_questions) != 2:
        return None

    # The two questions must be the same statement, one negated.
    # A representation ends with the sign: ... "+") or ... "-")
    # so [:-4] removes the sign and leaves the statement.
    statements = [question["representation"][:-4] for question in kept_questions.values()]
    if statements[0] != statements[1]:
        return None

    theory["questions"] = kept_questions
    return theory


# Filter train, dev and test, each into its own .json file.
for split in ["train", "dev", "test"]:
    kept_theories = []

    # Each line of a .jsonl file is one theory.
    with open(INPUT_FOLDER / f"meta-{split}.jsonl") as input_file:
        for line in input_file:
            theory = filter_theory(json.loads(line))
            if theory is not None:
                kept_theories.append(theory)

    # Write all kept theories as one JSON list.
    with open(OUTPUT_FOLDER / f"meta-{split}.json", "w") as output_file:
        json.dump(kept_theories, output_file, indent=2)

    print(f"{split}: {len(kept_theories)} theories kept")