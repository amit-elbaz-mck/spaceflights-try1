# (c) McKinsey & Company 2016 – Present
# All rights reserved
#
#
# This material is intended solely for your internal use and may not be reproduced,
# disclosed or distributed without McKinsey & Company's express prior written consent.
# Except as otherwise stated, the Deliverables are provided ‘as is’, without any express
# or implied warranty, and McKinsey shall not be obligated to maintain, support, host,
# update, or correct the Deliverables. Client guarantees that McKinsey’s use of
# information provided by Client as authorised herein will not violate any law
# or contractual right of a third party. Client is responsible for the operation
# and security of its operating environment. Client is responsible for performing final
# testing (including security testing and assessment) of the code, model validation,
# and final implementation of any model in a production environment. McKinsey is not
# liable for modifications made to Deliverables by anyone other than McKinsey
# personnel, (ii) for use of any Deliverables in a live production environment or
# (iii) for use of the Deliverables by third parties; or
# (iv) the use of the Deliverables for a purpose other than the intended use
# case covered by the agreement with the Client.
# Client warrants that it will not use the Deliverables in a "closed-loop" system,
# including where no Client employee or agent is materially involved in implementing
# the Deliverables and/or insights derived from the Deliverables.
"""Test MLRunDatasets."""
from unittest.mock import patch

from kedro_mlrun.dataset import MLRunDataset, MLRunModelDataset


class TestMLRunDataset:
    def test_logging_kwargs_used(self) -> None:
        """User-defined logging kwargs are used when logging artifacts."""
        logging_kwargs = {"foo": "bar", "spam": "ham"}
        ds = MLRunDataset(artifact_id="id", logging_kwargs=logging_kwargs)
        with patch("kedro_mlrun.dataset.log_object_with_packagers") as mock:
            ds.save("my_data")
            assert mock.called
            for k, v in logging_kwargs.items():
                assert mock.call_args.kwargs["logging_kwargs"][k] == v

    def test_logging_dbkey_set(self) -> None:
        """db_key is set to be the same as the artifact_id."""
        arti_id = "my_id_123"
        ds = MLRunDataset(artifact_id=arti_id)
        with patch("kedro_mlrun.dataset.log_object_with_packagers") as mock:
            ds.save("my_data")
            assert mock.called
            assert mock.call_args.kwargs["logging_kwargs"]["db_key"] == arti_id


class TestMLRunModelDataset:
    def test_model_is_applied(self) -> None:
        """Model is mlrun_applied after loading automatically."""
        ds = MLRunModelDataset(artifact_id="my-arti-123")
        with patch("kedro_mlrun.dataset.get_current_project"), patch(
            "kedro_mlrun.dataset.MLRunModelDataset._read_model_artifact"
        ) as model_mock, patch("kedro_mlrun.dataset.apply_mlrun") as apply_mock:
            ds.load()
            assert apply_mock.called
            assert apply_mock.call_args.args == (model_mock(),)
