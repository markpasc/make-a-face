class OopsMiddleware(object):

    def process_exception(self, request, exception):
        import logging
        log = logging.getLogger('.'.join((__name__, 'oops')))
        log.exception(exception)
        return None

