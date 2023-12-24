import os
import shutil
import time
import logging
import hashlib
import sqlite3

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class FolderProcessor:
    def __init__(self):
        self.last_status_time = time.time()
        self.files_verified = 0
        self.total_files_processed = 0
        self.total_files_moved = 0
        self.total_duplicates_deleted = 0

    def supported_extensions_condition(self, path):
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']
        video_extensions = ['.mp4', '.m4v', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg']
        return any(path.lower().endswith(extension) for extension in photo_extensions + video_extensions)

    def get_subfolder_from_extension(self, extension):
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']
        video_extensions = ['.mp4', '.m4v', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpg', '.mpeg']
        if extension in photo_extensions:
            return 'photos'
        elif extension in video_extensions:
            return 'videos'
        else:
            return None

    def calculate_hash(self, file_path):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256.update(byte_block)
        return sha256.hexdigest()

    def convert_bytes_to_mb(self, bytes_size):
        return bytes_size / (1024 ** 2)

    def log_folder_statistics(self, source_folder):
        logging.warning(f"Statistics for folder: {source_folder}")
        logging.warning(f"Total number of files: {self.total_files_processed}")
        logging.warning(f"Files moved: {self.total_files_moved}")
        logging.warning(f"Duplicates deleted: {self.total_duplicates_deleted}")

    def log_folder_processing_status(self, source_folder, subfolder, total_files):
        current_time = time.time()
        if current_time - self.last_status_time >= 10:
            remaining_files = total_files - self.files_verified
            logging.warning(f"Processing folder: {os.path.join(source_folder, subfolder)} - {self.files_verified} files verified, {remaining_files} files remaining.")
            self.last_status_time = current_time

    def move_files_without_duplicates(self, source, destination, connection):
        total_files = sum([len(files) for _, _, files in os.walk(source)])
        
        for root, dirs, files in os.walk(source):
            subfolder = None

            for file in files:
                full_source_path = os.path.join(root, file)

                if self.supported_extensions_condition(full_source_path):
                    self.total_files_processed += 1

                    file_hash = self.calculate_hash(full_source_path)

                    for _ in range(5):
                        try:
                            cursor = connection.cursor()
                            cursor.execute('SELECT * FROM hashes WHERE hash=?', (file_hash,))
                            existing_entry = cursor.fetchone()

                            if existing_entry:
                                os.remove(full_source_path)
                                logging.info(f"Duplicate file deleted: {file}")
                                self.total_duplicates_deleted += 1
                                break
                            else:
                                relative_path = os.path.relpath(full_source_path, source)
                                subfolders = os.path.dirname(relative_path).split(os.path.sep)
                                subfolder = next((sf for sf in subfolders if sf), None)

                                if subfolder:
                                    self.log_folder_processing_status(source, subfolder, total_files)

                                extension = os.path.splitext(file)[1].lower()
                                subfolder_type = self.get_subfolder_from_extension(extension)

                                if subfolder_type:
                                    full_destination_folder = os.path.join(destination, subfolder, subfolder_type)

                                    if not os.path.exists(full_destination_folder):
                                        os.makedirs(full_destination_folder)

                                    existing_files = os.listdir(full_destination_folder)
                                    last_number = max([int(fname.split(' ')[-1].split('.')[0]) for fname in existing_files], default=0)

                                    new_file_name = f"{subfolder} {str(last_number + 1).zfill(6)}{extension}"
                                    full_destination_path = os.path.join(full_destination_folder, new_file_name)

                                    shutil.move(full_source_path, full_destination_path)

                                    file_size_bytes = os.path.getsize(full_destination_path)
                                    file_size_mb = self.convert_bytes_to_mb(file_size_bytes)
                                    cursor.execute('INSERT INTO hashes VALUES (?, ?, ?)', (file_hash, file_size_mb, extension))
                                    connection.commit()

                                    time.sleep(0.2)
                                    while os.path.exists(full_source_path):
                                        time.sleep(1)

                                    self.files_verified += 1
                                    self.total_files_moved += 1
                                    break

                        except sqlite3.OperationalError as e:
                            logging.warning(f"Database is locked. Retrying... {e}")
                            time.sleep(1)
                    else:
                        logging.error("Failed after multiple attempts. Skipping file.")

        try:
            shutil.rmtree(source)
            logging.info(f"Source folder deleted: {source}")
        except OSError as e:
            logging.error(f"Error deleting source folder: {source} - {e}")

source_folder = r'Z:\Downloaded\Organizing'
destination_folder = r'S:\Content Creators\Exclusive Content'
database_path = r"Z:\Utils\Databases\hashes.db"

logging.warning(f"Processing folder: {source_folder}")

processor = FolderProcessor()
connection = sqlite3.connect(database_path)
processor.move_files_without_duplicates(source_folder, destination_folder, connection)
processor.log_folder_statistics(source_folder)
connection.close()

logging.warning(f"Processing finished for folder: {source_folder}")