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

Rebuild the image to contain the new dependencies:

    docker-compose build web

Make sure to commit updates to Pipfile and Pipfile.lock to git


### Javascript and CSS

JS and CSS are bundled using [parcel](https://parceljs.org/) - see `package.json`.

Dependencies are managed via `yarn`, e.g.

    docker-compose run --rm web yarn add bootstrap@4.x

Make sure to commit updates to package.json and yarn.lock to git.


Development setup
-----------------

Requires the environment variables `USER_ID=$(id -u)` and `GROUP_ID=$(id -g)` so that the container shares your UID and GID.

In one shell, run the frontend asset builder

    docker-compose run --rm web yarn dev

In another shell, initialise and run the django app

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
      > demodata.json

Only the minimal data needed to have a working system to click around in and
demonstrate all the features should be included. Avoid including massive amounts
of superfluous data. Update the command above as needed to get as close as possible
to exporting just the necessary data to get a running system.


Running tests
-------------

    docker-compose run --rm web python manage.py test

Tests might fail to connect to the databse if the docker-compose `db` service wasn't running and configured yet. Just check the logs for the `db` service and run the tests again.


Settings
--------

Undefined settings result in exceptions at startup to let you know they are not configured properly. It's one this way so that the defaults don't accidentally let bad things happen like forgetting analytics or connecting to the prod DB in development.


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
| `VAPID_PRIVATE_KEY` | unset | String | e.g. `/home/ubuntu/vapid_private_key.pem` |


Web Push Notifications
----------------------

To generate new vapid private key use the command bellow

    openssl ecparam -name prime256v1 -genkey -noout -out vapid_private_key.pem