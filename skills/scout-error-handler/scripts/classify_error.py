#!/usr/bin/env python3
"""
Error Classification Script for Scout Error Handler

Categorizes errors into types with severity levels.
Returns JSON with classification results.

Usage:
    python3 classify_error.py "<error_message>" [--context <context>]

Returns:
    {
        "type": "API_ERROR|NETWORK_ERROR|AUTH_ERROR|DATA_ERROR|RATE_LIMIT",
        "severity": "low|medium|high|critical",
        "retryable": true|false,
        "context": "<provided context>"
    }
"""

import sys
import re
import json
import argparse
from enum import Enum
from dataclasses import dataclass, asdict


class ErrorType(Enum):
    API_ERROR = "API_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    DATA_ERROR = "DATA_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    UNKNOWN = "UNKNOWN"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorClassification:
    type: str
    severity: str
    retryable: bool
    context: str = ""


# Error pattern mappings
ERROR_PATTERNS = {
    ErrorType.NETWORK_ERROR: {
        "patterns": [
            r"connection.*(timeout|refused|reset)",
            r"network.*(unreachable|error|failure)",
            r"dns.*(error|failure|not found)",
            r"socket.*error",
            r"ssl.*error",
            r"certificate.*(verify|error)",
            r"unable.*connect",
            r"host.*unreachable",
            r"no route to host",
            r"temporary failure",
        ],
        "severity": Severity.MEDIUM,
        "retryable": True,
    },
    ErrorType.API_ERROR: {
        "patterns": [
            r"5\d{2}.*error",
            r"internal server error",
            r"service unavailable",
            r"gateway timeout",
            r"bad gateway",
            r"server.*error",
            r"api.*(failure|error|down)",
            r"http.*5\d{2}",
        ],
        "severity": Severity.HIGH,
        "retryable": True,
    },
    ErrorType.RATE_LIMIT: {
        "patterns": [
            r"rate.*limit",
            r"too many requests",
            r"429",
            r"quota exceeded",
            r"throttled",
            r"limit exceeded",
            r"retry-after",
        ],
        "severity": Severity.MEDIUM,
        "retryable": True,
    },
    ErrorType.AUTH_ERROR: {
        "patterns": [
            r"unauthorized",
            r"authentication.*(failed|error|required)",
            r"403",
            r"401",
            r"forbidden",
            r"access.*denied",
            r"invalid.*(token|credential|key)",
            r"expired.*token",
            r"permission.*denied",
        ],
        "severity": Severity.CRITICAL,
        "retryable": False,
    },
    ErrorType.DATA_ERROR: {
        "patterns": [
            r"validation.*error",
            r"invalid.*(data|format|input)",
            r"required.*field",
            r"schema.*error",
            r"parse.*error",
            r"malformed",
            r"bad request",
            r"400",
            r"json.*error",
            r"type.*error",
        ],
        "severity": Severity.MEDIUM,
        "retryable": False,
    },
}


def classify_error(error_message: str, context: str = "") -> ErrorClassification:
    """Classify an error message into a type and severity."""
    error_lower = error_message.lower()
    
    for error_type, config in ERROR_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, error_lower, re.IGNORECASE):
                return ErrorClassification(
                    type=error_type.value,
                    severity=config["severity"].value,
                    retryable=config["retryable"],
                    context=context,
                )
    
    # Default: unknown error, not retryable
    return ErrorClassification(
        type=ErrorType.UNKNOWN.value,
        severity=Severity.HIGH.value,
        retryable=False,
        context=context,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Classify errors into types with severity levels"
    )
    parser.add_argument("error_message", help="The error message to classify")
    parser.add_argument(
        "--context",
        default="",
        help="Context where the error occurred (e.g., 'email_outreach')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (default behavior)",
    )
    
    args = parser.parse_args()
    
    classification = classify_error(args.error_message, args.context)
    
    output = asdict(classification)
    print(json.dumps(output, indent=2))
    
    # Exit code: 0 for retryable, 1 for non-retryable
    sys.exit(0 if classification.retryable else 1)


if __name__ == "__main__":
    main()
