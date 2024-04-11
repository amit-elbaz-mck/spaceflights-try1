#!/usr/bin/env bash
set -euxo pipefail

WD=~
ESCAPED_EMAIL=john_doe%40company.com
JFROG_TOKEN=
PROJECT_NAME=spaceflights
REPO_ORIGIN=user@github.com:my-org/my-repo.git
MLRUN_DBPATH="https://mlrun-api-uri.com"
V3IO_USERNAME="john-doe"
V3IO_ACCESS_KEY=""
GIT_TOKEN=
ENV_NAME="demo_env"

# switch to working directory
cd "${WD}"

# set up connection to McKinsey pypi
python -m pip config set global.index-url "https://${ESCAPED_EMAIL}:${JFROG_TOKEN}@mckinsey.jfrog.io/artifactory/api/pypi/python/simple"

# create conda env
conda create -n "${ENV_NAME}" python=3.9 -y
# evaluate conda hook so that conda activate works when the file is run as a script
eval "$(conda shell.bash hook)"
conda activate "${ENV_NAME}"
# upgrading the packages help to speed up dependency resolution later on
pip install -U pip setuptools

#         ,     \    /      ,
#       / \    )\__/(     / \
#      /   \  (_\  /_)   /   \
# ____/_____\__\@  @/___/_____\____
#|             |\../|              |
#|              \VV/               |
#|        WARNING: DRAGONS!!!      |
#|_________________________________|
# |    /\ /      \\       \ /\    |
# |  /   V        ))       V   \  |
# |/     `       //        '     \|
# `              V                '
# install kedro
pip install kedro -U

if [[ -d "./spaceflights" ]]; then
	echo "${WD}/spaceflights already exist. Deleting it..."
	rm -rf ./spaceflights
fi

#
# --------------
# ALL GOOD: RELAX AND CARRY ON!!!
# --------------
#

# create kedro project
echo "project_name: ${PROJECT_NAME}" > kedro_conf.yml
kedro new --starter=spaceflights --config=kedro_conf.yml

# switch to new project
cd "${PROJECT_NAME}"

# install the kedro project dependencies
pip install -r src/requirements.txt

# switch off/on kedro telemetry to avoid prompt
echo "consent: true" > .telemetry

# check it works
kedro run

# initialize git repo
git init
git add .
git commit -am "first commit"
git branch -M main
git remote add origin "${REPO_ORIGIN}"

#         ,     \    /      ,
#       / \    )\__/(     / \
#      /   \  (_\  /_)   /   \
# ____/_____\__\@  @/___/_____\____
#|             |\../|              |
#|              \VV/               |
#|   WARNING: ANOTHER DRAGON!!!    |
#|_________________________________|
# |    /\ /      \\       \ /\    |
# |  /   V        ))       V   \  |
# |/     `       //        '     \|
# `              V                '
git push -u origin main --force

#
# --------------
# MADE IT: RELAX AND CARRY ON!!!
# --------------
#

# install kedro-mlrun
pip install mck.kedro-mlrun

# If you're a lucky user with a shiny M1/M2 mac you need to run these
# otherwise you're even luckier and can just skip them!
conda install protobuf -y
conda install "cryptography~=3.0, <3.4" -y

# copy over the kedro mlrun source code
# ideally the cluster would just have access to this!
# for not though this fudge works just fine
KD_LOCATION=$(pip show mck.kedro-mlrun | grep Location | cut -d ' ' -f2)
cp -R "${KD_LOCATION}/kedro_mlrun" src/

# update remote
git add .
git commit -m "add kedro_mlrun source"
git push

# initialize mlrun stuff - w000000!
kedro mlrun init --pipeline __default__ --env local

# update remote
git add .
git commit -m "init deployment"
git push

# set credentials
cat <<EOT >> .mlrun/mlrun.env
# Github token that has the permission to access the contents of the repo you created
GIT_TOKEN=${GIT_TOKEN}
# URL to the MLRun server / Iguazio cluster
MLRUN_DBPATH=${MLRUN_DBPATH}
# The next two parameters are only needed when connecting to the Iguazio cluster
# They are necessary to write data on the v3io file store
V3IO_USERNAME=${V3IO_USERNAME}
V3IO_ACCESS_KEY=${V3IO_ACCESS_KEY}
EOT

# save project to cluster
kedro mlrun save

# if there are local files used to run demos etc
# log them as artifacts
kedro mlrun log-inputs --pipeline __default__ --env local

# 3, 2, 1, takeoff!
kedro mlrun run
