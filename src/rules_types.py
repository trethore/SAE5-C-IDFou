from typing import Literal

rule_type = Literal[
    "int",
    "float",
    "string",
    "date",
    "boolean",
    "array",
    "notNull",
    "unique",
    "notNegative",
    "toLowerCase",
    "toUpperCase",
    "beforeNow",
    "afterNow",
    "positiveNumber",
    "negativeNumber"
]

rules_dict = dict[str, dict[str, list[rule_type]]]
