class JulesAPIError(Exception):
    pass

class JulesAuthError(JulesAPIError):
    pass

class JulesRateLimitError(JulesAPIError):
    pass

class TransportError(Exception):
    pass
