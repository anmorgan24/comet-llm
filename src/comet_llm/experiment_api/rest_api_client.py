# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at https://www.comet.com
#  Copyright (C) 2015-2023 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import functools
import sys
import urllib.parse
from typing import IO, Optional

import requests  # type: ignore

from .. import config
from ..types import JSONEncodable
from . import request_exception_wrapper

ResponseContent = JSONEncodable


class RestApiClient:
    def __init__(self, api_key: str, comet_url: str):
        self._headers = {"Authorization": api_key}
        self._comet_url = comet_url

    def create_experiment(
        self, workspace: Optional[str], project: Optional[str]
    ) -> ResponseContent:
        return self._request(
            "POST",  "/api/rest/v2/write/experiment/create",
            json={
                "workspaceName": workspace,
                "projectName": project,
            },
        )

    def log_experiment_parameter(
        self, experiment_key: str, name: str, value: JSONEncodable
    ) -> ResponseContent:
        return self._request(
            "POST",  "/api/rest/v2/write/experiment/parameter",
            json={
                "experimentKey": experiment_key,
                "parameterName": name,
                "parameterValue": value,
            },
        )

    
    def log_experiment_asset_with_io(
        self, experiment_key: str, name: str, file: IO
    ) -> ResponseContent:
        return self._request(
            "POST", "/api/rest/v2/write/experiment/upload-asset",
            params={
                "experimentKey": experiment_key,
                "fileName": name,
            },
            files={"file": file}
        )
    
    @request_exception_wrapper.wrap
    def _request(self, method, path, *args, **kwargs):
        url = urllib.parse.urljoin(self._comet_url, path)
        response = requests.request(method, url, headers=self._headers, *args, **kwargs)
        response.raise_for_status()
        return response.json()


@functools.lru_cache(maxsize=0 if "pytest" in sys.modules else 1)
def get(api_key: str) -> RestApiClient:
    comet_url = config.comet_url()
    rest_api_client = RestApiClient(api_key, comet_url)

    return rest_api_client
