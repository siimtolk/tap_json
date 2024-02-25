# tap-json

`tap-json` is a Singer tap for json files.

It can
* read json objects and store them as strings under a predefined field name.
* handles single jason and array of jsons
* extract specified fields if they exist in json as strings and store in separate fields
* directory of file definitions can be written in a single json input file or defiuned in meltano.yml
* data is always appended, as this is intended for a raw input for further processing and merging into a structured layers

This 'tap-json' is based on 'tap-csv' (git+https://github.com/MeltanoLabs/tap-csv.git).

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.


## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| json_files_definition| False    | None    | A path to the JSON file holding an array of import json file settings. |
| add_metadata_columns| False    | False   | When True, add the metadata columns (`_sdc_source_file`, `_sdc_source_file_mtime`, `_sdc_source_lineno`) to output. |

A full list of supported settings and capabilities is available by running: `tap-jon --about`

The config `json`, either in meltano.yml or in a separate json file, contains an array called `files` that consists of dictionary objects detailing each destination table to be passed to Singer. Each of those entries contains:
* `entity`: The entity name to be passed to singer (i.e. the table)
* `path`: Local path to the file to be ingested. Note that this may be a directory, in which case all files in that directory and any of its subdirectories will be recursively processed
* `extract_fields`: The names of the columns that will be extracted from the json. Values extracted as strings, null's when missing.
* `encoding`: [Optional] The file encoding to use when reading the file (i.e. "latin1", "UTF-8"). Use this setting when you get a `UnicodeDecodeError` error.


Example:

```json
{
	"files":	[
					{	"entity" : "leads",
						"path" : "/path/to/leads.csv",
						"extract_fields" : ["Id"],
					},
					{	"entity" : "opportunities",
						"path" : "/path/to/opportunities_foler/",
						"extract_fields" : ["Id"],
						"encoding" : "latin1",
					}
				]
}
```

Optionally, the files definition can be provided by an external json file:

**config.json**
```json
{
	"json_files_definition": "files_def.json"
}
```

**files_def.json**
```json
[
	{	"entity" : "leads",
		"path" : "/path/to/leads.csv",
		"extract_fields" : ["Id"]
	},
	{	"entity" : "opportunities",
		"path" : "/path/to/opportunities.csv",
		"extract_fields" : ["Id"]
	}
]
```

## Installation

```bash
pipx install git+https://github.com/MeltanoLabs/tap-csv.git
```

## Usage

You can easily run `tap-json` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-json --version
tap-json --help
tap-json --config CONFIG --discover > ./catalog.json
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-json
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-json --version
# OR run a test `elt` pipeline:
meltano run tap-csv target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
