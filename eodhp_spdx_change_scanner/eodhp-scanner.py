from __future__ import annotations

import logging
import os
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING

import boto3
import botocore.exceptions

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3ServiceResource

logger = logging.getLogger(__name__)


def update_file(
    local_path: str,
    s3_path: str,
    s3_bucket_name: str,
    s3: S3ServiceResource,
) -> None:
    """Updates file in S3 from local directory"""
    logging.info(f"Updating {local_path} into {s3_bucket_name} {s3_path}")

    # Determine content type based on file extension
    if local_path.endswith(".html"):
        content_type = "text/html"
    elif local_path.endswith(".txt"):
        content_type = "text/plain"
    else:
        content_type = "binary/octet-stream"  # Default for other file types

    s3.Bucket(s3_bucket_name).upload_file(local_path, s3_path, ExtraArgs={"ContentType": content_type})


def delete_file(path: str, bucket_name: str, s3: S3ServiceResource) -> None:
    """Deletes any files no longer present"""
    logging.info(f"Deleting {path}")

    s3.Object(bucket_name, path).delete()


class Scanner:
    def __init__(self, **kwargs: dict) -> None:
        # S3 Client
        self.s3: S3ServiceResource | None = None

        self.initialise_s3()
        args = kwargs["kwargs"]
        if "s3_bucket" in args:
            self.s3_bucket_name: str = args["s3_bucket"]
        else:
            bucket = os.getenv("S3_BUCKET")
            if bucket is None:
                raise KeyError("S3_BUCKET not set")
            self.s3_bucket_name = bucket
        self.local_folder: str = args["dest"]
        self.repo_name = urllib.parse.urlparse(args["repourl"]).path.strip("/")
        self.s3_prefix = "/".join([os.getenv("SPDX_LICENCE_PATH", "api/catalogue/stac/licences/spdx")])

    def initialise_s3(self) -> None:
        if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            session = boto3.session.Session(
                aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            )
            self.s3 = session.resource("s3")
        else:
            self.s3 = boto3.resource("s3")

    def finish(self) -> None:
        logging.info("Finishing up")

    def scan_file(self, file_name: Path, data: object = None) -> None:
        file_name_str = str(file_name)
        local_path = f"{self.local_folder}/github.com/{self.repo_name}/{file_name_str}"
        s3_path = f"{self.s3_prefix}/{file_name_str}"

        if file_name_str.endswith(".html") or file_name_str.endswith(".txt"):
            if os.path.exists(local_path):
                try:  # s3 file exists and is updated
                    assert self.s3 is not None
                    self.s3.Object(self.s3_bucket_name, s3_path).load()
                    update_file(local_path, s3_path, self.s3_bucket_name, self.s3)
                    logging.info(f"File {file_name_str} updated")
                except botocore.exceptions.ClientError:  # s3 file doesn't exist and is added
                    assert self.s3 is not None
                    update_file(local_path, s3_path, self.s3_bucket_name, self.s3)
                    logging.info(f"File {file_name_str} added")
            else:  # s3 file is deleted
                assert self.s3 is not None
                delete_file(s3_path, self.s3_bucket_name, self.s3)
                logging.info(f"File {file_name_str} deleted")
