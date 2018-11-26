# -*- coding: utf-8 -*-
"""
Version control for dummies

https://github.com/nagordon/pyver
"""

__author__ = 'Neal Gordon'
__version__ = '0.2'

import os, shutil, time, datetime, sys, argparse, glob, hashlib, pickle, filecmp
import win32com.client, difflib
from distutils.util import strtobool
from datetime import timezone

def pyver(user, comment, archivefiles, ziparchive, duplicate):
    '''
    	main function of pyver. copys files from the current directory and creates an archive.
     comma-delimmeted log file pyver.log keeps a record of the file changes
    '''

    if not os.path.isdir('.archive'):
        print('not currently a pyver repo, creating archive file directory .archive')
        os.mkdir('.archive')
        pyverlog = open(os.path.join('.archive','pyver.log'),'a')
        pyverlog.write('User,      Timestamp,            Size,      Comment  \n')
        try:
            make_hidden('.archive')
        except:
            print('failed to make .archive hidden, which only works on windows')

    # parse past archives for unchanged files
    # read pickle file that has dictionary with all files and hash
    # when copying files, confirm it is not in the last copy with the same hash
    # if the file has changed, copy it, if it is the same, then leave it
    
    # read file history 
    if os.path.exists('.archive/pyver.pkl'):
        with open('.archive/pyver.pkl', 'rb') as f:
            pyver_dict = pickle.load(f)    
    else:
        pyver_dict = {}
    
    # create a list of archive directories from newest to oldest
    archivedirs = list(pyver_dict.keys())
    archivedirs.sort()
    archivedirs.reverse()
    
    archivenum = '%02d' % len(pyver_dict.keys())
    
    n = datetime.datetime.now()
    timestamp = archivenum + '_' + datetime.datetime.strftime(n, '%Y%m%d%H%M%S')
    # datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S') #create datetime object from string 
    archivepath = os.path.join('.archive',timestamp)    
    
    # create file list with hash for new set
    pyver_dict[timestamp] = {f:create_md5_hex_hash(f) for f in archivefiles}
    
    #create list of old unchanged files to omit from backup
    oldunchangedfiles = []
    if not duplicate:
        for f in pyver_dict[timestamp].keys():
            for k in archivedirs:
                if pyver_dict[k][f] == pyver_dict[timestamp][f]:
                    #print('{} file has not changed, skipping'.format(f))
                    oldunchangedfiles.append(f)
                    break
                
    # write new file list with hash
    with open('.archive/pyver.pkl', 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(pyver_dict, f)#, pickle.HIGHEST_PROTOCOL)    
    
    print('----files archived----')
    os.mkdir(archivepath)
    for f in archivefiles:
        if f in oldunchangedfiles:
            print('{} is an archived unchanged file, skipping new archive'.format(f))
            continue
        if not os.path.exists(os.path.dirname(os.path.join(archivepath, f))):
            os.makedirs(os.path.join(archivepath,os.path.dirname(f)))
        try:
            shutil.copy(f , os.path.join(archivepath, f))
            print(os.path.join(archivepath, f))
        except:
            print('%s copy failed. Is it open?' % os.path.join(archivepath, f))
        #print('directory %s created' % os.path.join(archivepath,os.path.dirname(f)))
    archivesize = sum([os.path.getsize(s) for s in os.listdir(archivepath)])/1e3 # kb

    ### makes a zip file instead
    if ziparchive:
        shutil.make_archive(archivepath,'zip', archivepath)
        shutil.rmtree(archivepath)

    #archivefilesstr = '|'.join(archivefiles)
    ''' writes what files were archived'''
    pyverlog = open(os.path.join('.archive','pyver.log'),'a')
    pyverlog.write('%s,      %s,    %i kb,     %s \n' % (user,
                                                         timestamp,
                                                         archivesize,
                                                         comment))
    pyverlog.close()

def make_hidden(hidedir):
    '''creates windows hidden folder
    can also use the windows command
    os.system("attrib +s +h "+.archive)
    '''
    import ctypes
    FILE_ATTRIBUTE_HIDDEN = 0x02
    ret = ctypes.windll.kernel32.SetFileAttributesW(hidedir, FILE_ATTRIBUTE_HIDDEN)
    if ret:
        print('.archive set to Hidden')
    else:  # return code of zero indicates failure, raise Windows error
        raise ctypes.WinError()

def log():
    '''shows the contents of the pyver log file'''

    if os.path.exists(os.path.join('.archive','pyver.log')):
        pyverlog = open(os.path.join('.archive','pyver.log'),'r')
        for k in pyverlog.readlines():
            print(k)
        pyverlog.close()
    else:
        print('not a pver repository')

def tree(path,indent=' '):
    '''recursiveley prints the contents of a directory'''
    for file in os.listdir(path):
        fullpath = path + '/' + file
        if os.path.isfile(fullpath):
            print('%s     %s  ' % (indent,file ) )
        else:   # os.path.isdir
            print('%s  ./%s ' % (indent,file ) )
            tree(fullpath,indent + '   |')

def make_win_exe():
    '''creates a windows exe file that allows the pyver program to be
        run without the windows interpreter
    '''
    os.system('pip install pyinstaller')
    os.system('pyinstaller pyver.py --onefile')

def all_files(rootDir = '.', wildcard = '.', prefixignore = '.~'):
    '''
    returns all files and directories that do not start with prefixignore
    accepts wildcards in the format *.py   or *.txt
    '''
    #rootDir = '.'
    files = []
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            fullpath = os.path.join(dirName, fname)
            # skip over files and folders that start with . or ~

            # os.path.splitext(f[-2])[1]      extension
            #if fullpath.split(os.sep)[1] != '.' and fullpath.split(os.sep)[1] != '~':
            #os.path.basename(fullpath)[0] != '.'
            #os.path.basename(fullpath)[0] != '~'
            
            # for all filenames confirm prefixignore char is not in the filename
            prefixlistbool = [p in [x[0] for x in fullpath.split(os.sep)[1:]] for p in prefixignore]
            
            # filter out prefixes
            if not sum([b for b in prefixlistbool if b]):
                #print(fullpath)
                fileext = os.path.splitext(fullpath)[1]
                if wildcard == fileext:
                    files.append(fullpath)
                    print('%s added %s' % (wildcard,fullpath))
                elif wildcard == '.':
                    files.append(fullpath)
                else:
                    print('extension %s not found or skipping' % (fileext))
    files = [x[2:] for x in files] # clear off .\\
    return files

def clearFiles(filetypes = ['exe','spec']):
    """ WARNING THIS WILL DELETE FILES SO USE CAREFULLY
        clears the files"""
    for fileext in filetypes:
        for f in glob.glob(os.path.dirname('.')+'/*.'+fileext):
            try:
                os.remove(f)
            except:
                pass

def clearFilesExcept(filetypes = ['py','txt','docx','xlsx']):
    """WARNING THIS WILL DELETE FILES SO USE CAREFULLY
        clears the files except filetypes"""
    for f in glob.glob('*.'):
        if os.path.splitext(f)[1] not in filetypes:
            try:
                os.remove(f)
            except:
                pass

def add_path(add_folder = "C:\\Users\\ngordon\\test"):
    '''temporarily adds path to the system PATH variable'''
    import sys
    sys.path.append(add_folder)



def create_md5_hex_hash(fname):
    '''
    return a md5 hash key for a individual file
    '''
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def find_modified_time(myfile):
    '''
    find when the file was last modified
    '''
    moddate = os.stat(myfile)[8] # there are 10 attributes this call returns and you want the next to last
    return time.ctime(moddate)


def create_windows_shortcut(targetfile, targetfolder):
    '''
    generate a shorcut to a windows file    

    # add if running in a thread
    pythoncom.CoInitialize() 

    targetfile = 'test1.xlsx'
    targetfolder = 'file_compare'
    '''
    
    # path to where you want to put the .lnk
    path = os.path.join(targetfolder, targetfile+'.lnk') 
    
    #icon = r'C:\path\to\icon\resource.ico' # not needed, but nice
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = targetfolder + '\\' + targetfile
    #shortcut.IconLocation = icon
    shortcut.WindowStyle = 1 # 7 - Minimized, 3 - Maximized, 1 - Normal
    shortcut.save()    
    

def files_same(f1,f2):
    '''
    https://docs.python.org/3.6/library/filecmp.html    
    returns  boolean if the files are the same
    '''
    return filecmp.cmp(f1,f2)
    
    
def dirdiff(dir1, dir2):
    '''
    Here is a simplified example of using the subdirs attribute to search 
    recursively through two directories to show common different files:
        
    dir1 = 'test1'
    dir2 = 'test2'
    '''
    
    print('----comparing directory {} and {}----'.format(dir1,dir2))
    dcmp = filecmp.dircmp(dir1, dir2) 
    #dcmp.report()
    dcmp.report_full_closure()

    # create html report for files that have changed    
    for name in dcmp.diff_files:
        print('created html diff report for {}'.format(name))
        filediff('{}/{}'.format(dir1, name) , '{}/{}'.format(dir2, name))


def string_to_bool(string):
    return bool(strtobool(str(string)))


def file_mtime(path):
    t = datetime.datetime.fromtimestamp(os.stat(path).st_mtime,
                               timezone.utc)
    return t.astimezone().isoformat()


def show_file_info(filename):
    '''
    path = 'README.md'
    '''    
    
    stat_info = os.stat(path)
    print('\tMode :', stat_info.st_mode)
    print('\tCreated :', time.ctime(stat_info.st_ctime))
    print('\tAccessed:', time.ctime(stat_info.st_atime))
    print('\tModified:', time.ctime(stat_info.st_mtime))


def filediff(fromfile, tofile):
    """
    Command line interface to difflib.py providing diffs in four formats:

    html:     generates side by side comparison with change highlights.
    
    """
    
    with open(fromfile) as ff:
        fromlines = ff.readlines()
    with open(tofile) as tf:
        tolines = tf.readlines()

    diff = difflib.HtmlDiff().make_file(fromlines,tolines,fromfile,tofile,context=True,numlines=2)

    # write new file list with hash
    newfilename = os.path.basename(fromfile) + '_' + os.path.basename(tofile) + '.html'
    with open(newfilename, 'w') as f:
        f.write(diff)



if __name__=='__main__':
    '''
	executed if module is not imported
    '''

    # if special flag is given, do not create archive but execute special program
    if len(sys.argv) == 2 and sys.argv[1] == 'log':
        log()
    elif len(sys.argv) >= 2 and sys.argv[1] == 'tree':
        path = sys.argv[2] if len(sys.argv) == 3 else '.'
        tree(path)
    elif len(sys.argv) == 4 and sys.argv[1] == 'filediff':
        filediff(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == 'dirdiff':
        dirdiff(sys.argv[2], sys.argv[3])        
        
    else:

        p = argparse.ArgumentParser()
        
        p.description = '| pyver | version: {} | author: {} |'.format(
                        __version__,__author__)

        
        p.add_argument('-u', '--user',
                       default = os.path.split(os.path.expanduser('~'))[-1],
                       help='''user that made the pyver entry''')
        p.add_argument('-f', '--files',
                       help='''omit to add all files.
								add extensions 
                                EXAMPLE "*.txt|*.docx"
								add files separated by vertical line 
                                EXAMPLE "file1.txt|file2.txt" ''')
        p.add_argument('-c', '--comment', default = '',
                       help='''add a comment enclosed in double quotes
                               as to what changed. 
                               EXAMPLE "This is my comment" ''')
        p.add_argument('-z', '--zip', default = False,
                       help='''default is to create directory, use zip flag to 
                               create a zip archive ''')        
        p.add_argument('-d', '--duplicate', default = True,
                       help='''default is to copy all files to archive 
                                directory, use dupe flag to skip unchanged files''')     
        p.add_argument('-p', '--prefixignore', default = None,
                       help='''default is to omit any filename that starts
                               with a '.' or '~'. to specify individual 
                               prefix omissions, list them without
                               puncuation such as '.~' 
                               If no omissions are desired, use "" ''')
                    
        args = p.parse_args()

        if args.files:
            # collect all files of a type
            tempfiles = args.files.split('|')
            args.files = []
            for t in tempfiles:
                if t[0] == '*':
                    args.files.extend(all_files('.', t[1:]))
                elif t not in os.listdir(os.getcwd()):
                    print('%s not found, skipping' % t)
                else:
                    args.files.append(t)
                # default to remove archive directory
                if '.archive' in args.files:
                    args.files.remove('.archive')
                    
        elif args.prefixignore == None:
            args.prefixignore = '~._'
            args.files = all_files('.','.',args.prefixignore)
        else:
            args.files = all_files('.','.',args.prefixignore)  # add all files

        
        args.duplicate = string_to_bool(args.duplicate)
        args.zip = string_to_bool(args.zip)
        
        pyver(args.user, args.comment, args.files, args.zip, args.duplicate)
