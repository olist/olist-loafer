5.0.0 (2023-12-12)
----------
* chore: move to a PEP 621 compliant build system (hatch) (#44)
* chore: add every supported version to black settings (#46)
* chore: add toml extension to devcontainer
* fix: hatch environment definitions were wrong
* build: make github actions run only the tests for the right python version
* chore: add github actions extension to dev container
* fix: lint check-fixtures command wasn't working
* style: use black isort profile
* chore: remove boto3 dependency
* chore: bump minimum aiobotocore version to 2.0.0
* refactor: remove ConfigurationError exception
* refactor: remove concurrency limit param
* refactor: remove max threads param
* perf: instantiate a single aiobotocore session
* chore: leave max python version open

4.0.0 (2023-07-10)
------------------

* chore: drop support for Python 3.7
* chore: drop add_current_dir_to_syspath decorator
* chore: remove import_callable function
* chore: add devcontainer support
* refactor: move version compatibility logic to compat.py
* chore: initial support for Python 3.12
* style: add EditorConfig configuration

3.0.12 (2023-04-10)
------------------

* chore: replace CircleCI with Github Actions
* perf: start processing messages as soon as a route yields then

3.0.11 (2022-11-08)
------------------

* Add support for Python 3.11

3.0.10 (2022-02-25)
------------------

* Use newer aiobotocore version

3.0.9 (2021-10-29)
------------------

* Add Python 3.10 support
* (sqs) Handle errors while changing VisibilityTimeout

3.0.8 (2021-09-27)
------------------

* Limit SQS backoff factor

3.0.7 (2021-08-24)
------------------

* Fix error on SQS provider shutdown

3.0.6 (2021-08-24)
------------------

* Fix aiobotocore compatibility

3.0.5 (2021-07-16)
------------------

* Add new linters
* Move project to poetry

3.0.4 (2020-12-21)
------------------

* Add backoff factor support for SQS queue

3.0.3 (2020-11-05)
------------------

* Supress RuntimeError

3.0.2 (2020-11-04)
------------------

* Fix ProviderRuntimeError

3.0.1 (2020-10-29)
------------------

* Reraise RuntimeError as ProviderRuntimeError

3.0.0 (2020-10-20)
------------------

* Add support for python 3.9
* Drop support for python 3.5 and 3.6

2.0.0 (2020-07-02)
----------------------------------

* Inicial fork release(test)

2.0.0+post1 (2020-05-26)
----------------------------------

* Use sentry_sdk


1.3.2+post3 (2020-04-27)
----------------------------------

* Improve shut down methods


1.3.2+post2 (2020-04-14)
----------------------------------

* Update aiobotocore client


1.3.2+post1 (2019-04-27)
----------------------------------

* Update dependencies
* Update makefile for olist build


1.3.2 (2019-04-27)
----------------------------------

* Improve message processing (#48 by @lamenezes)
* Improve error logging (#39 by @wiliamsouza)
* Refactor in message dispatcher and event-loop shutdown
* Minor fixes and improvements

1.3.1 (2017-10-22)
----------------------------------

* Improve performance (#35 by @allisson)
* Fix requirement versions resolution
* Minor fixes and improvements

1.3.0 (2017-09-26)
----------------------------------

* Refactor tasks dispatching, it should improve performance
* Refactor SQSProvider to ignore HTTP 404 errors when deleting messages
* Minor fixes and improvements

1.2.1 (2017-09-11)
----------------------------------

* Bump boto3 version (by @daneoshiga)

1.2.0 (2017-08-15)
----------------------------------

* Enable provider parameters (boto client options)

1.1.1 (2017-06-14)
----------------------------------

* Bugfix: fix SNS prefix value in use for topic name wildcard (by @lamenezes)

1.1.0 (2017-05-01)
----------------------------------

* Added initial contracsts for class-based handlers
* Added generic handlers: SQSHandler/SNSHander
* Improve internal error handling
* Improve docs

1.0.2 (2017-04-13)
----------------------------------

* Fix sentry error handler integration

1.0.1 (2017-04-09)
----------------------------------

* Add tox and execute tests for py36
* Update aiohttp/aiobotocore versions
* Minor fixes and enhancements


1.0.0 (2017-03-27)
----------------------------------

* Major code rewrite
* Remove CLI
* Add better support for error handlers, including sentry/raven
* Refactor exceptions
* Add message metadata information
* Update message lifecycle with handler/error handler return value
* Enable execution of one service iteration (by default, it still runs "forever")


0.0.3 (2016-04-24)
----------------------------------

* Improve documentation
* Improve package metadata and dependencies
* Add loafer.aws.message_translator.SNSMessageTranslator class
* Fix ImportError exceptions for configuration that uses loafer.utils.import_callable


0.0.2 (2016-04-18)
----------------------------------

* Fix build hardcoding tests dependencies


0.0.1 (2016-04-18)
----------------------------------

* Initial release
