import json
import os
import hashlib
from marker.convert import convert_single_pdf
from marker.models import load_all_models
from pathlib import Path
from shutil import copy2

def generate_filename_hash(filename):
    """
    Generate a hash for a filename using blake2b
    """
    hash_object = hashlib.blake2b(filename.encode(), digest_size=8)
    return hash_object.hexdigest()

def convert_pdfs_to_markdown(input_dir, output_dir):
    """
    Convert all PDF files in the input directory to Markdown format with hashed filenames

    Args:
        input_dir (str): Input directory containing PDF files
        output_dir (str): Output directory for Markdown files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a directory for hashed PDF files
    hashed_pdf_dir = os.path.join(output_dir, "hashed_pdfs")
    os.makedirs(hashed_pdf_dir, exist_ok=True)

    # Load marker models once for all conversions
    model_lst = load_all_models()

    # Get all PDF files from input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

    # Create filename mapping dictionary
    filename_mapping = {}

    # First pass: Create filename mapping and copy files with hashed names
    for pdf_file in pdf_files:
        original_name = os.path.splitext(pdf_file)[0]
        hashed_name = generate_filename_hash(original_name)

        # Store mapping
        filename_mapping[hashed_name] = original_name

        # Copy file with hashed name
        original_path = os.path.join(input_dir, pdf_file)
        hashed_path = os.path.join(hashed_pdf_dir, f"{hashed_name}.pdf")
        copy2(original_path, hashed_path)

    # Save filename mapping
    mapping_file = os.path.join(output_dir, "filename_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(filename_mapping, f, indent=2, ensure_ascii=False)

    # Second pass: Convert PDFs to Markdown using hashed names
    for hashed_name, original_name in filename_mapping.items():
        pdf_path = os.path.join(hashed_pdf_dir, f"{hashed_name}.pdf")
        md_path = os.path.join(output_dir, f"{hashed_name}.md")

        print(f"Converting {original_name}.pdf to Markdown (hash: {hashed_name})...")
        try:
            # Convert PDF to Markdown
            full_text, images, out_meta = convert_single_pdf(pdf_path, model_lst)

            # Add original filename to metadata
            out_meta['original_filename'] = original_name

            # Write the markdown content to file
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(full_text)

            # Save metadata alongside markdown file
            meta_path = os.path.splitext(md_path)[0] + '_meta.json'
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(out_meta, f, indent=2, ensure_ascii=False)

            print(f"Successfully converted {original_name}.pdf to {hashed_name}.md")

        except Exception as e:
            print(f"Error converting {original_name}.pdf: {str(e)}")
            continue

if __name__ == "__main__":
    # Define input and output directories
    input_dir = "./papers"  # Directory containing PDF files
    output_dir = "./markdown"  # Directory for output Markdown files

    # Convert all PDFs to Markdown
    convert_pdfs_to_markdown(input_dir, output_dir)