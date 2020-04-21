# -*- coding: utf-8 -*-
"""
Version control for dummies

https://github.com/nagordon/pyver

https://docs.python.org/3/library/argparse.html#the-parse-args-method

https://docs.python.org/3.8/library/filecmp.html
"""

__author__ = 'Neal Gordon'
__version__ = '0.3'

import os, shutil, time, datetime, sys, argparse, glob, hashlib, filecmp
import win32com.client, difflib
from distutils.util import strtobool
from datetime import timezone
import json
import natsort
# conda install -c anaconda natsort

#conda install pyinstaller

### uncomment if you want to use the graphic user interface
#from gooey import Gooey
#@Gooey 
def main():
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    
    subparsers = parser.add_subparsers(dest='subparser_name')
    
    parser.description = '| pyver | version: {} | author: {} |'.format(
                    __version__,__author__)

    # =========================================================================
    # FILE TOOLS
    # =========================================================================
    parser_log = subparsers.add_parser('log',
                                       help='prints pyver logs\n'\
                                       'Example--$ python -m pyver log') 
    parser_log.set_defaults(func=log)


    parser_tree = subparsers.add_parser('tree',
                                        help='print file tree\n'\
                                        'Example--$ python -m pyver tree\n'\
                                        'Example--$ pyver tree C:/Users/user/Desktop')
    parser_tree.add_argument('treedir',type=str,default='.')
    parser_tree.set_defaults(func=tree, treedir='.')


    parser_filediff = subparsers.add_parser('filediff',
                                        help='creates html file of the\n'\
                                        'differences of an ascii text file\n'
                                        'EXAMPLE--$ python -m pyver filediff')
    parser_filediff.set_defaults(func=filediff)  
    parser_filediff.add_argument('d1')
    parser_filediff.add_argument('d2')


    parser_dirdiff = subparsers.add_parser('dirdiff',
                                            help='creates an html file \n'\
                                            'of the differences of all \n'\
                                            'ascii text files in a directory\n'\
                                            'EXAMPLE--$ python -m pyver dirdiff')
    parser_dirdiff.add_argument('d1')
    parser_dirdiff.add_argument('d2')
    parser_dirdiff.set_defaults(func=dirdiff)  

    parser.set_defaults(treedir='.')
    # =========================================================================
    # PYVER FUNCTIONS
    # =========================================================================
    parser.add_argument('-u', '--user',
                    default = os.path.split(os.path.expanduser('~'))[-1],
                    help='user that made the pyver entry\n'\
                        'EXAMPLE--$ python -m pyver -u nagordon')
    
    parser.add_argument('-f', '--files',
                    default='',
                    help='Default is "" to to add all files.'\
                        'EXAMPLE of specific file extension wildcards\n'\
                        '$ python -m pyver -f "*.txt|*.docx" \n'\
                        'EXAMPLE for only individual files \n'\
                        '$ python -m pyver "file1.txt|file2.txt" ')
    
    parser.add_argument('-c', '--comment', default = '',
                    help='add a comment enclosed in double quotes. \n'\
                        'EXAMPLE--$ pyver -m pver -v "This is my comment"')
    
    parser.add_argument('-z', '--zip', default = False,
                    help='default is False to create a zipped archive.\n'\
                        'EXAMPLE--$ python -m pyver -z True')
    
    parser.add_argument('-d', '--duplicate', default = False,
                    help='default is to copy all files to archive \n'\
                        'directory regardless if the file has changed.\n'\
                        'Use duplicate flag to skip unchanged \n'\
                        'files based on hash key\n'\
                        'EXAMPLE--$ python -m pyver -d False')
    
    parser.add_argument('-p', '--prefixignore', default = '~._',
                        help='default is to omit any filename that starts\n'\
                                'with a "." or "~" or "_" \n'\
                                'To specify individual prefix omissions, list \n'\
                                'them without puncuation such as ".~" \n'\
                                'EXAMPLE-If no omissions are desired\n'\
                                '$ python -m pyver -p \n'\
                                'EXAMPLE to omit files that start with "g" \n'\
                                '$ python -m pyver -p g')
                
    
    # =========================================================================
    # Parse input
    # =========================================================================    
#    args = parser.parse_args(['dirdiff','./tutorial/test1','./tutorial/test2'])
#    args = parser.parse_args(['tree','.'])
#    args.func(args)
    args = parser.parse_args()
    #args.func(args)
#    
#    print(args.subparser_name)
 
    
    #myargs = [cleanquote(k) for k in sys.argv]
    if args.subparser_name == 'tree':
        path = sys.argv[2] if len(sys.argv) == 3 else '.'
        tree(path)
    elif args.subparser_name == 'log':
        log()
    elif args.subparser_name == 'filediff':
        filediff(sys.argv[2], sys.argv[3])
    elif args.subparser_name == 'dirdiff':
        print('args=',sys.argv)
        dirdiff(sys.argv[2], sys.argv[3])    
    

#     parser.parse_args(['tree'])
#    parser.parse_args(['tree','C:/Users/ngordon/bin/pyver'])
#    #parser.parse_args(["dirdiff './tutorial/test2' './tutorial/test2'"])

    else:
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



