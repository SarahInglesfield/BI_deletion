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
    out_file_names=[user+"_090524_newfilter_all_files.txt",user+"_090524_newfilter_filtered_files.json"]
    mk_output_files(out_file_names)

    # look for the users files
    if test:
        search_dirs = ["/bi/home/inglesfs/BI_deletion"]

    for location in search_dirs:
        print(location)
        file_list = find_files(user,location,test)

        #option to check outputs if running a test, without writing out
        if test:
            print(file_list)
            break

        #write output as a chunk for each location
        write_out_files(file_list,out_file_names,location)

    # Need to add some stuff for log file here
    

def write_out_files(file_list,out_file_names,location):
    
    # first write out everything to the all file
    with open(out_file_names[0], 'a',encoding="UTF8") as out:
        for name in file_list.keys():
            print(name,file=out)

    # now extract the keys which are kept by the filtering
    with open(out_file_names[1], 'a',encoding="UTF8") as out:
        
        for count, (name, size) in enumerate(file_list.items()):
            if size is not False:

                if location.startswith("/bi/home/") and count == 0:
                    print("[",file = out)
                else:
                    print(",", file = out)

                print(f"\u007b\n\"filename\":\"{name}\",", file = out)
                print(f"\"file_size\":\"{size}\",", file = out)
                print(f"\"delete_status\":true\n\u007d", end ="", file = out)
        
        if location == "/bi/scratch" :
            print(f"\n]", file = out)

         
def find_files(user,location,test): 

    all_files = {}

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
                    #store all the files to write out
                    # filename is the key, value is either false (if doesnt meet filtering criteria) or file size
                    # value is determined by the function filter_files
                    all_files.update({file_path:filter_files(f,file_path)})

            except KeyError:
                print(f"The user has been deleted:{file_path}")
                
            if test and count > 2:
                break
    
    #return the lists
    return(all_files)
    

def prune_dirs(dirs):

    dirs[:] = [d for d in dirs if d not in ["run_processing","Genomes"]]
    
    return(dirs)

def filter_files(file, file_path):
    keep_file = True

    # exclude files from initial directories which we aren't interested in
        # hidden directories
        # seqmonk cache and genome directories
        # installed software: R, python (including environments)
        # actually I dont think we can use starts with here because the file path could be anything...
        # we essentially need to get 
    filter_dirs = ["/\.","/seqmonk_cache/","/seqmonk_genomes/","/miniconda3/","/anaconda3/","/R/"]

    for pattern in filter_dirs:
        if re.search(pattern, file_path):
            keep_file = False
            break
    
    # exclude files with starts we aren't interested in 
        # exclude hidden files
    exclude_starts = (".")

    if file.startswith(exclude_starts):
        keep_file = False

    # # exclude conda environment files
    # if re.search("conda.+/", file_path):
    #     keep_file = False

    # End of filtering 
    # write output to filtered file
    if keep_file:
        size = human_size(os.stat(file_path).st_size)
    else:
        size = False

    return(size)


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

def parse_arguments():
    parser = argparse.ArgumentParser(description="""
    Script to generate a list of all files a user has and a filtered list of files to pass to web interface""")

    parser.add_argument("user", help="The username the files should belong to", type=str)
    parser.add_argument("--test", help="if specified, do a test run with small directory", action='store_true')

    options = parser.parse_args()
    return options

if (__name__ == "__main__"):
    main()

