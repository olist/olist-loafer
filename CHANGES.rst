0.3.3 (2017-02-16)
------------------

* Add a logger.exception to message dispatcher before calling Route.error_handler

0.3.2 (2016-11-14)
------------------

* Add Route.error_handler method and hook it in message dispatcher

0.3.1 (2016-10-10)
------------------

* Use asyncio.wait instead of asyncio.gather


0.3.0 (2016-10-07)
------------------

* Async route consumption

0.2.3 (2016-10-06)
------------------

* Allow to configure max_jobs on Dispacher through Manager

0.2.2 (2016-08-29)
------------------

* Fix bug in default AWSConsumer

0.2.1 (2016-08-22)
------------------

* Update Makefile

0.2.0 (2016-08-22)
------------------

* Update AWS Consumer
* Make SNSMessageTranslator default message_translator

0.1.0 (2016-08-17)
------------------

* Changed version numbering to match other projects
* Fixed a bug with LoaferManager start. Sometimes when starting the event loop would already be closed.

0.0.4 (2016-06-27)
------------------

* Got rid of CLI. It runs by parameters, now
* Got rid of prettyconf dependency

0.0.3 (2016-04-24)
------------------

* Improve documentation
* Improve package metadata and dependencies
* Add loafer.aws.message_translator.SNSMessageTranslator class
* Fix ImportError exceptions for configuration that uses loafer.utils.import_callable


0.0.2 (2016-04-18)
------------------

* Fix build hardcoding tests dependencies


0.0.1 (2016-04-18)
------------------

* Initial release
