# obs-pi-tally

Simple tally lights for OBS Studio using Python 3.7+

## Getting started

```zsh
# After cloning the repo, cd to the folder:
cd obs-pi-tally

cp config-sample.json config.json  # Copy the sample config file
vi config.json                     # Customize the file

python3 -m venv env      # Create a new virtual env
source env/bin/activate  # activate it

pip install -r requirements.txt  # install the required packages

python3 obs-pi-tally.py -c config.json
```
