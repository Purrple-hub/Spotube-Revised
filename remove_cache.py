# i hate cache files so lowk imma remove them

# first i need to catch every single pycache file ig? but imma try with a simple scan

import os


def remove_cache_files(directory="."):
    #for .pyc only
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dir = os.path.join(root, dir_name)
                try:
                    os.rmdir(cache_dir)
                    print(f"Removed directory: {cache_dir}")
                except OSError as e:
                    print(f"Error removing directory {cache_dir}: {e}")
        for file_name in files:
            if file_name.endswith(".pyc"):
                cache_file = os.path.join(root, file_name)
                try:
                    os.remove(cache_file)
                    print(f"Removed file: {cache_file}")
                except OSError as e:
                    print(f"Error removing file {cache_file}: {e}")

                    # okay now what about the folders?
def remove_empty_dirs(directory="."):
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # Check if the directory is empty
                try:
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                except OSError as e:
                    print(f"Error removing directory {dir_path}: {e}")

if __name__ == "__main__":
    remove_cache_files()
    remove_empty_dirs()