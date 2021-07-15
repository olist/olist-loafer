[![PyPI latest](https://img.shields.io/pypi/v/olist-loafer.svg?maxAge=2592000)](https://pypi.python.org/pypi/loafer)
[![Python versions](https://img.shields.io/pypi/pyversions/olist-loafer.svg?maxAge=2592000)](https://pypi.python.org/pypi/loafer)
[![License](https://img.shields.io/pypi/l/loafer.svg?maxAge=2592000)](https://pypi.python.org/pypi/olist-loafer)
[![CircleCI](https://circleci.com/gh/olist/olist-loafer/tree/main.svg?style=svg)](https://circleci.com/gh/olist/olist-loafer/tree/main)
[![Olist Sponsor](https://img.shields.io/badge/sponsor-olist-53b5f6.svg?style=flat-square)](http://opensource.olist.com/)


**olist-loafer** is an asynchronous message dispatcher for concurrent tasks processing, with the following features:

* Encourages decoupling from message providers and consumers
* Easy to extend and customize
* Easy error handling, including integration with sentry
* Easy to create one or multiple services
* Generic Handlers
* Amazon SQS integration

---
:information_source: Currently, only AWS SQS is supported

---

## How to use

A simple message forwader, from ``source-queue`` to ``destination-queue``:

```python
from loafer.ext.aws.handlers import SQSHandler
from loafer.ext.aws.routes import SQSRoute
from loafer.managers import LoaferManager

routes = [
    SQSRoute('source-queue', handler=SQSHandler('destination-queue')),
]

if __name__ == '__main__':
    manager = LoaferManager(routes)
    manager.run()
```

## How to contribute

Fork this repository, make changes and send us a pull request. We will review your changes and apply them. Before sending us your pull request please check if you wrote and ran tests:

```bash
make test
```
