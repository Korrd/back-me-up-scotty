# Script for running backup tasks on our server
# Q&A
    # This requires us to mount source and destination dirs.
    #   - How do we tell it what to backup?
    #       > By having the script receive arguments that tell it what to backup
    #   - How do we run the script?
    #       > By having a cron job that triggers it when desired
    #   - Why are we doing this inside a container?
    #       > So we can guarantee that the python env is always as we want it
    #   - This would be easier with bash. Why are we python'ing it?
    #       > Because we want to learn python, and the best way to do so is by using it

# Arguments
    # 0 = backup.py
    # 1 = /source/dir_or_file/to/compress
    # 2 = /destination/file.tar.gz
    # 3+ = Flags

import os
from datetime import timedelta
from sys import argv as args
from time import time

def main(args):
    FLAG_HELP = ("--help" in args)
    FLAG_OVERWRITE = ("--overwrite" in args)
    FLAG_DRY_RUN = ("--dry" in args) # for debugging purposes
    HELP_TEXT = "="*32 + "\n" + "| A wilde python backup script |".center(32) + "\n" + "="*32 + "\n\nUsage: backup.py source_file_or_dir destination_file.tar.gz [flags]\n- Flags must always go after source and destination.\n- Don't forget the .tar.gz on the target filename.\n" + "\n\nFlags:\n--overwrite     Overwrites destination file if it exists\n--help          Prints this help text\n--dry           Dry run, for debugging purposes"

    if (FLAG_HELP or len(args) < 3):
        print(HELP_TEXT)
        exit(1)

    if "--" in args[1] or "--" in args[2]:
        print(HELP_TEXT)
        exit(1)

    if not ".tar.gz" in args[2]:
        print(HELP_TEXT)
        exit(1)

    if FLAG_DRY_RUN:
        print("Running in dry mode...")
    
    # python3 backup.py ~/Downloads asdasd.tar.gz --dry --overwrite
    # SOURCE_DIR = os.path.abspath("/Users/vic/Downloads")
    # OUTPUT_FULLPATH = os.path.abspath("asdasd.tar.gz")
    # FLAG_DRY_RUN = True  # for debugging purposes

    SOURCE_DIR = os.path.abspath(args[1])
    OUTPUT_FULLPATH = os.path.abspath(args[2])
    OUTPUT_DIRNAME = os.path.dirname(os.path.abspath(OUTPUT_FULLPATH))
    OUTPUT_FILE_EXISTS = os.path.exists(OUTPUT_FULLPATH)
    OUTPUT_TMPFILE=f"{OUTPUT_FULLPATH}.tmp"

    # Check the source dir exists
    if not os.path.exists(SOURCE_DIR):
        print(f"The source at '{SOURCE_DIR}' does not exist.")
        exit(1)

    # Check the source dir is readable
    if not os.access(SOURCE_DIR, os.R_OK):
        print(f"The source at '{SOURCE_DIR}' is not readable. Check its permissions.")
        exit(1)

    # Create target dir if it does not exist
    if not os.path.exists(OUTPUT_DIRNAME):
        # If our target dir does not exist, we create it recursively
        print(f"The output dir at '{OUTPUT_DIRNAME}' does not exist. Creating it with permissions 0755...")
        os.makedirs(OUTPUT_DIRNAME, 0o755, exist_ok=True)
        print(f"'{OUTPUT_DIRNAME}' created!")

    # Ensure target dir is writable (if it got created by us, it will always be)
    if not os.access(OUTPUT_DIRNAME, os.W_OK):
        print(f"The source at '{OUTPUT_DIRNAME}' is not writable. Check its permissions.")
        exit(1)

    # Ensure we don't overwrite the target file unless the user explicitly wants to, to prevent mistakes
    if not FLAG_OVERWRITE and OUTPUT_FILE_EXISTS:
        print(f"Output file at '{OUTPUT_FULLPATH}' already exists. If you wish to overwrite it, run me with the \"--overwrite\" flag set.")
        exit(1)

    # Compress
    print(f"Compression started\n - Source:      {SOURCE_DIR}\n - Destination: {OUTPUT_FULLPATH}")
    START_TIME = time()
    # Compress on temp file
    compress(source = SOURCE_DIR, destination = OUTPUT_TMPFILE)
    if not FLAG_DRY_RUN:
        # Replace old file with new
        if OUTPUT_FILE_EXISTS:
            os.remove(OUTPUT_FULLPATH)
        os.rename(OUTPUT_TMPFILE, OUTPUT_FULLPATH)
    else: 
        os.remove(OUTPUT_TMPFILE)

    END_TIME = time()

    print("Finished.")
    print(f"Elapsed time: {timedelta(seconds=(END_TIME - START_TIME))}")
    

# Does the compression
def compress(source, destination):
    import multiprocessing
    # Using the native python module, compression will be single-threaded
    # import tarfile
    # tarfile.open(destination, "w:gz").add(source)
    
    # But if we use pigz, we can use all cores for it
    THREADS = multiprocessing.cpu_count()
    print(f"{THREADS} cores detected. Using them all for greater speed")
    bash_exec(f"tar cf - \"{source}\" | pigz -q -9 - p {THREADS} > \"{destination}\"")


def bash_exec(command=""):
  import subprocess as sp
  # Invoke shell command and return its exit code
  return sp.call(command, shell=True)


# Entrypoint --- PLACE ALWAYS AT THE END OF THE FILE
if __name__ == "__main__":
    main(args)
# ==================================================
