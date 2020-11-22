# About
    # Script for running backup tasks on my home server
    # Coded by Victor M. Martin in Nov-2020 as an excercise for
    # learning python3 overnight for a do-or-die tech interview
    # https://github.com/Korrd/back-me-up-scotty

import os
from datetime import timedelta
from sys import argv as args
from time import time


def main(args):

    # Let's get our flags...
    FLAG_HELP = ("--help" in args)
    if FLAG_HELP:
        print_help_text()
        exit(1)

    FLAG_OVERWRITE = ("--overwrite" in args)
    FLAG_DRY_RUN = ("--dry" in args)  # for debugging purposes
    FILES_TO_EXCLUDE = get_argument_value(args=args, flag="--exclude").split(",")
    OUTPUT_FULLPATH = get_argument_value(args=args, flag="--target")
    SOURCE_DIR = get_argument_value(args=args, flag="--source")
    THREADS = get_argument_value(args=args, flag="--threads") or 0

    # ... and do some very basic validation to filter out Layer 8 issues ;)
    if OUTPUT_FULLPATH == "" or SOURCE_DIR == "":
        print_help_text()
        exit(1)

    if not ".tar.gz" in OUTPUT_FULLPATH:
        print_help_text()
        exit(1)

    if FLAG_DRY_RUN:
        print("Running in dry mode...")
    
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

    # Right. Everything seems to be in order. Let's do the deed.
    print(f"Compression started\n - Source:      {SOURCE_DIR}\n - Destination: {OUTPUT_FULLPATH}")
    START_TIME = time()

    result = compress(source = SOURCE_DIR, destination = OUTPUT_TMPFILE, exclude = FILES_TO_EXCLUDE, threads=THREADS)
    if not FLAG_DRY_RUN:
        # Replace old file with new
        if OUTPUT_FILE_EXISTS:
            os.remove(OUTPUT_FULLPATH)
        os.rename(OUTPUT_TMPFILE, OUTPUT_FULLPATH)
    else: 
        os.remove(OUTPUT_TMPFILE)

    END_TIME = time()

    print(f"Finished with exit code {result}.")
    print(f"Elapsed time: {timedelta(seconds=(END_TIME - START_TIME))}")
    

def compress(source, destination,threads=0,exclude=list):
    import multiprocessing

    # This exclude logic gets a list of paths, and proceeds as follows:
        # > If there is only one item, and that item is empty, then exclude will result in an empty string
        # > If there is only one valid element, the join will return that element without prefix,
        #   and the prefix gets added by concatenation
        # > If there is more than one item in the list, the first item on the list will get its prefix by
        #   concatenation, while the rest gets it from the join magic (which I totally dislike).
        #
        # Yeah, I know, it's dark as fuck, but hey! this is my first ever python script.
    items_to_exclude = ""
    if not (len(exclude) == 1 and exclude[0] == ""):
        items_to_exclude = "--exclude " + " --exclude ".join(exclude)

    # Thread count logic. We want to be sure to get the most performance out of it,
    # while also NOT murdering the CPU if the user specifies a too high thread count
    if int(threads) == 0: 
        threads = multiprocessing.cpu_count()
        print(f" - No thread count specified by user and {str(threads)} cores detected. Going trigger-happy!")
    elif int(threads) > multiprocessing.cpu_count():
        threads = multiprocessing.cpu_count()
        print( f" - Specified thread count is higher than this system's core count. I will use {str(threads)} instead.")
    else:
        print( f" - I Will use {str(threads)} threads as specified by the user")

    # As the native python tarfile library is single-threaded,
    # we will use pigz, so we can darle mas gasolina B-)
    return bash_exec(f"tar cf {items_to_exclude} - \"{source}\" | pigz -9 -p {threads} > \"{destination}\"")


def bash_exec(command=""):
  import subprocess as sp
  # Invoke shell command and return its exit code
  return sp.call(command, shell=True)


def print_help_text():
    print("="*32)
    print("| A wilde python backup script |".center(32))
    print("="*32)
    print("\n\nUsage: backup.py --source=source_file_or_dir --target=destination_file.tar.gz [flags]")
    print("- Don't forget the .tar.gz on the target filename.")
    print("\n\nFlags:")
    print(f"--dry                                          Dry run, for debugging purposes")
    print("--exclude=dir1[,file1,dir2,...,dirN,fileN]     Exclude specific stuff from target file")
    print(f"--help                                         Prints this help text")
    print("--overwrite                                    Overwrites destination file if it exists instead of aborting")
    print("--threads                                      Specifies amount of parallel threads for multicore systems. If unset, I will use them all")


def get_argument_value(args, flag, separator="="):
    for element in args:
        if element.startswith(flag):
            return element.split(separator)[1]
    return "" # Return empty if not found


# Entrypoint --- ALWAYS PLACE AT EOF
if __name__ == "__main__":
    main(args)
