# GH-PIPELINES
Grasshopper data pipeline repo for scheduled batch processes

## Environment variables:

Add the below export lines to your ~/.bash_profile (if that file does not exist, create one)   
Once added soure the profile using the following command: `. ~/.bash_profile`  


```
export ENV_NAME={env} # (env options: dev, qa, uat, prod)
export GH_VENV_HOME=~/.virtualenvs
export AWS_PROFILE={aws_profile}  
export AIRFLOW_HOME={repo_directory}  
export PYTHONPATH=$AIRFLOW_HOME  
export AIRFLOW__CORE__DAGS_FOLDER=$AIRFLOW_HOME/dags  
export AIRFLOW__CORE__REMOTE_LOG_CONN_ID=$AWS_PROFILE  
export AIRFLOW__CORE__REMOTE_BASE_LOG_FOLDER=s3://{env}-reservoir/airflow/logs/$AWS_PROFILE  # (env options: dev, qa, uat, prod)  
export AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://{username}:{password}@localhost/airflow  
export AIRFLOW__CORE__PLUGINS_FOLDER=$AIRFLOW_HOME/plugins
alias ghp="python3 $PYTHONPATH/ghp.py"
```

## Local package install

You can run the below command to install the recommended local python packages.
These packages (pandas, ipython, boto3, mypy, etc) will aid in development for the gh-pipeline repo.
Note that this is a local install and there could be dependacy conflicts if you already have
other python pacakges installed.  These are only **recommended** packages and are **not required**.  
Command: `ghp configure local`  

## List environments

To get a list of all gh-pipelines virtual environments enter the following:  `ghp list-envs`


# Airflow - Setup
Schedule and monitor pipeline workflows


## Database setup

Create a new database named `airflow`  

## Run commands:

- Source the profile: `. ~/.bash_profile`
- Install dependancies in virtual environment: `ghp configure airflow`
- Start Airflow locally: `ghp start`


## Note

- After `ghp start` command has been executed you can view the UI in your browser at localhost:8080
- All new dags should be placed in the dag folder
- The python operators used in those dags should go in the operators folder (see demo example)
- Run the command: `ghp renv airflow`.  This will give you access to run airflow specific commands like `airflow webserver -p 8080`


# Singer IO - Setup

## Run commands:

- Source the profile: `. ~/.bash_profile`  
- Install dependacies in virtual environments: `ghp configure {singer environment} {singer environment} ...`  
    - Note that there are many singer environment some include tap_s3_csv, singer_target_postgres, etc
    - You need to configure an environment before you can use the corresponding tap or target tools

## Creating taps and targets

- Each tap/target class combination should be created in a module under the singer_io folder (see **singer_io/demo.py** example)  
- All tap/target classes must inherit from the `singer_io.singer_device.SingerDevice` class  
- Property files ie. (config, catalog, properties) should reside in the template folder with the following structure:  
    - templates/{module_name}/{module_name}_{class_name}_{property}.json (see **singer_io/templates/demo** example)  
- Once a tap/target module has been created you can execute a migration using a similar to the below example:  
```
from singer_io.singer_device import migrate
from singer_io import demo

tap = demo.Tap() # represents Singer tap for demo module
target = demo.Target() # represents Singer target for demo module

migrate(tap, target) # transfer data from the tap source to the target destination
```

# DBT - Setup
Create database transformations

## Run commands:

- Source the profile: `. ~/.bash_profile`
- Create a profile.yml file in the follow directory (see sample below): `~/.dbt/profile.yml`
- Install dependacies in virtual environment: `ghp configure dbt`

```

# For more information on how to configure this file, please see:
# https://docs.getdbt.com/docs/profile

dbt_transforms:
  target: dev
  outputs:
    dev:
      type: postgres
      threads: 1
      host: localhost
      port: 5432
      user: postgres
      pass: postgres
      dbname: test
      schema: pipelines
    prod:
      type: postgres
      threads: 1
      host: 127.0.0.1
      port: 5439
      user: alice
      pass: pa55word
      dbname: warehouse
      schema: analytics
  

```

## Run dbt transformation

- All code related to dbt transformations should reside under the "dbt_transforms" folder
    - Note: That the majority of the tranformation code will be select statements in the **dbt_transforms/model** folder
    - Note: Tables created from processes external to dbt (ie. Singer) should be defined in the "on-run-start" section of **dbt_transforms/dbt_project.yml**
- To check dbt set up run the following: `echo "dbt debug" | ghp renv dbt -s`
- To run all dbt transformation execute the following: `echo "dbt run" | ghp renv dbt -s`

## References

- [Airflow Docs](https://airflow.apache.org/docs/stable/start.html)
- [Singer Docs](https://github.com/singer-io/getting-started)
- [DBT Docs](https://docs.getdbt.com/tutorial/create-a-project-dbt-cli/)



