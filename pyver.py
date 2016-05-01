# -*- coding: utf-8 -*-
"""
Version control for dummies
"""

__author__ = 'Neal Gordon'
__version__ = '0.1'

import os, shutil, datetime, sys, argparse, glob

def pyver(user, comment, archivefiles):
    '''
	main function of pyver. copys files from the current directory and creates an archive.
	the tab-delimmeted log file pyver.csv keeps a record of the file changes
    '''
    
    #user setting to create compressed zip files instead of copies of directories
    ziparchive = False    
    
    if not os.path.isdir('.pyver'):
        print('not currently a pyver repo, creating archive file directory .pyver')
        os.mkdir('.pyver')
        pyverlog = open(os.path.join('.pyver','pyver.log'),'a')
        pyverlog.write('User   Timestamp   ArchiveSize   Comment   Files  \n')        
        try:
            make_hidden('.pyver')
        except:
            print('failed to make .pyver hidden, which only works on windows')
        
    n = datetime.datetime.now()
    timestamp = datetime.datetime.strftime(n, '%Y%m%d%H%M%S')  
    archivepath = os.path.join('.pyver',timestamp)
    
	### was used to copy an entire directory but was wasteful
    #shutil.copytree('.', archivepath, ignore=shutil.ignore_patterns('.pyver'))

    print('----files archived----')
    os.mkdir(archivepath)
    for f in archivefiles:
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

    archivefilesstr = '|'.join(archivefiles)
    ''' writes what files were archived'''
    pyverlog = open(os.path.join('.pyver','pyver.log'),'a')
    pyverlog.write('%s , %s , %ikb , %s , %s\n' % (user,
                                           timestamp,
                                           archivesize,
                                           comment,
                                           archivefilesstr))
    pyverlog.close()
	
def make_hidden(hidedir):
    '''creates windows hidden folder
    can also use the windows command 
    os.system("attrib +s +h "+.pyver)
    '''
    import ctypes
    FILE_ATTRIBUTE_HIDDEN = 0x02
    ret = ctypes.windll.kernel32.SetFileAttributesW(hidedir, FILE_ATTRIBUTE_HIDDEN)
    if ret:
        print('.pyver set to Hidden')
    else:  # return code of zero indicates failure, raise Windows error
        raise ctypes.WinError()

def log():
    '''shows the contents of the pyver log file''' 
    
    if os.path.exists(os.path.join('.pyver','pyver.log')):
        pyverlog = open(os.path.join('.pyver','pyver.log'),'r')
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

def all_files(rootDir = '.', wildcard='.'):
    '''
    returns all files and directories that do not start with . or ~
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
            if '.' not in [x[0] for x in fullpath.split(os.sep)[1:]] and \
               '~' not in [x[0] for x in fullpath.split(os.sep)[1:]]:
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

if __name__=='__main__':
    '''
	executed if module is not imported
    '''
    
    if len(sys.argv) == 2 and sys.argv[1] == 'log':
        log()
    elif len(sys.argv) == 2 and sys.argv[1] == 'tree':
        tree('.')
    else:    
       
        p = argparse.ArgumentParser()
        p.add_argument('-u', '--user', 
                       default = os.path.split(os.path.expanduser('~'))[-1], 
                       help='''user that made the pyver entry''')
        p.add_argument('-f', '--files',
                       help='''omit to add all files. 
								add extensions EXAMPLE "*.txt|*.docx"
								add files separated by vertical line EXAMPLE "file1.txt|file2.txt" ''')
        p.add_argument('-c', '--comment', default = '', 
                       help='''add a comment enclosed in double quotes 
                               as to what changed. EXAMPLE "This is my comment" ''')                             
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
                #if '.pyver' in args.files:
                #    args.files.remove('.pyver')
                
        else:
            #files = os.listdir(os.getcwd())  ## does not capture subdirectories
            args.files = all_files('.','.')  # add all files
            #if '.pyver' in args.files:
            #    args.files.remove('.pyver')
        #user, archivefiles, comment = args.user, args.files, args.comment        
        #print(args.files)
        pyver(args.user, args.comment, args.files)      
        