# Delta Reporter Core Service

This service is intended to manage core data that are sent or displayed at Delta Reporter

This service is designed to be deployed on AWS, GCP or Azure using Serverless framework

## Local development

Its highly recommended to use **[autoenv](https://github.com/inishchith/autoenv)** which will load the environment variables from the `.env` file, 
this is done each time you open Delta Core Service folder

To install it just run `pip install autoenv` and add `` source `which activate.sh` `` to your `~/.bashrc` or `~/.bash_profile`

```
echo "source `which activate.sh`" >> ~/.bashrc
OR
echo "source `which activate.sh`" >> ~/.bash_profile
```

Then reload your shell

```
source ~/.bashrc
OR
source ~/.bash_profile
```

To develop locally, create a virtual environment and install your dependencies:

```
npm install -g serverless
pip install virtualenv
virtualenv venv --python=python3
source venv/bin/activate
pip install -r requirements.txt
```

Then, run your app:

```
python app.py
 * Running on http://localhost:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
```

Navigate to [localhost:5000](http://localhost:5000) to see your app running locally.

## Database management

The Core service uses PosgreSQL as the database to persist all the data

SQLAlchemy is a ORM toolkit which is used to access the data on the database, more info about it can be found here https://www.tutorialspoint.com/sqlalchemy/index.htm

Finally, a migration tool called Alembic is used to maintain and track changes on  the schema https://pypi.org/project/alembic/

### Accesing the database

The best way to run the database is to run the image already incorporated in Docker Compose in Delta Reporter main repo.

`docker start delta_database`

Thats will start PosgreSQL on you local port `54320`, you can connect to it directly using psql:

`psql -h localhost -p 54320 -U delta delta_db`


### Loading schema and default values

After the database is up and running, use alembic to restore the schema

`python manage.py db upgrade`

Or using delta_core container:

`docker exec delta_core python manage.py db upgrade`

This command runs the scripts located in `migrations/versions/` in order to apply the changes on the database

if for any reason you want to restore the schema to a previous state, use `python manage.py db downgrade`

Then, to load default values, start the Core Service and send a POST request to this endpoint

`/initial_setup`

If you got

`
{
  "message": "Database initialized successfully"
}
`

Then the tables `ProjectStatus, LaunchStatus, TestSuiteStatus, TestType, TestRunStatus, TestStatus, TestResolution` are gonna have values on them
