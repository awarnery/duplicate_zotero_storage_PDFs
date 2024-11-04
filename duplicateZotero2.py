import os
import shutil
import csv
from datetime import datetime

# Define source and destination folders
source_folder = "/Users/ambroisewarnery/Zotero/storage"
destination_folder = "/Users/ambroisewarnery/Desktop/DuplicataZotero"
pdf_storage_folder = os.path.join(destination_folder, "PDF_files")
pdf_bin_folder = os.path.join(pdf_storage_folder, "PDF_bin")
metadata_folder = os.path.join(destination_folder, "metadata")
saved_pdf_csv = os.path.join(metadata_folder, "saved_pdf.csv")
last_run_date_txt = os.path.join(metadata_folder, "last_run_date.txt")
current_state_csv = os.path.join(metadata_folder, "current_state.csv")

# Ensure necessary folders exist
os.makedirs(pdf_storage_folder, exist_ok=True)
os.makedirs(pdf_bin_folder, exist_ok=True)
os.makedirs(metadata_folder, exist_ok=True)

# Helper function to get the modification date of a file
def get_modification_date(file_path):
    return datetime.fromtimestamp(os.path.getmtime(file_path))

# Step 1: Build current_state_csv with name, last modified date, and full path of PDFs in the source folder
def build_current_state_csv():
    with open(current_state_csv, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for root, _, files in os.walk(source_folder):
            for filename in files:
                if filename.endswith(".pdf"):
                    file_path = os.path.join(root, filename)
                    last_modified = get_modification_date(file_path)
                    writer.writerow([filename, last_modified.isoformat(), file_path])

# Step 2: Compare current_state_csv and saved_pdf_csv
def load_saved_pdfs():
    saved_pdfs = {}
    if os.path.exists(saved_pdf_csv):
        with open(saved_pdf_csv, mode="r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                saved_pdfs[row[0]] = (datetime.fromisoformat(row[1]), row[2])  # (last modified date, full path)
    return saved_pdfs

def load_current_pdfs():
    current_pdfs = {}
    with open(current_state_csv, mode="r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            current_pdfs[row[0]] = (datetime.fromisoformat(row[1]), row[2])  # (last modified date, full path)
    return current_pdfs

# Step 3: Copy new PDFs to the PDF storage folder using the full path from current_state_csv
def copy_new_pdfs(current_pdfs, saved_pdfs):
    for pdf_name, (last_modified, full_path) in current_pdfs.items():
        if pdf_name not in saved_pdfs:
            shutil.copy2(full_path, pdf_storage_folder)

# Step 4: Move deleted PDFs to PDF_bin
def move_deleted_pdfs(current_pdfs, saved_pdfs):
    for pdf_name in saved_pdfs.keys() - current_pdfs.keys():
        src_path = os.path.join(pdf_storage_folder, pdf_name)
        bin_path = os.path.join(pdf_bin_folder, pdf_name)
        shutil.move(src_path, bin_path)

# Step 5: Recopy PDFs with a modified date greater than the last run date
def copy_modified_pdfs(current_pdfs, saved_pdfs, last_run_date):
    for pdf_name, (last_modified, full_path) in current_pdfs.items():
        if last_modified > last_run_date and (pdf_name not in saved_pdfs or last_modified > saved_pdfs[pdf_name][0]):
            shutil.copy2(full_path, pdf_storage_folder)

# Step 6: Update saved_pdf_csv and last_run_date.txt
def update_saved_csv_and_date(current_pdfs):
    with open(saved_pdf_csv, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for pdf_name, (last_modified, full_path) in current_pdfs.items():
            writer.writerow([pdf_name, last_modified.isoformat(), full_path])

    with open(last_run_date_txt, mode="w") as datefile:
        datefile.write(datetime.now().isoformat())

# Main function to run all steps
def main():
    # Step 1: Build current_state_csv
    build_current_state_csv()

    # Step 2: Load current and saved PDF states
    saved_pdfs = load_saved_pdfs()
    current_pdfs = load_current_pdfs()

    # Load last run date
    if os.path.exists(last_run_date_txt):
        with open(last_run_date_txt, mode="r") as datefile:
            last_run_date = datetime.fromisoformat(datefile.read().strip())
    else:
        last_run_date = datetime.min

    # Step 3: Copy new PDFs
    copy_new_pdfs(current_pdfs, saved_pdfs)

    # Step 4: Move deleted PDFs to PDF_bin
    move_deleted_pdfs(current_pdfs, saved_pdfs)

    # Step 5: Copy modified PDFs if modified after the last run date
    copy_modified_pdfs(current_pdfs, saved_pdfs, last_run_date)

    # Step 6: Update saved_pdf_csv and last_run_date.txt
    update_saved_csv_and_date(current_pdfs)

# Run the script
if __name__ == "__main__":
    main()
