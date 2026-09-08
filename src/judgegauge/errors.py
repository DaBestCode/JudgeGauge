class JudgeGaugeError(Exception):
    """Base error for JudgeGauge."""


class ConfigurationError(JudgeGaugeError):
    """The calibration run cannot start with the supplied configuration."""


class ProviderError(JudgeGaugeError):
    """The judge endpoint could not complete a request."""


class InvalidReadout(JudgeGaugeError):
    """The judge returned a response that cannot be measured safely."""


class JudgeUnreliable(JudgeGaugeError):
    """The judge completed calibration but failed at least one frozen gate."""