def cleanquote(s):
    '''clear off extra quotes'''
    
    return s.replace('"','').replace("'",'')
    

    
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
    if os.path.exists('.archive/pyver.jsn'):
        with open('.archive/pyver.jsn') as f:
            pyver_dict = json.load(f)
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
                if f in pyver_dict[k].keys(): # confirm not a new file
                    if pyver_dict[k][f] == pyver_dict[timestamp][f]:
                        #print('{} file has not changed, skipping'.format(f))
                        oldunchangedfiles.append(f)
                        break
    
    
    with open('.archive/pyver.jsn', 'w') as file:
         file.write(json.dumps(pyver_dict, ensure_ascii=True, indent=1))   

    print()
    print('---------- files archived in {} ----------'.format(timestamp))
    os.mkdir(archivepath)
    for f in archivefiles:
        if f in oldunchangedfiles:
            print('- unchanged skipping {}'.format(f))
            continue
        if not os.path.exists(os.path.dirname(os.path.join(archivepath, f))):
            os.makedirs(os.path.join(archivepath,os.path.dirname(f)))
        try:
            shutil.copy(f , os.path.join(archivepath, f))
            print('+ archived {}'.format(f))
        except:
            print('failed copy - {}\n'.format(os.path.join(archivepath, f)) )
        #print('directory %s created' % os.path.join(archivepath,os.path.dirname(f)))
    archivesize = sum([os.path.getsize(s) for s in os.listdir(archivepath)])/1e3 # kb
    print()

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

def tree(path='.', indent=' '):
    '''recursiveley prints the contents of a directory'''
    #path = path.replace('"','')  # remove extra quotes from args
    #path = path.replace("'",'')  # remove extra quotes from args
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


def find_files_recusive_glob(ext='png'):
    myimages = glob('**/*.'+ext, recursive=True)
    return myimages



def all_files2(ext='png', andcriteria=['.']):
    '''
    recursively finds files match match all criteria of a specific fiel extension
    '''
    myfiles = glob('**/*.'+ext, recursive=True)

    for c in andcriteria:
        myfiles = [k for k in myfiles if c in k]
    return natsort(myfiles)



def all_files(rootDir = '.', wildcard = '.', prefixignore = '.~'):
    '''
    returns all files and directories that do not start with prefixignore
    accepts wildcards in the format *.py   or *.txt
    '''

    files = []
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            fullpath = os.path.join(dirName, fname)
            
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
    IN WORK-NOT CURRENTLY USED
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
    
    returns True if the files are the same
    '''
    return filecmp.cmp(f1,f2)
    

def string_to_bool(string):
    '''
    returns a boolean type object given a string
    '''
    return bool(strtobool(str(string)))


def file_mtime(path):
    '''
    returns the file modified time
    '''
    t = datetime.datetime.fromtimestamp(os.stat(path).st_mtime,
                               timezone.utc)
    return t.astimezone().isoformat()


def show_file_info(filename):
    '''
    prints file info such as time created    
    
    '''    
    
    stat_info = os.stat(filename)
    print('\tMode :', stat_info.st_mode)
    print('\tCreated :', time.ctime(stat_info.st_ctime))
    print('\tAccessed:', time.ctime(stat_info.st_atime))
    print('\tModified:', time.ctime(stat_info.st_mtime))


def filediff(fromfile, tofile, addconext = False, contextlines=0):
    """
    Command line interface to difflib.py providing diffs in four formats:
    html:     generates side by side comparison with change highlights.
    
    """
    try:

        with open(fromfile) as ff:
            fromlines = ff.readlines()
        with open(tofile) as tf:
            tolines = tf.readlines()

        diff = difflib.HtmlDiff().make_file(fromlines,tolines,fromfile,tofile,context=True,numlines=2)

        # write new file list with hash
        newfilename = os.path.basename(fromfile) + '_' + os.path.basename(tofile) + '.html'
        with open(newfilename, 'w') as f:
            print('created {}'.format(newfilename))
            f.write(diff)
    except:
        filessame = filecmp.cmp(fromfile,tofile)
        if filessame:
            print('the files are the same')
        else:
            print('the files are different')



def dirdiff(dir1, dir2):
    '''
    Here is a simplified example of using the subdirs attribute to search 
    recursively through two directories to show common different files:
        
    dir1 = './tutorial/test1' 
    dir2 = './tutorial/test2'
    
    
    './tutorial/test1' './tutorial/test2'
    '''
    
    print('----comparing directory {} and {}----'.format(dir1,dir2))
    dcmp = filecmp.dircmp(dir1, dir2) 
    print(dcmp.report())
    dcmp.report_full_closure()

    # create html report for files that have changed    
    for name in dcmp.diff_files:
        try:
            print('created html diff report for {}'.format(name))
            filediff('{}/{}'.format(dir1, name) , '{}/{}'.format(dir2, name))
        except:
            print('failed html diff report for {}'.format(name))

if __name__=='__main__':
   '''
	executed if module is not imported
   dirdiff(sys.argv[1], sys.argv[2])   
    '''
   
   main()
