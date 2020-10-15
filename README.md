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


For example, if you wanted to generate all the files in the directory `/User/Alice/Data/Experiment42/` for any that are not already created/up to date you would run:

`python3 generate-viz-images.py /User/Alice/Data/Experiment42/`

## Get changes to code made by others:

`cd` into `cell-growth-util` folder made above.
`git pull`
