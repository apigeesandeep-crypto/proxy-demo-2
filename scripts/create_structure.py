#!/usr/bin/env python3
"""
create_structure.py
Creates the Apigee proxy folder scaffolding for proxy-demo-2.
Supports AssignMessage policy bundle structure.
"""

import os
import sys

PROXY_NAME = "proxy-demo-2"

DIRECTORIES = [
    "apiproxy",
    "apiproxy/proxies",
    "apiproxy/targets",
    "apiproxy/policies",
]


def create_directories(base_path: str = ".") -> None:
    for directory in DIRECTORIES:
        full_path = os.path.join(base_path, directory)
        os.makedirs(full_path, exist_ok=True)
        print(f"[OK] Created directory: {full_path}")


def main():
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"==> Scaffolding proxy bundle under: {os.path.abspath(base_path)}")
    create_directories(base_path)
    print("==> Directory scaffolding complete.")
    print("")
    print("    Folder structure:")
    for directory in DIRECTORIES:
        indent = "    " + ("    " * directory.count("/"))
        print(f"{indent}└── {os.path.basename(directory)}/")


if __name__ == "__main__":
    main()
