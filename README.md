# Folder Organizer

## Introduction

This Python script is designed to organize files from a source folder to a destination folder while avoiding duplicates based on file hashes.
It categorizes files into subfolders, such as "photos" and "videos," and logs statistics about the process.
The script uses SQLite to track file hashes and sizes.

## Dependencies

Ensure that the following Python modules are installed before running the script:

* os: Provides a way to interact with the operating system.
* shutil: Offers file operations, such as moving and deleting.
* time: Enables time-related functions.
* logging: Facilitates logging for monitoring and debugging.
* hashlib: Computes hash values for file content.
* sqlite3: Interacts with the SQLite database.

## Configuration

Adjust the following variables in the script according to your preferences:

* source_folder: The path to the folder containing unorganized files.
* destination_folder: The path where organized files will be moved.
* database_path: The path to the SQLite database for storing file hashes.

## Functions

#### supported_extensions_condition(self, path)

Checks if a file path has a supported photo or video extension.

#### get_subfolder_from_extension(self, extension)

Determines the subfolder type based on the file extension.

#### calculate_hash(self, file_path)

Computes the SHA256 hash of a file.

#### convert_bytes_to_mb(self, bytes_size)

Converts file size from bytes to megabytes.

#### log_folder_statistics(self, source_folder)

Logs statistics about the processed folder.

#### log_folder_processing_status(self, source_folder, subfolder, total_files)

Logs the processing status of the folder.

#### move_files_without_duplicates(self, source, destination, connection)

Moves files from the source to the destination while avoiding duplicates.
Updates the SQLite database with file hashes and sizes.

## Running the Script

Set the source_folder, destination_folder, and database_path variables.

Execute the script using the following command:

~~~bash
python organizer.py
~~~

Monitor the script's progress and check the logs for information.

## Conclusion

This script helps keep your files organized by categorizing them into subfolders based on their content type. It uses file hashing to identify and avoid duplicates, providing an efficient and organized approach to file management.