import pytest
from testix import *

from comet_llm.experiment_api import experiment_api


@pytest.fixture(autouse=True)
def mock_imports(patch_module):
    patch_module(experiment_api, "comet_api_client")
    patch_module(experiment_api, "config")


def _construct(experiment_key):
    with Scenario() as s:
        s.comet_api_client.get("api-key") >> Fake("client_instance")
        s.client_instance.create_experiment(
            "LLM",
            "the-workspace",
            "project-name",
        ) >> {"experimentKey": experiment_key, "workspaceName": "the-workspace", "projectName": "project-name"}
        s.config.comet_url() >> "https://comet.com/clientlib"

        tested = experiment_api.ExperimentAPI.create_new(
            api_key="api-key",
            workspace="the-workspace",
            project_name="project-name",
        )
        assert tested.project_url == "https://comet.com/the-workspace/project-name"

    return tested


def test_log_asset():
    tested = _construct("experiment-key")

    with Scenario() as s:
        s.client_instance.log_experiment_asset_with_io(
            "experiment-key",
            name="the-name",
            file="the-io",
            asset_type="asset-type",
        )
        tested.log_asset_with_io(
            name="the-name",
            file="the-io",
            asset_type="asset-type",
        )


def test_log_parameter():
    tested = _construct("experiment-key")

    with Scenario() as s:
        s.client_instance.log_experiment_parameter(
            "experiment-key",
            name="parameter-name",
            value="parameter-value",
        )
        tested.log_parameter(
            name="parameter-name",
            value="parameter-value",
        )


def test_log_metric():
    tested = _construct("experiment-key")

    with Scenario() as s:
        s.client_instance.log_experiment_metric(
            "experiment-key",
            name="metric-name",
            value="metric-value",
        )
        tested.log_metric(
            name="metric-name",
            value="metric-value",
        )


def test_log_tags():
    tested = _construct("experiment-key")

    with Scenario() as s:
        s.client_instance.log_experiment_tags(
            "experiment-key",
            tags="the-tags",
        )
        tested.log_tags("the-tags")


def test_log_other():
    tested = _construct("experiment-key")

    with Scenario() as s:
        s.client_instance.log_experiment_other(
            "experiment-key",
            name="the-name",
            value="the-value"
        )
        tested.log_other("the-name", "the-value")


def test_from_existing_id__happyflow():
    with Scenario() as s:
        s.comet_api_client.get("api-key") >> Fake("client_instance")
        s.client_instance.get_experiment_metadata("example-id") >> {
            "workspaceName": "the-workspace",
            "projectName": "project-name"
        }
        s.config.comet_url() >> "https://comet.com/clientlib"

        tested = experiment_api.ExperimentAPI.from_existing_id(
            id="example-id",
            api_key="api-key",
        )

        assert tested.project_url == "https://comet.com/the-workspace/project-name"
        assert tested.workspace == "the-workspace"
        assert tested.project_name == "project-name"


def test_from_existing_id__initialize_parameters_false__parameters_not_intialized():
    with Scenario() as s:
        s.comet_api_client.get("api-key") >> Fake("client_instance")

        tested = experiment_api.ExperimentAPI.from_existing_id(
            id="example-id",
            api_key="api-key",
            load_metadata=False
        )

        assert tested.workspace is None
        assert tested.project_name is None