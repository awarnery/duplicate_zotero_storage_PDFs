import os
import shutil
import csv
from datetime import datetime

# Define source and destination folders
source_folder = "/Users/ambroisewarnery/Zotero/storage"
destination_folder = "/Users/ambroisewarnery/Desktop/DuplicataZotero"
document_storage_folder = os.path.join(destination_folder, "PDF_files")
document_bin_folder = os.path.join(document_storage_folder, "PDF_bin")
metadata_folder = os.path.join(destination_folder, "metadata")
saved_document_csv = os.path.join(metadata_folder, "saved_pdf.csv")
last_run_date_txt = os.path.join(metadata_folder, "last_run_date.txt")
current_state_csv = os.path.join(metadata_folder, "current_state.csv")

# Define the file extension for the documents you want to manage
document_extensions = (".pdf",".epub", ".mp3")

# Ensure necessary folders exist
os.makedirs(document_storage_folder, exist_ok=True)
os.makedirs(document_bin_folder, exist_ok=True)
os.makedirs(metadata_folder, exist_ok=True)

# Helper function to get the modification date of a file
def get_modification_date(file_path):
    return datetime.fromtimestamp(os.path.getmtime(file_path))

# Step 1: Build current_state_csv with name, last modified date, and full path of documents in the source folder
def build_current_state_csv():
    with open(current_state_csv, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for root, _, files in os.walk(source_folder):
            for filename in files:
                if filename.endswith(document_extensions):
                    file_path = os.path.join(root, filename)
                    last_modified = get_modification_date(file_path)
                    writer.writerow([filename, last_modified.isoformat(), file_path])

# Step 2: Compare current_state_csv and saved_document_csv
def load_saved_documents():
    saved_documents = {}
    if os.path.exists(saved_document_csv):
        with open(saved_document_csv, mode="r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                saved_documents[row[0]] = (datetime.fromisoformat(row[1]), row[2])  # (last modified date, full path)
    return saved_documents

def load_current_documents():
    current_documents = {}
    with open(current_state_csv, mode="r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            current_documents[row[0]] = (datetime.fromisoformat(row[1]), row[2])  # (last modified date, full path)
    return current_documents

# Step 3: Copy new documents to the document storage folder using the full path from current_state_csv
def copy_new_documents(current_documents, saved_documents):
    for doc_name, (last_modified, full_path) in current_documents.items():
        if doc_name not in saved_documents:
            shutil.copy2(full_path, document_storage_folder)

# Step 4: Move deleted documents to Document_bin
def move_deleted_documents(current_documents, saved_documents):
    for doc_name in saved_documents.keys() - current_documents.keys():
        src_path = os.path.join(document_storage_folder, doc_name)
        bin_path = os.path.join(document_bin_folder, doc_name)
        shutil.move(src_path, bin_path)

# Step 5: Recopy documents with a modified date greater than the last run date
def copy_modified_documents(current_documents, saved_documents, last_run_date):
    for doc_name, (last_modified, full_path) in current_documents.items():
        if last_modified > last_run_date and (doc_name not in saved_documents or last_modified > saved_documents[doc_name][0]):
            shutil.copy2(full_path, document_storage_folder)

# Step 6: Update saved_document_csv and last_run_date.txt
def update_saved_csv_and_date(current_documents):
    with open(saved_document_csv, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for doc_name, (last_modified, full_path) in current_documents.items():
            writer.writerow([doc_name, last_modified.isoformat(), full_path])

    with open(last_run_date_txt, mode="w") as datefile:
        datefile.write(datetime.now().isoformat())

# Main function to run all steps
def main():
    # Step 1: Build current_state_csv
    build_current_state_csv()

    # Step 2: Load current and saved document states
    saved_documents = load_saved_documents()
    current_documents = load_current_documents()

    # Load last run date
    if os.path.exists(last_run_date_txt):
        with open(last_run_date_txt, mode="r") as datefile:
            last_run_date = datetime.fromisoformat(datefile.read().strip())
    else:
        last_run_date = datetime.min

    # Step 3: Copy new documents
    copy_new_documents(current_documents, saved_documents)

    # Step 4: Move deleted documents to Document_bin
    move_deleted_documents(current_documents, saved_documents)

    # Step 5: Copy modified documents if modified after the last run date
    copy_modified_documents(current_documents, saved_documents, last_run_date)

    # Step 6: Update saved_document_csv and last_run_date.txt
    update_saved_csv_and_date(current_documents)

# Run the script
if __name__ == "__main__":
    main()
