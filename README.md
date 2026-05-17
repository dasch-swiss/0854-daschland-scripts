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

**Important:** Add these to your `.env` to ensure that the data XML does not contain randomly generated IDs.

```
XMLLIB_SORT_RESOURCES=true
XMLLIB_SORT_PROPERTIES=true
XMLLIB_AUTHORSHIP_ID_WITH_INTEGERS=true
```

## Project Structure

- `data` The folder containing the project data.
    - `daschland_ontology` The ontology folder containing the Excel files used to create the JSON ontology file.
    - `multimedia` The folder containing the multimedia data (video, audio, ...) for the project, in subfolders
      according to the project classes.
    - `output`:
        - `daschland.json` The JSON file containing the data model for the project.
        - `data_daschland.xml` The XML file containing the data for the project.
    - `processed` The folder containing all data to import the project.
    - `raw` The folder containing the raw data files of the project. Each resource class has a separate spreadsheet
      file.
- `documentation`
- `src` The folder containing the Python scripts for the project.
    - `helpers` The helper scripts containing custom functions.
    - `process_data` The scripts to process the files used for the import.
    - `xmllib` The scripts to generate the XML data file from the raw spreadsheets, using the library "dsp-tools
      xmllib".
- `test`: Unit tests and e2e tests
- `CLAUDE.md`: Instructions for Claude Code
- `justfile`: Shorthand commands
- `pyproject.toml` The Python project file containing all dependencies for the project.
- `uv.lock` The lock file for the project, which is used to create a virtual environment for the project.

## Create the Project JSON File

We use the `dsp-tools excel2json` command to generate the JSON file with the project definition.
If you want to update it, edit the Excel files in `data/daschland_ontology`.

After that, create the project JSON again with `just daschland-excel2json`.

## Process Data

Processing data can be executed either in two distinct steps or all at once.
See below for an overview of the separate steps.

To update the data and create the XML run:

```bash
just daschland-xmllib
```

Some log statements and infos will be printed to the console.
They are informational, and can be ignored.

### Update Source Data Only

The `src/process_data` scripts sync multimedia file metadata from `data/multimedia/`
into the raw spreadsheets in `data/raw/`.
Run this whenever any changes have been made, but you do not want to create the import XML yet.

```bash
uv run src/process_data/process_data_main.py
```

### Create the Import XML File

The XML file can be created as a separate step by running this command.

```bash
uv run src/main.py
```

## Upload Protocol

### Manual Uploads

To upload data to a DSP-API server, use the [`dsp-tools`](https://pypi.org/project/dsp-tools/) command line tool.
It is installed in the virtual environment.

#### Local

```bash
dsp-tools create data/output/daschland.json
dsp-tools xmlupload data/output/data_daschland.xml
```

#### Dev Server

To manually deploy to the dev server, trigger the GitHub Actions workflow `.github/workflows/create-on-dev.yml` from the Actions tab. This workflow runs the same `dsp-tools create` and `dsp-tools xmlupload` commands as local uploads but targets [app.dev.dasch.swiss](https://app.dev.dasch.swiss). Use this to test against a fresh dev environment when needed.

### Automatic Deployments

#### Stage Server

After every deployment to stage, the Alice in DaSCHland project is **automatically recreated and repopulated** on the stage DSP-API server.

**Why?** The Alice project is a comprehensive showcase of DSP features and frequently changes. Testers are accustomed to modifying data on stage freely, assuming it will be reset regularly. To maintain consistency and ensure testers always have a fresh, predictable dataset, the project is automatically recreated after each stage deployment.

**How it works:**
1. After a successful stage deployment, the ops-deploy Jenkins job triggers the GitHub Actions workflow
2. The workflow (`.github/workflows/create-on-stage.yml`) runs two commands:
   - `dsp-tools create` — creates the project schema on `api.stage.dasch.swiss`
   - `dsp-tools xmlupload` — populates the project with data from the latest XML

**Monitoring:** You can view the workflow execution results in the GitHub Actions tab, or check the deploy logs at [deploy.ops.dasch.swiss](https://deploy.ops.dasch.swiss/job/ops_deploy/job/dsp_stage_01_daschland/)

**User accounts used:**
- Project creation: `dasch@dasch.swiss` (admin account)
- Data upload: `cheshire.cat@dasch.swiss` (project account)
