"""Custom client handling, including CSVStream base class."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Iterable, List, Dict

from singer_sdk import typing as th
from singer_sdk.streams import Stream

SDC_SOURCE_FILE_COLUMN = "_sdc_source_file"
SDC_SOURCE_LINENO_COLUMN = "_sdc_source_lineno"
SDC_SOURCE_FILE_MTIME_COLUMN = "_sdc_source_file_mtime"


class JSONStream(Stream):
    """Stream class for JSON streams."""

    file_paths: list[str] = []  # noqa: RUF012
    header: list[str] = []  # noqa: RUF012

    def __init__(self, *args, **kwargs):
        """Init JSON Stream."""
        # cache file_config so we dont need to go iterating the config list again later
        self.file_config = kwargs.pop("file_config")
        super().__init__(*args, **kwargs)

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        for file_path in self.get_file_paths():
            file_last_modified = datetime.fromtimestamp(
                os.path.getmtime(file_path), timezone.utc
            )

            file_lineno = -1

            for row in self.get_rows(file_path):
                file_lineno += 1

                
                row_table = []
                if len(self.extract_fields_list)>0:
                    for fn in self.extract_fields_list:
                        row_table.append(row.get(fn, th.StringType))

                
                row_table.append(f"{row}")

                if self.config.get("add_metadata_columns", False):
                    row = [file_path, file_last_modified, file_lineno, *row_table]

                yield dict(zip(self.header, row))

    def _get_recursive_file_paths(self, file_path: str) -> list:
        file_paths = []

        for dirpath, _, filenames in os.walk(file_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if self.is_valid_filename(file_path):
                    file_paths.append(file_path)

        return file_paths

    def get_file_paths(self) -> list:
        """Return a list of file paths to read.

        This tap accepts file names and directories so it will detect
        directories and iterate files inside.
        """
        # Cache file paths so we dont have to iterate multiple times
        if self.file_paths:
            return self.file_paths

        file_path = self.file_config["path"]
        if not os.path.exists(file_path):
            raise Exception(f"File path does not exist {file_path}")

        file_paths = []
        if os.path.isdir(file_path):
            clean_file_path = os.path.normpath(file_path) + os.sep
            file_paths = self._get_recursive_file_paths(clean_file_path)
        elif self.is_valid_filename(file_path):
            file_paths.append(file_path)

        if not file_paths:
            raise RuntimeError(
                f"Stream '{self.name}' has no acceptable files. \
                    See warning for more detail."
            )
        self.file_paths = file_paths
        return file_paths

    def is_valid_filename(self, file_path: str) -> bool:
        """Return a boolean of whether the file includes JSON extension."""
        is_valid = True
        if file_path[-5:] != ".json":
            is_valid = False
            self.logger.warning(f"Skipping non-JSON file '{file_path}'")
            self.logger.warning(
                "Please provide a JSON file that ends with '.json'; e.g. 'users.json'"
            )
        return is_valid

    def get_rows(self, file_path: str) -> List[Dict]:
        """Return a list of dictionaries, made from the JSON objects in a particular JSON file."""
        encoding = self.file_config.get("encoding", "utf-8")  # Default to utf-8 if not specified
        with open(file_path, encoding=encoding) as f:
            data = json.load(f)
        
        # Ensure 'data' is always a list of dictionaries
        if isinstance(data, dict):
            data = [data]
        
         # Yield each json object one at a time
        for item in data:
            yield item


    @property
    def schema(self) -> dict:
        """Define the schema how the json file information is stored.
        Default columns: json_file_path, extract_fields(predefined in conf, like timestamp, uid, etc), payload
        """
        properties: list[th.Property] = []
        header = []
        self.extract_fields_list = self.file_config.get("extract_fields", [])
        header+=self.extract_fields_list
        header.append(self.file_config.get("payload_field_name", "payload"))

        properties.extend(th.Property(column, th.StringType()) for column in header)
        # If enabled, add file's metadata to output
        if self.config.get("add_metadata_columns", False):
            header = [
                SDC_SOURCE_FILE_COLUMN,
                SDC_SOURCE_FILE_MTIME_COLUMN,
                SDC_SOURCE_LINENO_COLUMN,
                *header,
            ]

            properties.extend(
                (
                    th.Property(SDC_SOURCE_FILE_COLUMN, th.StringType),
                    th.Property(SDC_SOURCE_FILE_MTIME_COLUMN, th.DateTimeType),
                    th.Property(SDC_SOURCE_LINENO_COLUMN, th.IntegerType),
                )
            )
        
        # Cache header for future use
        self.header = header
        return th.PropertiesList(*properties).to_dict()

