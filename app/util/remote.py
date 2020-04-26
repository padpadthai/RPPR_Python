import logging
from io import BytesIO
from pathlib import Path
from typing import List
from zipfile import ZipFile, BadZipFile

from requests import get, Response, RequestException


def extract_remote_zip(url: str, output_directory, ssl_verify=True) -> List[str]:
    zip_response = get_remote_zip(url, output_directory, ssl_verify)
    zip_response.extractall(path=output_directory)
    logging.debug("Extracted files '{}' to '{}'".format(zip_response.namelist(), output_directory))
    return list(map(lambda zip_item: "{}/{}".format(output_directory, zip_item), zip_response.namelist()))


def get_remote_zip(url: str, output_directory, ssl_verify=True):
    logging.debug("Downloading zip file from '{}' to '{}'".format(url, output_directory))
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    get_request = get_remote_resource(url, ssl_verify)
    try:
        zip_response = ZipFile(BytesIO(get_request.content))
    except BadZipFile:
        logging.error("Unable to process resource from '{}' as a zip file".format(url))
        raise
    logging.debug("Downloaded zip file from '{}' to '{}'".format(url, output_directory))
    return zip_response


def get_remote_resource(url: str, ssl_verify=True) -> Response:
    if not ssl_verify:
        logging.debug("Request is not verify SSL certificate")
    try:
        request = get(url, verify=ssl_verify)
    except RequestException:
        logging.error("There was a problem retrieving the resource at url '{}'".format(url))
        raise
    logging.debug("Retrieved resource at '{};".format(url))
    return request
