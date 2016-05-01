# pyver 
Version control for dummies

## TODO  
* [ ] Add filtering wildcards to make adding files easier. Ex ```pyver -f *.docx``` will keep only files with the extension ```docx```

## Why pyver?  
The movtiation behind this attempt at creating a version control method is to create a very, very simple way to track the history of files. The work-flow of pyver is something I do anyway when working on something simple that uses binary files, especially ones that are linked through the software that is required to read them (eg CAD designs). I will create multiple directories, eg v1, v2 and copy the entire contents of my in-progress files in it that I want to preserve the history.

There are a couple of other excellent options, but have a steep learning curve. Also, most version control systems are designed for code or text files, not large binanry files, like word documents or cad files. If you need more functionality, I'd recommend checking out these programs in order os simplicity. [boar VCS](https://bitbucket.org/mats_ekberg/boar/wiki/Home), [mercurial SCM](https://www.mercurial-scm.org/), [git](https://git-scm.com/) with the [large file extension](https://git-lfs.github.com/)

## The basic operation of this program goes like this
1) create some files  
2) run pyver and make a snapshot of your files  
3) make as many revisions as you want  
4) if you want to revert back to an older revision, grab files our of the dated .pyver directories and put them in your current directory  

### Criteria for design
* Simplicity is your friend, obscurity is your enemy
* It is unacceptable to rename files to track versions. This accomplishes this by putting the files in different directories and keep your current file with the desired, persistent filename
* Can be used over a network drive. Does not require a central server. 
* Be OS agnostic (written in Python)
* know when the changes were made, with a comment and who did it

# Tutorial
To get started, lets do a quick demo in windows. Brace yourself, you are going to have to use the command line. In your current directory with the pyver.py file, open a command line with ```shift+right_click``` and select ```Open command window here```. Or Type ```alt+D``` and type ```powershell``` or ```cmd```.
Now type 
```
python pyver.py
```

Done. Microphone flip and you walk off the stage. We have created a pyver repository and made a backup of all the files in our current directory in an archive naming year-month-day-hour-minute-second. Anytime we need to make another backup, just repeat the last step.

OK, lets add a bit more work upfront to save us some typing for years to come. I would recommend having a windows folder that is added to the user PATH system variable where you can keep test or production scripts that you want to access from the command line. For example, I have ```C:\Users\Neal\bin``` that is in the system PATH variable which I can dump python scripts with the *.bat file. Now, all we have to type is ```pyver``` to get the same result as ```python pyver.py```

There are a few built in commands to interrogate the repository. The first is log, which shows the contents of a text file that keeps track of the commits that are made
```
pyver log
Neal , 20160125210812 , 7kb ,  , pyver.py|README.md|pyver.bat
Neal , 20160125210814 , 7kb ,  , pyver.py|README.md|pyver.bat
Neal , 20160125210817 , 7kb ,  , pyver.py|README.md|pyver.bat
Neal , 20160125210854 , 7kb , making a comment for this commit , pyver.py|README.md|pyver.bat
Neal , 20160125210912 , 4kb , only adding one file , pyver.py
```

The next is tree, which shows all the files in the repo.
```
pyver tree

./.pyver 
|  ./20160125210812 
|   |     pyver.py  
|   |     README.md  
|   |     pyver.bat  
|     pyver.log  
|  ./20160125210814 
|   |     pyver.py  
|   |     README.md  
|   |     pyver.bat  
|  ./20160125210817 
|   |     pyver.py  
|   |     README.md  
|   |     pyver.bat  
|  ./20160125210854 
|   |     pyver.py  
|   |     README.md  
|   |     pyver.bat  
|  ./20160125210912 
|   |     pyver.py  
  pyver.py  
  README.md  
  pyver.bat  
```


We also have some flags we can use to customize our commits. This commit adds only the files file1.txt and file2.docx and adds a comment. Note-none of the flag inputs can have spaces, so files are seperated by ```|``` and comments are written without spaces using ```-```

```
pyver -f "file1.txt|file2.docx" -c "making a comment for this commit"
```

We can also use wildcards to add groups of files rather than listing each individual file. 
```
pyver -f "*.txt|*.docx" -c "I added all the txt and docx files to my archive"
```

Also, pyver will skip all files and directories that start with . and ~. These files are typically temporary, backup, or configuration files.

I used pyinstaller to build my own windows executable
```
pyinstaller pyver.py --onefile
```

There you have it. The worlds easiest version control system that multiple users can use over a network, retrieving your old files is trivial, and now you don't have to change your file names to all the silly things people come up with.
