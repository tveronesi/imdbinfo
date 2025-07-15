# Copyright (C) 2014-2025 H. Turgut Uyar <uyar@tekir.org>
#
# Piculet is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Piculet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Piculet.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from functools import partial
from types import MappingProxyType
from typing import Any, Literal, Mapping, TypeAlias

# Rimuovo l'import di typedload e jmespath se non disponibili
try:
    import typedload
except ImportError:
    typedload = None
try:
    from jmespath import compile as compile_jmespath
except ImportError:
    compile_jmespath = None

JSONNode: TypeAlias = dict

DocType: TypeAlias = Literal["json"]

_PARSERS: dict[DocType, Callable[[str], JSONNode]] = {
    "json": json.loads,
}

CollectedData: TypeAlias = Mapping[str, Any]

_EMPTY: CollectedData = MappingProxyType({})

Preprocessor: TypeAlias = Callable[[JSONNode], JSONNode]

preprocessors: dict[str, Preprocessor] = {}


class Preprocess:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Preprocessor = preprocessors[name]

    def __str__(self) -> str:
        return self.name


Postprocessor: TypeAlias = Callable[[CollectedData], CollectedData]

postprocessors: dict[str, Postprocessor] = {}


class Postprocess:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Postprocessor = postprocessors[name]

    def __str__(self) -> str:
        return self.name


Transformer: TypeAlias = Callable[[Any], Any]


transformers: dict[str, Transformer] = {
    "decimal": lambda x: Decimal(str(x)),
    "int": int,
    "lower": str.lower,
    "str": str,
    "strip": str.strip,
}


class Transform:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Transformer = transformers[name]

    def __str__(self) -> str:
        return self.name


class JSONPath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._compiled = compile_jmespath(path).search

    def __str__(self) -> str:
        return self.path

    def apply(self, root: JSONNode) -> Any:
        return self._compiled(root)  # type: ignore

    def select(self, root: JSONNode) -> list[JSONNode]:
        selected = self._compiled(root)
        return selected if selected is not None else []  # type: ignore


@dataclass(kw_only=True)
class JSONPicker:
    path: JSONPath
    transforms: list[Transform] = field(default_factory=list)
    foreach: JSONPath | None = None

    def extract(self, root: JSONNode) -> Any:
        return self.path.apply(root)


@dataclass(kw_only=True)
class JSONCollector:
    rules: list[JSONRule] = field(default_factory=list)
    transforms: list[Transform] = field(default_factory=list)
    foreach: JSONPath | None = None

    def extract(self, root: JSONNode) -> CollectedData:
        return collect(root, self.rules)


@dataclass(kw_only=True)
class JSONRule:
    key: str | JSONPicker
    extractor: JSONPicker | JSONCollector
    transforms: list[Transform] = field(default_factory=list)
    foreach: JSONPath | None = None


def extract(
    root: JSONNode, rule: JSONRule
) -> CollectedData:
    data: dict[str, Any] = {}

    if rule.foreach is None:
        subroots = [root]
    else:
        subroots = rule.foreach.select(root)

    for subroot in subroots:
        if rule.extractor.foreach is None:
            nodes = [subroot]
        else:
            nodes = rule.extractor.foreach.select(subroot)

        raws = [rule.extractor.extract(n) for n in nodes]
        raws = [v for v in raws if (v is not _EMPTY) and (v is not None)]
        if len(raws) == 0:
            continue
        if len(rule.extractor.transforms) == 0:
            values = raws
        else:
            values = []
            for value in raws:
                for transform in rule.extractor.transforms:
                    value = transform.apply(value)
                values.append(value)
        value = values[0] if rule.extractor.foreach is None else values

        for transform in rule.transforms:
            value = transform.apply(value)

        # Sostituisco il match-case con if-elif per compatibilità Python <3.10
        if isinstance(rule.key, str):
            key = rule.key
        elif isinstance(rule.key, JSONPicker):
            key = rule.key.extract(subroot)
            for key_transform in rule.key.transforms:
                key = key_transform.apply(key)
        else:
            key = None
        if key is not None:
            data[key] = value

    return data if len(data) > 0 else _EMPTY


def collect(
    root: JSONNode, rules: list[JSONRule]
) -> CollectedData:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract(root, rule)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


@dataclass(kw_only=True)
class _Spec:
    version: str
    url: str
    url_default_params: dict[str, Any] = field(default_factory=dict)
    url_transform: Transform | None = None
    doctype: DocType
    pre: list[Preprocess] = field(default_factory=list)
    post: list[Postprocess] = field(default_factory=list)


@dataclass(kw_only=True)
class JSONSpec(_Spec):
    path_type: Literal["jmespath"] = "jmespath"
    rules: list[JSONRule] = field(default_factory=list)


def scrape(document: str, spec: JSONSpec) -> CollectedData:
    root = _PARSERS[spec.doctype](document)
    for preprocess in spec.pre:
        root = preprocess.apply(root)
    # Sostituisco il match-case con if-elif per compatibilità Python <3.10
    if isinstance(root, dict) and isinstance(spec, JSONSpec):
        data = collect(root, spec.rules)
    else:
        raise TypeError("Node and spec types don't match")
    for postprocess in spec.post:
        data = postprocess.apply(data)
    return data


_data_classes = {Decimal}
deserialize = partial(
    typedload.load,
    strconstructed=_data_classes,
    pep563=True,
    basiccast=False,
)
serialize = partial(typedload.dump, strconstructed=_data_classes)

_spec_classes = {Preprocess, Postprocess, Transform, JSONPath}
load_spec = partial(
    deserialize,
    type_=JSONSpec,
    strconstructed=_spec_classes,
    failonextra=True,
)
dump_spec = partial(serialize, strconstructed=_spec_classes)