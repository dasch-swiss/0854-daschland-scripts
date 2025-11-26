# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Setup

- `uv sync` - Set up Python environment and install dependencies
- `just` - List all available recipes/commands

### Code Quality and Testing

- `just lint` - Run all linters (ruff, mypy, vulture) at once
- `just format` - Run all auto-formatting tools
- `just test` - Run unit tests with pytest
- `just ruff-check` - Check Python code style
- `just mypy` - Type checking
- `just vulture` - Dead code analysis
- `just clean` - Remove artifact files

### Data Generation

- `uv run src/xmllib/xmllib_main.py` - Generate the main XML file (data_daschland.xml) using xmllib

### DSP-API Upload

Local upload:

```bash
dsp-tools create daschland.json
dsp-tools xmlupload -u cheshire.cat@dasch.swiss -p 'alice9548' data_daschland.xml
```

Test server (rdu-08):

```bash
dsp-tools create -s https://api.rdu-08.dasch.swiss -u root@example.com -p 'xxxx' daschland.json
dsp-tools xmlupload -s https://api.rdu-08.dasch.swiss -u cheshire.cat@dasch.swiss -p 'alice9548' data_daschland.xml
```

## DSP-TOOLS Overview

DSP-TOOLS is the command-line interface for the DaSCH Service Platform.
This project heavily relies on DSP-TOOLS for data model creation and upload workflows.

### Key DSP-TOOLS Commands Used

1. **Create JSON project definition**: `dsp-tools excel2json` converts Excel files into a JSON file.
  This is a pure restructuring, the information stays the same.
2. **Data Model Creation**: `dsp-tools create` establishes the data model from the JSON file on the DSP server.
3. **Validation**: `dsp-tools validate-data` validates the XML data against the data model on the server.
4. **Data Upload**: `dsp-tools xmlupload` populates the project with resources and metadata defined in the XML file.

### Important DSP-TOOLS Notes

- Creates `id2iri_mapping_[timestamp].json` files during xmlupload, to map IDs of the XML to IRIs on the DSP server
- Supports both local DSP instances and remote servers like <https://app.rdu-08.dasch.swiss/>
- For project creation and data upload, authentication is always required on remote servers
- XML files must conform to the ontology/data model structure defined in the JSON file

## Development Workflow

### Pull Request Reviews

PRs in this repository are typically reviewed by:

- [@Notheturtle](https://github.com/Notheturtle)
- [@jnussbaum](https://github.com/jnussbaum)
- [@Nora-Olivia-Ammann](https://github.com/Nora-Olivia-Ammann)

## Architecture Overview

This is a DaSCH Service Platform (DSP) example project called "Alice in DaSCHland"
that demonstrates data modeling and upload workflows.
The project converts multimedia and metadata about Lewis Carroll's Alice books
into formats suitable for the DSPplatform.

### Core Data Flow

1. **Spreadsheets** (`data/raw/`) contain structured data for different resource types
2. **Conversion path**: `src/xmllib/` uses dsp-tools xmllib for XML generation
3. **Output**: Generated files (JSON + XML) for upload to DSP-API servers
4. **Mirror**: NodeGoat CSV files (`data/processed`) are automatically updated for parallel project

### Key Components

- **Resource Types**: Archive, Audio, AudioSegment, Book, BookChapter, BookCover, BookEdition, Character,
  Documentation, Event, Image, Location, Material, Region, Video, VideoSegment
- **Data Sources**: Excel spreadsheets in `data/raw/`
- **Multimedia Files**: Organized in `data/multimedia/` by type (audio, image, video, etc.)
- **Ontology**: Defined in `data/daschland_ontology/` Excel files, compiled to `data/output/daschland.json`

### Important Notes

- Requires Git LFS for large multimedia files
- Uses uv for Python environment management
- ExifTool required for metadata extraction
- NodeGoat files are automatically updated when running main XML generation
