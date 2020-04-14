# -*- coding: utf-8 -*-
"""
diff an entire directory
"""

__author__ = 'Neal Gordon'
__version__ = '0.2'

import os, sys,filecmp, difflib

### uncomment if you want to use the graphic user interface
#from gooey import Gooey
#@Gooey 
def main():
    

        dirdiff(sys.argv[1], sys.argv[2])        
        
    
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
        print('created {}'.format(newfilename))
        f.write(diff)



if __name__=='__main__':
   '''
	executed if module is not imported
   '''
   
   main()