
# Data Manager

This program is meant to help manage data backup between a scientific compute cluster and S3 cloud storage.

## What This Program Does

This program focuses on a few things
 - tracks files that need to be backed up
 - computes and stores checksums for those files
 - uploads tracked files to S3
 - computes checksums on files downloaded from S3
 - checks that local checksums and S3 checksums match

## How This Program Works

This program works by running idempotent operations on a sqlite database. Pointers to local files are stored as records in the S3 database. Additional records for remote S3 files can be added and linked to local file records. Checksums, both local and remote, are performed as update operations on the records.

Validation works by checking if checksums for remote files match the checksum for their corresponding local file.

## Installation

```
pip install gimmebio.data_manager
pip install gimmebio.cli
```

## Commands

Add a list of files
```
gimmebio data add files -l <file list>
```

Compute local checksums
```
gimmebio data run md5
```

View files
```
gimmebio data list files
```

Add remotes
```
gimmebio data add s3-remote -k mason s3://masonbackup/mirrors/athena
```

Upload files
```
gimmebio data run upload 
```

More, Help
```
gimmedbio data --help
```

## Footer

Original Author: David Danko