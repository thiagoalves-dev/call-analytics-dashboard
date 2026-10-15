class UnprocessableError(ValueError):
    pass


class AuthenticationError(Exception):
    pass


class ConflictError(ValueError):
    pass


class IncompleteSeedError(RuntimeError):
    pass
