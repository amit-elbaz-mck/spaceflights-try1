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
from typing import TYPE_CHECKING

import mlrun
from kfp import dsl

if TYPE_CHECKING:
    from mlrun.projects import MlrunProject


@dsl.pipeline(name="__default__")
def kfpipeline() -> None:
    project: MlrunProject = mlrun.get_current_project()

    preprocess_companies_node = project.run_function(
        function="kedro_handler",
        handler="kedro_cli",
        name="preprocess-companies-node",
        params={"args": ["run", "-e", "local_mlrun", *['-n', 'preprocess_companies_node']]},
        verbose=True,
        auto_build=True,
    ).after()

    preprocess_shuttles_node = project.run_function(
        function="kedro_handler",
        handler="kedro_cli",
        name="preprocess-shuttles-node",
        params={"args": ["run", "-e", "local_mlrun", *['-n', 'preprocess_shuttles_node']]},
        verbose=True,
        auto_build=True,
    ).after()

    create_model_input_table_node = project.run_function(
        function="kedro_handler",
        handler="kedro_cli",
        name="create-model-input-table-node",
        params={"args": ["run", "-e", "local_mlrun", *['-n', 'create_model_input_table_node']]},
        verbose=True,
        auto_build=True,
    ).after(preprocess_shuttles_node, preprocess_companies_node)

    split_data_node = project.run_function(
        function="kedro_handler",
        handler="kedro_cli",
        name="split-data-node",
        params={"args": ["run", "-e", "local_mlrun", *['-n', 'split_data_node']]},
        verbose=True,
        auto_build=True,
    ).after(create_model_input_table_node)

    train_model_node = project.run_function(
        function="kedro_handler",
        handler="kedro_cli",
        name="train-model-node",
        params={"args": ["run", "-e", "local_mlrun", *['-n', 'train_model_node']]},
        verbose=True,
        auto_build=True,
    ).after(split_data_node)

    evaluate_model_node = project.run_function(
        function="kedro_handler",
        handler="kedro_cli",
        name="evaluate-model-node",
        params={"args": ["run", "-e", "local_mlrun", *['-n', 'evaluate_model_node']]},
        verbose=True,
        auto_build=True,
    ).after(split_data_node, train_model_node)
