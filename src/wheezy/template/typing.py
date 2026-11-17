import re
import typing
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from typing import Protocol, TypeAlias

# flake8: noqa: E704

Token: TypeAlias = tuple[int, str, str]


class Builder(ABC):
    lineno: int

    @abstractmethod
    def start_block(self) -> None: ...  # pragma: nocover

    @abstractmethod
    def end_block(self) -> None: ...  # pragma: nocover

    @abstractmethod
    def add(self, lineno: int, code: str) -> None: ...  # pragma: nocover

    @abstractmethod
    def build_block(
        self, nodes: Iterable[Token]
    ) -> None: ...  # pragma: nocover

    @abstractmethod
    def build_token(
        self,
        lineno: int,
        token: str,
        value: str | Iterable[Token],
    ) -> None: ...  # pragma: nocover


Tokenizer = Callable[[re.Match[str]], Token]
LexerRule = tuple[re.Pattern[str], Tokenizer]
PreProcessorRule = Callable[[str], str]
PostProcessorRule = Callable[[list[Token]], str]
BuilderRule = Callable[
    [
        Builder,
        int,
        str,
        str | list[str] | Iterable[Token] | None,
    ],
    bool,
]
ParserRule = Callable[[str], str | list[str]]


class ParserConfig(Protocol):
    end_tokens: list[str]
    continue_tokens: list[str]
    compound_tokens: list[str]
    out_tokens: list[str]


RenderTemplate = Callable[
    [
        Mapping[str, typing.Any],
        Mapping[str, typing.Any],
        Mapping[str, typing.Any],
    ],
    str,
]


class SupportsRender(ABC):
    @abstractmethod
    def render(
        self, ctx: Mapping[str, typing.Any]
    ) -> str: ...  # pragma: nocover


TemplateClass = Callable[[str, RenderTemplate], SupportsRender]


class Loader(ABC):
    @abstractmethod
    def list_names(self) -> tuple[str, ...]: ...  # pragma: nocover

    @abstractmethod
    def load(self, name: str) -> str | None: ...  # pragma: nocover
