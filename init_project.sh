#!/usr/bin/env bash
set -euxo pipefail

source ./mlrun.env

# switch to working directory
# cd "${WD}"

# set up connection to McKinsey pypi
python -m pip config set global.index-url "https://${ESCAPED_EMAIL}:${JFROG_TOKEN}@mckinsey.jfrog.io/artifactory/api/pypi/python/simple"

#create conda env
# conda create -n "${CONDA_ENV_NAME}" python=3.9 -y

# evaluate conda hook so that conda activate works when the file is run as a script
eval "$(conda shell.bash hook)"
conda activate "${CONDA_ENV_NAME}"

#pip install kedro -U

if [[ -d "./spaceflights" ]]; then
	echo "${WD}/spaceflights already exist. Deleting it..."
	rm -rf ./spaceflights
fi


# create kedro project
echo "project_name: ${PROJECT_NAME}" > kedro_conf.yml
kedro new --starter=spaceflights --config=kedro_conf.yml


# switch to new project
cd "${PROJECT_NAME}"

# upgrading the packages help to speed up dependency resolution later on
pip install -U pip setuptools

# install the kedro project dependencies
pip install -r src/requirements.txt


# installing kedro-mlrun separately, in case resolution with reqs.txt not possible
# pip install mck.kedro-mlrun

# switch off/on kedro telemetry to avoid prompt
echo "consent: true" > .telemetry


# If you're a lucky user with a shiny M1/M2 mac you need to run these
# otherwise you're even luckier and can just skip them!
# conda install protobuf -y
# conda install "cryptography~=3.0, <3.4" -y
