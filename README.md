# daschland-scripts

This repository contains all data for the creation of the example project Alice in DaSCHland.
To upload the project, please follow the instructions in the upload protocol down below.

## Local Setup

Before cloning the repo, you need to install [Git LFS](https://git-lfs.com/).
This is because this repo contains files that are too big to be stored regularly in Git.

```bash
brew install git-lfs
git lfs install
```

We use [uv](https://docs.astral.sh/uv/) to set up Python and the virtual environment.
Install uv with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once you have cloned this repo, `cd` into it, and then get started with:

```bash
uv sync
source .venv/bin/activate
pre-commit install
```

This will select an appropriate Python interpreter
(or install it, if no suitable installation can be found).
Then it will create a virtual environment, and install the dependencies.

To execute the scripts, you'll also need [ExifTool](https://exiftool.org/):

```bash
brew install exiftool
```

If you want to use the handy `just` commands, you need to install it with

```bash
brew install just
```

Type `just` to get an overview of available recipes.

The JSON project definition defines user accounts which are created by `dsp-tools create`.
In order to keep their passwords secret, the JSON of this repo doesn't specify the passwords in the JSON.
Instead, you must set an environment variable in a `.env` file in your root directory.
This will become the password for all user accounts in the JSON file.
Before creating the project locally or on a DSP server, execute this in your terminal:

```bash
echo DSP_USER_PASSWORD="$(openssl rand -base64 32)" >> .env
```

(The `openssl rand` command generates a random character sequence. Every time you call it, its output is different.)


## Project Structure

- `data` The folder containing the project data.
  - `daschland_ontology` The ontology folder containing the Excel files used to create the JSON ontology file.
  - `multimedia` The folder containing the multimedia data (video, audio, ...) for the project, in subfolders according to the project classes.
  - `output`:
    - `daschland.json` The JSON file containing the data model for the project.
    - `data_daschland.xml` The XML file containing the data for the project.
  - `processed` The folder containing all data to import the project.
  - `raw` The folder containing the raw data files of the project. Each resource class has a separate spreadsheet file.
- `documentation`
- `src` The folder containing the Python scripts for the project.
  - `helpers` The helper scripts containing custom functions.
  - `process_data` The scripts to process the files used for the import.
  - `xmllib` The scripts to convert the XML data to JSON, using the library "dsp-tools xmllib".
- `test`: Unit tests and e2e tests
- `CLAUDE.md`: Instructions for Claude Code
- `justfile`: Shorthand commands
- `pyproject.toml` The Python project file containing all dependencies for the project.
- `uv.lock` The lock file for the project, which is used to create a virtual environment for the project.


## Create the Project JSON File

We use the `dsp-tools excel2json` command to generate the JSON file with the project definition.
If you want to update it, edit the Excel files in `daschland_ontology`.

After that, create the project JSON again with `just daschland-excel2json`.


## Create the Import XML File

The XML file used for the xmlupload can be generated with `just daschland-xmllib`
or run the python file `src/xmllib/main.py` directly.

Some log statements and infos will be printed to the console.
They are informational, and can be ignored.


## Upload Protocol

To upload data to a DSP-API server, use the [`dsp-tools`](https://pypi.org/project/dsp-tools/) command line tool.
It is installed in the virtual environment.
Please use the project admin account "CheshireCat" to upload data to the DSP-API server.

Uploading data locally:

```bash
dsp-tools create daschland.json
dsp-tools xmlupload data_daschland.xml
```

Uploading data to a test server:

```bash
dsp-tools create -s https://api.rdu-08.dasch.swiss -u root@example.com -p 'predefined_root_password' daschland.json
dsp-tools xmlupload -s https://api.rdu-08.dasch.swiss -u cheshire.cat@dasch.swiss -p 'some_random_password' data_daschland.xml
```
