[![codecov](https://codecov.io/gh/OpenUpSA/muni_portal/branch/master/graph/badge.svg)](https://codecov.io/gh/OpenUpSA/muni-portal-backend/)
[![Build Status](https://travis-ci.org/OpenUpSA/muni_portal.png)](https://travis-ci.org/OpenUpSA/muni-portal-backend)


Muni Portal
===========


Project Layout
--------------


### Django

Apps go in the project directory `muni_portal`


### Python

Dependencies are managed via pyproject.toml in the docker container.

Add and lock dependencies in a temporary container:

    docker-compose run --rm web poetry add pkgname==1.2.3

Remove dependencies by executing as `root`, like this:

    docker-compose run --rm -u root web poetry remove pkgname

> NOTE: Removing packages requires root privileges because Poetry is installed as root before the django user is created,
> resulting in the normal container user not having permission to remove system files in the container

Rebuild the image to ensure subsequent containers are based on the updated dependencies:

    docker-compose build web

Make sure to commit updates to `pyproject.toml` and `poetry.lock` to git


Development setup
-----------------

If you are using Linux, it is recommended that you set the environment variables `USER_ID=$(id -u)` and `GROUP_ID=$(id -g)`
so that the docker container shares your UID and GID. This is so that you have permission to edit the files created by the container process, e.g. migrations.

You can do this by exporting the variables in your shell before running docker commands

    export USER_ID=$(id -u)
    export GROUP_ID=$(id -g)

Initialise and run the django app

    docker-compose run --rm web bin/wait-for-postgres.sh
    docker-compose run --rm web python manage.py migrate
    docker-compose run --rm web python manage.py loaddata seeddata.json demodata.json
    docker-compose up

The demodata fixture should install

- A few basic pages
- A superuser with username `admin` and password `password`

If you need to destroy and recreate your dev setup, e.g. if you've messed up your
database data or want to switch to a branch with an incompatible database schema,
you can destroy all volumes and recreate them by running the following, and running
the above again:

    docker-compose down --volumes


To run Django Q tasks in development, you can either run 

    docker-compose run --rm  web python manage.py qcluster

with `DJANGO_Q_SYNC=False` in your .env file

Or you can set `DJANGO_Q_SYNC=True` to run the tasks synchronously in the same process as your Django server without 
need to start a `cluster` process.


### Maintaining the demo data fixture

The demo data fixture was produced using the command

    docker-compose run --rm web python manage.py dumpdata --natural-foreign --indent 2\
      -e contenttypes \
      -e auth.permission \
      -e wagtailcore.groupcollectionpermission \
      -e wagtailcore.grouppagepermission \
      -e wagtailcore.pagelogentry \
      -e wagtailimages.rendition \
      -e sessions \
      -e core.contactdetailtype \
      -e admin.logentry \
      -e token_blacklist \
      > demodata.json

Only the minimal data needed to have a working system to click around in and
demonstrate all the features should be included. Avoid including massive amounts
of superfluous data. Update the command above as needed to get as close as possible
to exporting just the necessary data to get a running system.


Running tests
-------------
If you haven't yet, you'll first need to run `collectstatic` before running tests

    docker-compose run --rm web python manage.py collectstatic --no-input

Then run the test suite

    docker-compose run --rm web python manage.py test

Tests might fail to connect to the databse if the docker-compose `db` service wasn't running and configured yet. Just check the logs for the `db` service and run the tests again.


Migrations in deployment
------------------------

Migrations are run automatically on deployment to dokku via the script in `app.json`.


Settings
--------

Undefined settings result in exceptions at startup to let you know they are not configured properly.
It's this way so that the defaults don't accidentally let bad things happen like forgetting analytics or
connecting to the prod DB in development.


| Key | Default | Type | Description |
|-----|---------|------|-------------|
| `DATABASE_URL` | undefined | String | `postgresql://user:password@hostname/dbname` style URL |
| `DJANGO_DEBUG_TOOLBAR` | False | Boolean | Set to `True` to enable the Django Debug toolbar NOT ON A PUBLIC SERVER! |
| `DJANGO_SECRET_KEY` | undefined | String | Set this to something secret and unguessable in production. The security of your cookies and other crypto stuff in django depends on it. |
| `TAG_MANAGER_CONTAINER_ID` | undefined | String | [Google Tag Manager](tagmanager.google.com) Container ID. [Use this to set up Google Analytics.](https://support.google.com/tagmanager/answer/6107124?hl=en). Requried unless `TAG_MANAGER_ENABLED` is set to `False` |
| `TAG_MANAGER_ENABLED` | `True` | Boolean | Use this to disable the Tag Manager snippets, e.g. in dev or sandbox. |
| `AWS_STORAGE_BUCKET_NAME` | `None` | String | e.g. `muni-portal-backend` |
| `AWS_SECRET_ACCESS_KEY` | `None` | String | |
| `AWS_ACCESS_KEY_ID` | `None` | String | e.g. `AKIAYIFP5EK2FOOBAR` |
| `AWS_S3_REGION_NAME` | `None` | String | e.g. `eu-west-1` |
| `AWS_S3_CUSTOM_DOMAIN` | `None` | String | e.g. `muni-portal-backend.s3.amazonaws.com` |
| `MEDIA_URL` | `/media/` | String | e.g. `https://muni-portal-backend.s3.amazonaws.com` |
| `DEFAULT_FILE_STORAGE` | `'django.core.files.storage.FileSystemStorage'` | String | e.g. `storages.backends.s3boto3.S3Boto3Storage` |
| `WAGTAILAPI_BASE_URL` | unset | String | e.g. `https://muni-portal-backend.openup.org.za` |
| `DEFAULT_FROM_EMAIL` | undefined | String | e.g. `Default from email for notifications` |
| `DEBUG_CACHE` | False | Boolean | Set to true to enable django cache despite DEBUG being True. Then it uses in-memory cache so reset cache by restarting the container. |
| `ENVIRONMENT` | `development` | String | Set to the environment the code is running in, e.g. development, production. |
| `SENTRY_DSN` | `None` | String | Used for Sentry configuration. [Where to find your DSN?](https://docs.sentry.io/product/sentry-basics/dsn-explainer/#where-to-find-your-dsn) |
| `SENTRY_PERF_SAMPLE_RATE` | `0.1` | Float | Sentry performance sampling rate. Don't set this too high, or else you might use up your Sentry quota! [What is Sentry Performance?](https://docs.sentry.io/platforms/python/guides/django/performance/) |
| `COLLABORATOR_API_USERNAME` | `None` | String | Username for Collaborator Web API (Service Requests) |
| `COLLABORATOR_API_PASSWORD` | `None` | String | Password for Collaborator Web API (Service Requests) |
| `COLLABORATOR_API_BASE_URL` | `https://consumercollab.collaboratoronline.com` | String | Base API URL for Collaborator Web API (Service Requests) |


Security
--------

Exploits to watch out for with security of this service (not comprehensive):

- Do not allow credentialed access to /admin or the Webflow API where an admin might be logged in and an attacker uses their session to fetch or modify information (CORS and CSRF)
  - Do not allow cookie or basic authentication to user-endpoints like fetching/updating their profile or performing actions on their behalf (CORS and CSRF)
    - By only allowing token-based authentication, the browser can not be tricked into supplying credentials
    - CORS by default disallows the browser from automatically supplying credentials - be careful about changing this behaviour

Specific approach to CORS and CSRF

- the resources relevant to CSRF are the ones protected by automated credential headers like session cookie or basic authentication.
- our custom resources disallow both those, and are therefore secure against CSRF
- wagtail (API and CMS) and the django admin uses session cookies
- any resources that work with automated credential headers like cookies or basic auth must be protected from access by unsafe origins using CORS.
- CORS must therefore not be allowed for admin or wagtail resources.
- CORS may only be allowed for our custom resources that only allow token authentication

Important configuration for security

- CORS_URLS_REGEX - Currently allows access to user account API. [Example here](https://regex101.com/r/Ui3hn2/3).

- CORS_ALLOWED_ORIGIN_REGEXES - Should be configured via environment. [Example here](https://regex101.com/r/q6jWFA/2/).

- List of allowed headers: Accept, Accept-Encoding, Content-Type, Charset, HTTP_AUTHORIZATION, Origin.
