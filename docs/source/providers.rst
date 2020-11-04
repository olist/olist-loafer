Providers
---------

Providers are responsible to retrieve messages and acknowledge it
(delete from source).


SQSProvider
~~~~~~~~~~~


``SQSProvider`` (located at ``loafer.ext.aws.providers``) receives the following options:

    * ``queue_name``: the queue name
    * ``options``: (optional): a ``dict`` with SQS options to retrieve messages.
      Example: ``{'WaitTimeSeconds: 5, 'MaxNumberOfMessages': 5}``

    Also, you might override any of the parameters below from boto library (all optional):

    * ``api_version``
    * ``aws_access_key_id``
    * ``aws_secret_access_key``
    * ``aws_session_token``
    * ``endpoint_url``
    * ``region_name``
    * ``use_ssl``
    * ``verify``

To use exponencial backoff factor options must contain :code:`'BackoffFactor': 1.5` and optionally :code:`'VisibilityTimeout': 30` (30 is used as default)
Whenever exponencial backoff is used, :code:`'AttributeNames': ['ApproximateReceiveCount']` is attached to receive message options (if not already in there) as is required to calculate visibility timeout.

Check `boto3 client`_ documentation for detailed information.

Usually, the provider are not configured manually, but set by :doc:`routes` and
it's helper classes.

.. _boto3 client: http://boto3.readthedocs.io/en/latest/reference/core/session.html#boto3.session.Session.client
