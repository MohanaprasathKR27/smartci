
import hashlib
import json
from pathlib import Path
import shutil

# Project directory
ROOT = Path(__file__).resolve().parent.parent

# Source directory
SRC_DIR = ROOT / "src"

# Cache directory
CACHE_DIR = ROOT / ".build_cache"

# Build artifacts directory
ARTIFACT_DIR = CACHE_DIR / "artifacts"

# Cache manifest
CACHE_FILE = CACHE_DIR / "cache_manifest.json"


# Define module dependencies
DEPENDENCIES = {
    "pricing.py": [],
    "cart.py": ["pricing.py"],
    "inventory.py": []
}


def calculate_hash(file_path):
    """Generate SHA-256 hash of a file."""
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def load_cache():
    """Load previous cache information."""

    if CACHE_FILE.exists():
        data = json.loads(CACHE_FILE.read_text())

        if "modules" not in data:
            return {"modules": {}}

        return data

    return {"modules": {}}

def save_cache(cache):
    """Save cache information."""

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    CACHE_FILE.write_text(
        json.dumps(cache, indent=4)
    )


def calculate_signature(module, signatures):
    """Calculate a signature using source and dependency hashes."""

    source_hash = calculate_hash(SRC_DIR / module)

    dependency_signatures = {
        dependency: signatures[dependency]
        for dependency in DEPENDENCIES[module]
    }

    data = {
        "source": source_hash,
        "dependencies": dependency_signatures
    }

    encoded = json.dumps(data, sort_keys=True).encode()

    return hashlib.sha256(encoded).hexdigest()


def main():

    print("\nSMART BUILD CACHE SYSTEM")
    print("========================")

    old_cache = load_cache()
    new_cache = {"modules": {}}

    signatures = {}

    # Process modules in dependency order
    for module in ["pricing.py", "cart.py", "inventory.py"]:

        signature = calculate_signature(module, signatures)
        signatures[module] = signature

        artifact = ARTIFACT_DIR / module

        previous = old_cache["modules"].get(module, {})

        cache_valid = (
            previous.get("signature") == signature
            and artifact.exists()
        )

        if cache_valid:
            print(f"CACHE HIT  : {module}")
        else:
            print(f"CACHE MISS : {module}")

            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

            # Simulate a build by copying source into an artifact
            shutil.copy2(SRC_DIR / module, artifact)

        new_cache["modules"][module] = {
            "signature": signature
        }

    save_cache(new_cache)

    print("\nBuild process completed.")
    print("Cache manifest updated.")


if __name__ == "__main__":
    main()
