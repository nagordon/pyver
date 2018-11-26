# pyver 
Version control for dummies

## TODO  
* [ ] Append revision string (eg -00, -01, etc) on the end of an archive
* [ ] Clean up file view in log, make new lines?
* [ ] Add file watching with [watchdog](https://pypi.python.org/pypi/watchdog) , archive only changed files
* [ ] File locking or read only attributing with [py-filelock](https://github.com/benediktschmitt/py-filelock) or [fasteners](https://github.com/harlowja/fasteners) or [portalocker](https://github.com/WoLpH/portalocker) or [Filelock](https://github.com/dmfrey/FileLock)
* [ ] Console colors with [colorama?](https://pypi.python.org/pypi/colorama)
* [ ] Create GUI - https://github.com/chriskiehl/Gooey
* [ ] Package with [flit](http://flit.readthedocs.io/en/latest/index.html)
* [x] create file hash key
* [x] added file compare tool
* [x] added directory compare tool
* [x] added optional file character name prefixes to ignore

## Why pyver?  
The movtiation behind pyver, which is to creating a version control method which is very, very simple to track the history of files. The work-flow of pyver is something I do anyway when working on something simple that uses binary files, especially ones that are linked through the software that is required to read them (eg CAD designs). I will create multiple directories, eg v1, v2 and copy the entire contents of my in-progress files in it that I want to preserve the history. The issue with this is that when file names are changed, it can break links to dependent files, so keeping a file identical is important for tracking files. It was also a goal to use this tool over a network drive where multiple users can archive files as they wish 
There are a couple of other excellent options, but have a steep learning curve and some do not perform well with large binary files. Also, most version control systems are designed for code or text files, not large binanry files, like word documents or cad files. If you need more functionality, I'd recommend checking out these programs in order os simplicity. [boar VCS](https://bitbucket.org/mats_ekberg/boar/wiki/Home), [mercurial SCM](https://www.mercurial-scm.org/), [git](https://git-scm.com/) with the [large file extension](https://git-lfs.github.com/)

## The basic operation of this program goes like this
1) create some files  
2) run pyver and make a copy of your files  
3) make as many revisions as you want  
4) if you want to revert back to an older revision, grab files out of the dated .archive directories and put them in your current directory  

### Criteria for design
* Simplicity is your friend, obscurity is your enemy
* It is unacceptable to rename files to track versions. This accomplishes this by putting the files in different directories and keep your current file with the desired, persistent filename
* Can be used over a network drive. Does not require a central server. 
* Be OS agnostic (written in Python)
* know when the changes were made, with a comment and who did it

# Tutorial

## Install
Pyver can be installed using the `setup.py` file. This will allow you to use the `-m` flag directly from the command line anywhere on your system and a custom bat file is not required.
```
python setup.py install
```

## Help  
if you need help or want to see the documentation, either reference the [README](https://github.com/nagordon/pyver/blob/master/README.md) or refer to the local docstring.
```
pydoc pyver
```

## Run from the command line
If you prefer not running the setup.py, you can create a bat file and add it to the system variables. To get started, lets do a quick demo in windows. Brace yourself, you are going to have to use the command line. In your current directory with the pyver.py file, open a command line with ```shift+right_click``` and in the menu select ```Open command window here```. Another way to get a command window in your current directory is to type ```alt+D``` and type ```powershell``` or ```cmd```.
Now type 
```
python pyver.py
#or
python -m pyver
```

Done. That's it. We have created a pyver repository and made a backup of all the files in our current directory in an archive naming year-month-day-hour-minute-second. Anytime we need to make another backup, just repeat the last step.


## Add pyver path to system
OK, lets add a bit more work upfront to save us some typing for years to come. I would recommend having a windows folder that is added to the user PATH system variable where you can keep test or production scripts that you want to access from the command line. For example, I have ```C:\Users\Neal\bin``` that is in the system PATH variable which I can dump python scripts with the *.bat file. Now, all we have to type is ```pyver``` to get the same result as ```python pyver.py```
To add this path variable, type 

```
1) Start  
2) search "variables" and select "Edit Enviornmental variables for your account"
3) Add PATH variable or append with the path to the folder with your scripts  
```

## Building a Windows EXE
I used pyinstaller to build my own windows executable
```
pyinstaller pyver.py --onefile
```

## backing up multiple directories
If there are multiple directories that need backed up, one easy way is to select the folders in windows explorer and paste them into a script(similar to this one) and then modify the `filelist` variable as shown

```
import os

filelist = ["C:/Users/user1/test1", "C:/Users/user1/test2"]

for f in filelist:
    os.chdir(f)
    os.system('pyver -c "automated backup"')
    print('archived {}'.format(f))
print('complete')
```

## finish
There you have it. The worlds easiest version control system that multiple users can use over a network, retrieving your old files is trivial, and now you don't have to change your file names to all the silly things people come up with.
