import logging
import os
import urllib
from pathlib import Path

import boto3
import botocore

logger = logging.getLogger(__name__)


def update_file(
    local_path: str,
    s3_path: str,
    s3_bucket_name: str,
    s3: boto3.resource,
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

    s3.Bucket(s3_bucket_name).upload_file(
        local_path, s3_path, ExtraArgs={"ContentType": content_type}
    )


def delete_file(path: str, bucket_name: str, s3: boto3.resource) -> None:
    """Deletes any files no longer present"""
    logging.info(f"Deleting {path}")

    s3.Object(bucket_name, path).delete()


class Scanner:
    def __init__(self, **kwargs):
        # S3 Client
        self.s3 = None

        self.initialise_s3()
        args = kwargs["kwargs"]
        if "s3_bucket" in args:
            self.s3_bucket_name = args["s3_bucket"]
        else:
            self.s3_bucket_name = os.getenv("S3_BUCKET")
        if self.s3_bucket_name is None:
            raise KeyError("S3_BUCKET not set")
        self.local_folder = args["dest"]
        self.repo_name = urllib.parse.urlparse(args["repourl"]).path.strip("/")
        self.s3_prefix = "/".join(
            [os.getenv("SPDX_LICENCE_PATH", "api/catalogue/stac/licences/spdx")]
        )

    def initialise_s3(self):
        if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            session = boto3.session.Session(
                aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            )
            self.s3 = session.resource("s3")

        else:
            self.s3 = boto3.resource("s3")

    def finish(self):
        logging.info("Finishing up")

    def scan_file(self, file_name: Path, data=None):
        file_name = str(file_name)
        local_path = f"{self.local_folder}/github.com/{self.repo_name}/{file_name}"
        s3_path = f"{self.s3_prefix}/{file_name}"

        if file_name.endswith(".html") or file_name.endswith(".txt"):
            if os.path.exists(local_path):
                try:  # s3 file exists and is updated
                    self.s3.Object(self.s3_bucket_name, s3_path).load()
                    update_file(local_path, s3_path, self.s3_bucket_name, self.s3)
                    logging.info(f"File {file_name} updated")
                except botocore.exceptions.ClientError:  # s3 file doesn't exist and is added
                    update_file(local_path, s3_path, self.s3_bucket_name, self.s3)
                    logging.info(f"File {file_name} added")
            else:  # s3 file is deleted
                delete_file(s3_path, self.s3_bucket_name, self.s3)
                logging.info(f"File {file_name} deleted")
