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
"""Test MLRunHooks."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from kedro.io import DataCatalog

from kedro_mlrun.dataset import MLRunDataset
from kedro_mlrun.hooks import MLRunModelHooks


class TestMLRunHooks:
    def test_get_model_classes(self) -> None:
        """Model types in the catalog can be identified."""
        mymodule = MagicMock()
        mymodule.ModelType = model_type = type("ModelType", (), {})
        mymodule.NonModelType = type("NonModelType", (), {})
        with patch.dict("sys.modules", mymodule=mymodule), patch(
            "kedro_mlrun.hooks.is_model_dataset_type",
            side_effect=lambda x: x is model_type,
        ):
            cat = DataCatalog(
                data_sets={
                    "model_ds": MLRunDataset(
                        artifact_id="model", data_type="mymodule.ModelType"
                    ),
                    "non-model-ds": MLRunDataset(
                        artifact_id="nonmodel", data_type="mymodule.NonModelType"
                    ),
                }
            )
            assert MLRunModelHooks()._get_model_classes(cat) == {  # noqa: SLF001
                model_type
            }
