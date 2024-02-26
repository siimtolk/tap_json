"""CSV tap class."""

from __future__ import annotations

import json
import os
from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th  # JSON schema typing helpers
from singer_sdk.helpers._classproperty import classproperty
from singer_sdk.helpers.capabilities import TapCapabilities

from tap_json.client import JSONStream


class TapJSON(Tap):
    """JSON tap class."""

    name = "tap-json"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "files",
            th.ArrayType(
                th.ObjectType(
                    th.Property("entity", th.StringType, required=True),
                    th.Property("path", th.StringType, required=True),
                    th.Property("payload_field_name", th.StringType, required=False, default="payload"),
                    th.Property("extract_fields", th.ArrayType(th.StringType), required=False, default=[]),
                    th.Property(
                        "encoding", th.StringType, required=False, default="utf-8"
                    ),
                )
            ),
            description="An array of json file stream settings.",
        ),
        th.Property(
            "json_files_definition",
            th.StringType,
            description="A path to the JSON file holding an array of input JSON file settings.",
        ),
        th.Property(
            "add_metadata_columns",
            th.BooleanType,
            required=False,
            default=False,
            description=(
                "When True, add the metadata columns (`_sdc_source_file`, "
                "`_sdc_source_file_mtime`, `_sdc_source_lineno`) to output."
            ),
        ),
    ).to_dict()

    @classproperty
    def capabilities(self) -> list[TapCapabilities]:
        """Get tap capabilites."""
        return [
            TapCapabilities.CATALOG,
            TapCapabilities.DISCOVER,
        ]

    def get_file_configs(self) -> list[dict]:
        """Return a list of file configs.

        Either directly from the config.json or in an external file
        defined by json_files_definition.
        """
        json_files = self.config.get("files")
        json_files_definition = self.config.get("json_files_definition")
        if json_files_definition:
            if os.path.isfile(json_files_definition):
                with open(json_files_definition) as f:
                    json_files = json.load(f)
            else:
                self.logger.error(f"tap-json: '{json_files_definition}' file not found")
                exit(1)
        if not json_files:
            self.logger.error("No JSON file definitions found.")
            exit(1)
        return json_files

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [
            JSONStream(
                tap=self,
                name=file_config.get("entity"),
                file_config=file_config,
            )
            for file_config in self.get_file_configs()
        ]


if __name__ == "__main__":
    TapJSON.cli()
