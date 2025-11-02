import os
import hashlib
import shutil
from datetime import datetime

RECORD_FILE = "hash_record.txt"
DELIMITER = "-" * 50 + "\n"


# Hash calculation
def calculate_hash(file_path):
    """Return SHA-256 hex digest of the file, or None if not found."""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None


# Save a record (append)
def save_hash_record(filename, original_hash, changed_hash=None):
    """Append a human-readable record for this file to RECORD_FILE."""
    with open(RECORD_FILE, "a", encoding="utf-8") as f:
        f.write(f"Filename: {filename}\n")
        f.write(f"Original Hash: {original_hash}\n")
        if changed_hash:
            f.write(f"Changed Hash: {changed_hash}\n")
        f.write(f"Recorded At: {datetime.now().isoformat()}\n")
        f.write(DELIMITER)

# -------------------------
# Load original and last changed for a specific filename
# -------------------------
def load_hash_record_for(filename):
    """
    Parse RECORD_FILE and return (original_hash, last_changed_hash).
    original_hash is the FIRST recorded Original Hash for the filename (the true original).
    last_changed_hash is the most recent Changed Hash recorded for the filename (or None).
    Returns (None, None) if no record for filename exists.
    """
    if not os.path.exists(RECORD_FILE) or os.path.getsize(RECORD_FILE) == 0:
        return None, None

    with open(RECORD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # split into blocks by the delimiter
    raw_blocks = [b.strip() for b in content.split(DELIMITER) if b.strip()]
    original_hash = None
    last_changed_hash = None

    # parse blocks in forward order to get the first Original Hash
    for block in raw_blocks:
        lines = block.splitlines()
        block_info = {}
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                block_info[key.strip()] = val.strip()
        if block_info.get("Filename") == filename:
            if original_hash is None and "Original Hash" in block_info:
                original_hash = block_info["Original Hash"]

    # parse blocks in reverse order to get the latest Changed Hash
    for block in reversed(raw_blocks):
        lines = block.splitlines()
        block_info = {}
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                block_info[key.strip()] = val.strip()
        if block_info.get("Filename") == filename and "Changed Hash" in block_info:
            last_changed_hash = block_info["Changed Hash"]
            break

    return original_hash, last_changed_hash

# -------------------------
# Save file copies
# -------------------------
def save_original_copy(src_path, dest_folder="original_backup"):
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(src_path)
    dest = os.path.join(dest_folder, filename)
    # don't overwrite existing original backup (preserve the very first copy)
    if not os.path.exists(dest):
        shutil.copy2(src_path, dest)
    return dest

def save_changed_copy(src_path, dest_folder="changed_files"):
    os.makedirs(dest_folder, exist_ok=True)
    filename = os.path.basename(src_path)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{name}_changed_{timestamp}{ext}"
    dest = os.path.join(dest_folder, new_name)
    shutil.copy2(src_path, dest)
    return dest

# -------------------------
# Main
# -------------------------
def main():
    path = input("Enter the file path to monitor: ").strip().strip('"').strip("'")
    if not os.path.exists(path):
        print("❌ File not found.")
        return

    filename = os.path.basename(path)
    current_hash = calculate_hash(path)
    if current_hash is None:
        print("❌ Failed to read file.")
        return

    original_hash, last_changed_hash = load_hash_record_for(filename)

    # No record yet for this file => treat as first run for this filename
    if original_hash is None:
        # Save original copy and append a record (original hash)
        saved = save_original_copy(path, dest_folder="original_backup")
        save_hash_record(filename, current_hash)
        print(f"✅ First time: original saved to '{saved}' and original hash recorded.")
        return

    # If current equals original -> unchanged
    if current_hash == original_hash:
        print("✅ File is unchanged (matches stored original).")
        return

    # If current equals last changed -> already recorded this change
    if last_changed_hash is not None and current_hash == last_changed_hash:
        print("ℹ️ File modified, but this exact modification was already recorded earlier.")
        return

    # Otherwise: it's a new modification -> save changed copy and append record
    saved = save_changed_copy(path, dest_folder="changed_files")
    save_hash_record(filename, original_hash, current_hash)
    print(f"⚠️ File modified: saved changed copy to '{saved}' and recorded changed hash.")

if __name__ == "__main__":
    main()
