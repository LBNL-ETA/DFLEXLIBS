#!/usr/bin/env python3
"""Check the Brick HeatingOrCooling shapes against the example models.

Runs SHACL inference over each model and reports which shape classes each node
was labelled with. The conforming model should light up every connector shape;
the non-conforming model should light up almost nothing.

    python validate.py
"""
import sys
from pathlib import Path

import rdflib
from rdflib import RDF, Namespace

try:
    import pyshacl
except ImportError:
    sys.exit("pyshacl is required: pip install pyshacl")

OBC = Namespace("urn:hpflex/shapes#")
HERE = Path(__file__).resolve().parent
SHAPES_DIR = HERE.parent

# Nodes that must be recognised in the conforming model.
EXPECTED = [
    "Zone1", "Zone1_TCurZon", "Zone1_TCurZonSet", "Zone1_TPreTarSet",
    "Zone1_TSheTarSet", "Zone1_TDefSet", "Zone1_rouZonFla",
    "PBui", "PBuiThr", "Meter", "DemandFlexMode",
]
# Nodes that must NOT be recognised in the non-conforming model.
REJECTED = ["Zone2", "DuctTemp", "Zone2_TCurZon", "Zone2_TCurZonSet",
            "ChillerPower", "Zone3"]

# Nodes that may legitimately match some shapes but must never match others.
# This is the disambiguation guarantee: a demand flexibility event target is,
# by Brick subclass entailment, also a brick:Zone_Air_Temperature_Setpoint, so
# without an explicit exclusion it would be offered as a candidate for the
# active setpoint connector.
FORBIDDEN = {
    "Zone3_TSheTarSet": ["TCurZonSet", "TComZonSet"],
    "Zone1_TPreTarSet": ["TCurZonSet", "TComZonSet"],
    "Zone1_TSheTarSet": ["TCurZonSet", "TComZonSet"],
    "Zone1_TDefSet": ["TCurZonSet", "TComZonSet"],
}


def load_shapes():
    g = rdflib.Graph()
    g.parse(SHAPES_DIR / "obc-extensions.ttl", format="turtle")
    g.parse(SHAPES_DIR / "heating-or-cooling.ttl", format="turtle")
    return g


def infer(model_path):
    """Label every node in the model with the shape classes it conforms to."""
    data = rdflib.Graph()
    data.parse(model_path, format="turtle")
    # The extension vocabulary must be visible to the data graph so that
    # sh:class checks can follow the subclass chain up into Brick.
    data.parse(SHAPES_DIR / "obc-extensions.ttl", format="turtle")
    pyshacl.validate(data, shacl_graph=load_shapes(), advanced=True, inplace=True)

    labels = {}
    for node, cls in data.subject_objects(RDF.type):
        if str(cls).startswith(str(OBC)) and str(node).startswith("urn:example"):
            name = str(node).split("#")[-1]
            labels.setdefault(name, []).append(str(cls).split("#")[-1])
    return {k: sorted(v) for k, v in labels.items()}


def main():
    failures = []

    print("=== conforming-model.ttl ===")
    labels = conforming = infer(HERE / "conforming-model.ttl")
    for name in sorted(labels):
        print(f"  {name:<22} -> {labels[name]}")
    for name in EXPECTED:
        if name not in labels:
            failures.append(f"{name} should have been recognised but was not")

    print("\n=== non-conforming-model.ttl ===")
    labels = infer(HERE / "non-conforming-model.ttl")
    for name in sorted(labels):
        print(f"  {name:<22} -> {labels[name]}")
    for name in REJECTED:
        if name in labels:
            failures.append(f"{name} should have been rejected but matched {labels[name]}")

    for model_labels in (conforming, labels):
        for name, forbidden in FORBIDDEN.items():
            for shape in forbidden:
                if shape in model_labels.get(name, []):
                    failures.append(f"{name} must not match {shape}")

    print()
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print("PASS: expected nodes recognised, bad nodes rejected, no shape collisions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
