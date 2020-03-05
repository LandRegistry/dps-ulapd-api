### Ulapd API

Ulapd API is a collection of web services built upon [Flask](http://flask.pocoo.org/) for managing user accounts

#### Development and Test

- Development

    - services/ : contains service classes
    - views/ : contains controller classes (i.e. resource classes)

- Environment

Docker and Docker-Compose are used to build local dev environment and how ualpd-api interacts with other web services is configured in `fragments/docker-compose-fragment.yml`

ualpd-api is accessible on port: __8008__


- Unit tests

The unit tests are contained in the unit_tests folder. [Pytest](https://docs.pytest.org/en/latest/) is used for unit testing. To run the tests use the following command:

    make unittest
    (or just py.test)

To run them and output a coverage report and a junit xml file run:

    make report="true" unittest

These files get added to a test-output folder. The test-output folder is created if doesn't exist.

To run the unit tests if you are using the common dev-env use the following command:

    docker-compose exec ualpd-api make unittest
    or, using the alias
    unit-test report-feeder

or

    docker-compose exec ualpd-api make report="true" unittest
    or, using the alias
    unit-test report-feeder -r

#### Linting

Linting is performed with [Flake8](http://flake8.pycqa.org/en/latest/). To run linting:

    docker-compose exec ualpd-api make lint

or

    cd into ualpd-api and run python3 -m flake8
