# back-me-up-scotty
A script to automate various backup tasks that must be run on my home server

---

## What am I?
Script for running backup tasks on my home server.
Coded by Victor M. Martin in Nov-2020 as an excercise for learning python3 overnight for a do-or-die tech interview

## Q&A

This requires us to mount source and destination dirs to our container
  - How do we tell it what to backup?
      > By having the script receive arguments that tell it what to backup
  - How do we run the script?
      > By invoking a docker container with params that does the deed
  - Why are we doing this inside a container?
      > So we can guarantee that the python env is always as we want it,
      > as envs on different systems tend to be a bloody mess
  - This would be easier with bash. Why are we python'ing it?
      > Because we want to learn python3, and the best way to do so is by coding
      > overcommented, overengineered crap which applies most of what we learned.
  - Is this meant for production?
      > NO WAY! Don't you dare! It's a newbie script meant to excercise & solidify
      > knowledge. As such, it is full of flaws and NOT meant for a productive env 

## Usage

```bash
docker run -d --rm \
    --name a-backup-task \
    -v /source/path/on/host:/tmp/source/path/on/container \
    -v /target/path/on/host:/tmp/target/path/on/container \
    korrd2/back-me-up-scotty:latest \
    python /usr/src/backup.py --source=/tmp/source/path/on/container --target=/tmp/target/path/on/container/filename.tar.gz \
    [insert flags here]
```

### Flags
```bash
--dry                                          Dry run, for debugging purposes
--exclude=dir1[,file1,dir2,...,dirN,fileN]     Exclude specific stuff from target file
--help                                         Prints this help text
--overwrite                                    Overwrites destination file if it exists instead of aborting
--threads                                      Specifies amount of parallel threads for multicore systems. If unset, I will use them all

```

## TODO
- Implement shorthanded argument flags
- Handle args without the need for an "=" for key=value differentiation and arg delimitation
- Handle args with paths that contain spaces
- Write some tests on build time
- Validate flag values some more
