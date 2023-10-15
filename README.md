## 5143 Virtual Filesystem - P02
### Group Members

#### [Angel Badillo](https://github.com/It-Is-Legend27)
#### [Leslie Cook](https://github.com/Leslie-N-Cook)

### Overview:
Create a sqlite database that acts as a virtual file system with files, directories, and metadata for each. 
Run linux shell commands within the sqlite database to navigate the virtual file system.

### Instructions

1. Install the required packages 

   `pip install -r requirements.txt`

2. Execute the file system shell 
    
    `python3 main.py` or `python main.py`

3. Run the commands to navigate the file system
  
    `ls -lah` - list files and directories in current directory
      
    `mkdir bananas` - make directory
  
    `cd bananas` - change directory

    `cd ..` - move back one directory
  
    `pwd` - print working directory

    `mv stuff.txt bananas` - move a file to another directory

    `cp bananas/stuff.txt home/angel/newfile.txt` - copy file from a directoy and rename it in another location
  
    `rm -rf bananas` - remove file or directory

    `chmod 777 home` - change permissions of file or directory using octal notation

    `exit` - exit the shell's virtual file system 

### Virtual File System in SQLite Database
<img src=photos/filesystem.png>

### Walkthrough
<img src=photos/image.png>

### Assignment Requirements 
<img src=photos/image_req.png>