# Scheduling Aircraft Landings


## Getting Started

These instructions will help you set up and run your Python project for Linux OS.  
To use a python virtual environment on Windows OS, take a look at the [virtualenv official documentation](https://docs.python.org/3/library/venv.html).

### Prerequisites

Make sure you have the following installed on your machine:

- [Python](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)

### Set up a virtual environment for the project
Create a new virtual environment is optional, but recommended. If you do not want to do it, just install the requirements and run python as usual.  

Create a virtual environment for the project within the project working directory:

```
python -m venv venv
```

Activate the environment created before:

```
source venv/bin/activate
```

### Install python requirements

```
pip install -r requirements.txt
```

### Run the project

```
./venv/bin/python main.py
```
