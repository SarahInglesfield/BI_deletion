#! python

import re
import os
import pathlib
import argparse

def main():

    # add input for filenames
    options = parse_arguments()

    # Include a testing setting here (set on the command line - default false)
    test= options.test

    # setup the details for the user and search locations
    user = options.user

    group= pathlib.Path("/bi/home/"+user).group()

    search_dirs = ["/bi/home/"+user,
                   "/bi/group/"+group,
                   "/bi/scratch"]

    # setup the output files
    out_file_names=[user+"_all_files.txt",user+"_filtered_files.txt"]
    mk_output_files(out_file_names)

    # look for the users files
    if test:
        search_dirs = ["/bi/home/inglesfs/BI_deletion"]

    for location in search_dirs:
        print(location)
        find_files(user,location,out_file_names,test)
    

def parse_arguments():
    parser = argparse.ArgumentParser(description="""
    Script to generate a list of all files a user has and a filtered list of files to pass to web interface""")

    parser.add_argument("user", help="The username the files should belong to", type=str)
    parser.add_argument("--test", help="if specified, do a test run with small directory", action='store_true')

    options = parser.parse_args()
    return options

def find_files(user,location,out_file_names,test):   
    
    for count, (dirpath, dirs, files) in enumerate(os.walk(location)):
        # ignores by default symlink directories
        
        # ignore certain directories when we're in the scratch as there shouldn't be any user data here 
        if location == "/bi/scratch":
            dirs = prune_dirs(dirs)
        
        for f in files:
            
            file_path= os.path.join(dirpath,f)
            #print(file_path)

            #ignore symlinks
            if(os.path.islink(file_path)):
                continue
            
            #only consider files that are owned by the user
            try:
                if(os.path.isfile(file_path) and pathlib.Path(file_path).owner() == user):
                    write_out_files(out_file_names[0],file_path)
                    filter_files(f, file_path,out_file_names[1])
            except KeyError:
                print(f"The user has been deleted:{file_path}")
                

            if test and count > 20:
                break

def prune_dirs(dirs):

    dirs[:] = [d for d in dirs if d not in ["run_processing","Genomes"]]
    
    return(dirs)

def filter_files(file, file_path,out_file_name):
    # exclude hidden directories

    if re.search("/\.[^/]+", file_path):
        return

    # exclude hidden files
    exclude_starts = (".")

    if file.startswith(exclude_starts):
        return

    # exclude conda environment files
    if re.search("conda.+/", file_path):
        return
    
    size = human_size(os.stat(file_path).st_size)

    # write output to filtered file
    write_out_files(out_file_name, "\t".join([file_path,size]))


def write_out_files(out_file_name, contents):
    with open(out_file_name, 'a',encoding="UTF8") as out:
        print(contents, file = out)


def human_size(size):
    if size < 1024:
        return_size = f"{size} B"
    elif size < pow(1024,2):
        return_size = f"{round(size/1024)} KB"
    elif size < pow(1024,3):
        return_size = f"{round(size/(pow(1024,2)))} MB"
    elif size < pow(1024,4):
        return_size = f"{round(size/(pow(1024,3)))} GB"
    else:
        return_size = size
    
    return(return_size)

def mk_output_files(out_file_names):
    for file in out_file_names:
        with open(file, 'w') as out:
            pass   
         
if (__name__ == "__main__"):
    main()

