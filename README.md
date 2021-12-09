## Download (once):

`git clone https://github.com/visdesignlab/cell-growth-util`


## Create [virtual environment](https://docs.python.org/3/tutorial/venv.html) (once):

`cd cell-growth-util`

`python3 -m venv .venv`

## Activate virual environment (each time you open a new console):

Windows: `.venv\Scripts\activate.bat`

Mac: `source .venv/bin/activate`

## Install dependencies (once):

`python3 -m pip install -r requirements.txt`

## Run:

`python3 generate-viz-images <folder> [-f | -force] [-q | -quiet]`

| Argument        | Description           |
|---|---|
| `folder` | Required. The root folder. Everything below this will be checked and generated. |
| `-f` or `-force`      | Optional. Adding this argument will cause the script to skip checking the modified timestamp and generate all files.      | 
| `-q` or `-quiet` | Optional. Setting this flag will reduce the amount of statements printed to the command line.      |
| `-delete` | Optional. Setting this flag will cause all `data*.mat` files to be deleted as soon as this script is done using them. To reduce risk of accidents `-d` is NOT supported. In addition, when files are deleted, the following message is printed `🗑 ❌❌❌ DELETING FILE ❌❌❌🗑 : (folder_path/data*.mat)`      |

### Single Experiment:

For example, if you wanted to generate all the files in the directory `/User/Alice/Data/Experiment42/` for any that are not already created/up to date you would run:

`python3 generate-viz-images.py /User/Alice/Data/Experiment42/`

### Multiple Experiments:

You can also generate files for multiple experiments. For instance, if you have three experiments `/User/Alice/Data/Experiment1/`, `/User/Alice/Data/Experiment2/`, `/User/Alice/Data/Experiment3/` you could run:

`python3 generate-viz-images.py /User/Alice/Data/`

In general, the best folder choice is the _deepest_ folder that still includes all the experiments you want to generate. This is especially imporant if you use the `-delete` flag. **If you set the folder too high you risk deleting `data*.mat` files you may not have intended to.**

## Get changes to code made by others:

`cd` into `cell-growth-util` folder made above.

`git pull`
