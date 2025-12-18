import os
import zipfile
import uuid
import json
import tempfile

def build_zip(response_text: str) -> str:
    """
    Creates a temporary folder, writes the generated architecture into a file,
    zips it, and returns the filename.
    """
    artifact_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp()
    scaffold_path = os.path.join(temp_dir, "architecture.txt")

    # Write result file
    with open(scaffold_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(response_text, indent=2, ensure_ascii=False))

    zip_filename = f"{artifact_id}.zip"
    zip_filepath = os.path.join(temp_dir, zip_filename)

    with zipfile.ZipFile(zip_filepath, "w") as zipf:
        zipf.write(scaffold_path, arcname="architecture.txt")

    return zip_filename
