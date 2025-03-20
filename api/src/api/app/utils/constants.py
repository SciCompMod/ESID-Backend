from enum import Enum


class MovementFilter(str, Enum):
    START = "START"
    END = "END"
    START_AND_END = "START_AND_END"
    START_OR_END = "START_OR_END"


class MigrationSort(str, Enum):
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"
    TOTAL = "TOTAL"
