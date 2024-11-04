import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, src_folder, dest_folder):
        self.src_folder = src_folder
        self.dest_folder = dest_folder

        # Copy existing PDF files at the start
        self.initial_copy()

    def initial_copy(self):
        for root, dirs, files in os.walk(self.src_folder):
            for file in files:
                if file.endswith('.pdf'):
                    self.copy_file(os.path.join(root, file), file)

    def on_created(self, event):
        if event.is_directory:
            return None
        elif event.src_path.endswith('.pdf'):
            self.copy_file(event.src_path, os.path.basename(event.src_path))

    def on_modified(self, event):
        if event.src_path.endswith('.pdf'):
            self.copy_file(event.src_path, os.path.basename(event.src_path))

    def on_deleted(self, event):
        if event.src_path.endswith('.pdf'):
            self.delete_file(os.path.basename(event.src_path))

    def copy_file(self, src_path, file_name):
        dest_path = os.path.join(self.dest_folder, file_name)

        # Ensure the destination directory exists
        os.makedirs(self.dest_folder, exist_ok=True)

        shutil.copy2(src_path, dest_path)

    def delete_file(self, file_name):
        dest_path = os.path.join(self.dest_folder, file_name)

        # Check if file exists in destination folder
        if os.path.exists(dest_path):
            os.remove(dest_path)

if __name__ == "__main__":
    source_folder = "/Users/ambroisewarnery/Zotero/storage"
    destination_folder = "/Users/ambroisewarnery/Desktop/Zotero"
    event_handler = NewFileHandler(source_folder, destination_folder)
    observer = Observer()
    observer.schedule(event_handler, source_folder, recursive=True) # Set recursive to True
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
