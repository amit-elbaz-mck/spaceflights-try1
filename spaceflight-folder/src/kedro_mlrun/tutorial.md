# Tutorial: Deploy Your Spaceflights

- [Tutorial: Deploy Your Spaceflights](#tutorial-deploy-your-spaceflights)
  - [0. Prerequisites](#0-prerequisites)
    - [Set up a Kedro Project](#set-up-a-kedro-project)
    - [Push Your Code to Github](#push-your-code-to-github)
  - [1. Install `kedro-mlrun`](#1-install-kedro-mlrun)
  - [2. Initialise Your Deployment](#2-initialise-your-deployment)
  - [3. Set Deployment Configuration](#3-set-deployment-configuration)
  - [4. Save Your Project to Target](#4-save-your-project-to-target)
  - [5. Run](#5-run)
  - [What is next?](#what-is-next)

> \[!NOTE\]
> This tutorial is also available as a single executable script
> [here](../../../examples/deploy_spaceflights.sh).
> Before running the script, remember to fill in the placeholders at the top!

## 0. Prerequisites

### Set up a Kedro Project

Before we dive into deploying a Kedro project using `kedro-mlrun` and MLRun, let's set
up the necessary prerequisites.

Create a new Conda environment and activate it:

```shell
conda create -n "demo_env" python=3.9 -y
conda activate demo_env
```

Install Kedro:

```shell
pip install kedro
```

Create a new Kedro project based on the "[spaceflights]" starter template:

```shell
kedro new --starter=spaceflights
```

Navigate into the newly created project directory and install the project's
dependencies:

```shell
cd spaceflights
pip install -r src/requirements.txt
```

(Optional) If you're curious, you can run the pipeline locally to verify that
everything is set up correctly:

```shell
kedro run
```

### Push Your Code to Github

In order to leverage MLRun's ability to fetch code from a GitHub repository, we need
to push our Kedro project code to a GitHub repository.

You can easily create a new repo in the [Mck-Playground] organization.
After creating your repo, continue as follows:

Initialise a Git repository and commit all the files in your project:

```shell
git init
git add .
git commit -am "first commit"
```

Add the remote origin for your GitHub repository.
Replace `YOUR_REPO_NAME` with the name of your repository in the
[Mck-Playground] organization:

```shell
git branch -M main
# do not forget to replace YOUR_REPO_NAME with your repo name!
git remote add origin org-62409928@github.com:McK-Playground/YOUR_REPO_NAME.git
git push -u origin main
```

Your code is now successfully pushed to your GitHub repository.
Always using the code from this repo, MLRun will keep your deployment up to date.

Next, we will proceed with the installation of `kedro-mlrun` and configuring MLRun for the deployment.

## 1. Install `kedro-mlrun`

Install `kedro-mlrun` from JFrog Artifactory:

```shell
pip install mck.kedro-mlrun
```

(For M1 users) If you are using an Apple M1 chip, you may need to install additional
dependencies:

```shell
conda install protobuf
conda install "cryptography~=3.0, <3.4"
```

Next, we need to make sure that MLRun has access to the `kedro-mlrun` package.
While it is ideal to have the Iguazio cluster set up to fetch packages from JFrog
Artifactory, we will provide the package locally under the `src/` directory for this
tutorial.

To locate where the `kedro-mlrun` package is installed on your local machine, run the
following command:

```shell
pip show mck.kedro-mlrun
```

You will see output similar to the following, with the package location specified under "Location:":

```shell
Name: mck.kedro-mlrun
Version: 0.0.1
Summary: kedro_mlrun
Home-page:
Author: QuantumBlack Labs
Author-email: feedback@quantumblack.com
License:
Location: /Users/your_username/miniconda3/envs/demo_env/lib/python3.9/site-packages
Requires: graphlib-backport, jinja2, kedro, mlrun, plotly, python-dotenv, python-slugify, scikit-learn
Required-by:
```

Once you have located the package's installation directory, copy the package source ...

```shell
cp -R /Users/your_username/miniconda3/envs/demo_env/lib/python3.9/site-packages/kedro_mlrun src/
```

... and push it to your repository:

```shell
git add .
git commit -m "add kedro_mlrun source"
git push
```

With this, the source code of the `kedro-mlrun` package is available in your project
repository, ensuring that MLRun can access them at deployment time.

## 2. Initialise Your Deployment

```bash
kedro mlrun init --pipeline __default__ --env local
```

This command sets up the necessary files and configurations for the selected pipeline
to be deployed.
Upon running this command, you will notice that

- an `.mlrun/` folder is created inside
  your project directory
- an `mlrun_runner.py` script is created at the project root
- a new Kedro environment, `local_mlrun`, is created

`.mlrun/` contains helper scripts generated by `kedro-mlrun`, which will be executed
by the plugin based on subsequent CLI commands you will enter.

It's important to have an understanding of these helper scripts, even though you don't
need to run them manually.
Here's a brief overview:

- `kedro_handler.py`: This module is executed by MLRun when the pipeline starts running
  on the target platform.
  It acts as a bridge to the Kedro CLI, allowing you to specify familiar `kedro run`
  command-line arguments when running your pipeline on the target platform.
- `save.py`: This script is responsible for saving the selected pipeline on the target
  platform.
  The process of saving a pipeline can vary across platforms, but on MLRun, it involves
  configuring an MLRun Function and Workflow within an MLRun project.
- `workflow.py`: This script defines the selected pipeline in terms of an MLRun
  Workflow.
  It provides the necessary instructions and dependencies for MLRun to execute your
  Kedro pipeline.
- `mlrun_runner.py`: This script executes the workflow defined in `workflow.py` on the
  target platform.

Push these additions to your repository:

```shell
git add .
git commit -m "init deployment"
git push
```

By initialising your deployment and generating these files, you are one step closer to running your Kedro pipeline on the target platform.

## 3. Set Deployment Configuration

To establish a connection between the MLRun client and the MLRun server or Iguazio
cluster, we need to provide specific configuration parameters.
These parameters should be set in `.mlrun/mlrun.env`.
Create this file and populate it with the following contents:

```shell
# Github token that has the permission to access the contents of the repo you created
GIT_TOKEN=ghp_foobarbazspamegg
# URL to the MLRun server / Iguazio cluster
MLRUN_DBPATH=https://mlrun-api.my.iguazio.cluster.com
# The next two parameters are only needed when connecting to the Iguazio cluster
# They are necessary to write data on the v3io file store
V3IO_USERNAME=your_username
V3IO_ACCESS_KEY=abc1234-111a-b222-c345678d
```

Replace the placeholder values with your own configuration details.

> Note that `.mlrun/.gitignore` should ignore `mlrun.env` - we do not want to expose our
> credentials!

## 4. Save Your Project to Target

With the deployment initialised and the configuration set, it's time to save your
project on the target platform.
Run the following command:

```shell
kedro mlrun save
```

This command creates an MLRun project and sets up a new MLRun Function and Workflow
(remember the scripts under the .mlrun/ directory?).
It also builds a Docker image.
Your Workflow will be executed in a container from this image.

In many cases, a Kedro pipeline starts by reading raw data.
To run the pipeline on the target platform, we need to upload these datasets to a file
store on the target.
The following command identifies all the free inputs by inspecting the Kedro catalog
and pipeline configuration, and then uploads them:

```shell
kedro mlrun log-inputs --pipeline __default__ --env local
```

## 5. Run

Now that we have completed the necessary setup steps, it's time to execute the pipeline
on the target platform:

```shell
kedro mlrun run
```

This command triggers the execution of your Kedro pipeline on the target platform,
utilising the configuration and deployment settings you have specified.

## What is next?

Congratulations!
You have successfully created and executed a Kedro pipeline on the target deployment
platform.
However, a pipeline is not necessarily a static entity that runs only once.
It can be improved and refined over time.
To iterate on your pipeline and incorporate enhancements, follow these steps:

1. Make changes to your Kedro project, such as modifying pipeline components, adding
   new features, or optimising existing functionality.
2. Rebuild the deployment files to reflect the updated code:
   Run the command `kedro mlrun rebuild --pipeline MY_PIPE --env MY_ENV`, replacing
   MY_PIPE and MY_ENV with the name of your pipeline and environment.
3. Use Git to commit and push your changes to your repository, ensuring that your
   remote codebase is up to date with your local codebase.
4. Finally, run the pipeline again on the target platform to observe the effects of
   your changes:
   Execute `kedro mlrun run`.

By following this iterative process, you can continuously improve your Kedro pipeline and adapt it to changing requirements and data sources.

Happy pipeline development and deployment!

[mck-playground]: https://github.com/McK-Playground
[spaceflights]: https://docs.kedro.org/en/stable/tutorial/spaceflights_tutorial.html