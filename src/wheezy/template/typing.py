import typing
from abc import abstractmethod
from typing import TypeAlias

# flake8: noqa: E704

Token: TypeAlias = tuple[int, str, str]


class Builder:
    lineno: int

    @abstractmethod
    def start_block(self) -> None: ...  # pragma: nocover

    @abstractmethod
    def end_block(self) -> None: ...  # pragma: nocover

    @abstractmethod
    def add(self, lineno: int, code: str) -> None: ...  # pragma: nocover

    @abstractmethod
    def build_block(
        self, nodes: typing.Iterable[Token]
    ) -> None: ...  # pragma: nocover

    @abstractmethod
    def build_token(
        self,
        lineno: int,
        token: str,
        value: typing.Union[str, typing.Iterable[Token]],
    ) -> None: ...  # pragma: nocover


Tokenizer = typing.Callable[[typing.Match[str]], Token]
LexerRule = tuple[typing.Pattern[str], Tokenizer]
PreProcessorRule = typing.Callable[[str], str]
PostProcessorRule = typing.Callable[[list[Token]], str]
BuilderRule = typing.Callable[
    [
        Builder,
        int,
        str,
        typing.Union[str, list[str], typing.Iterable[Token], None],
    ],
    bool,
]
ParserRule = typing.Callable[[str], typing.Union[str, list[str]]]


class ParserConfig:
    end_tokens: list[str]
    continue_tokens: list[str]
    compound_tokens: list[str]
    out_tokens: list[str]


RenderTemplate = typing.Callable[
    [
        typing.Mapping[str, typing.Any],
        typing.Mapping[str, typing.Any],
        typing.Mapping[str, typing.Any],
    ],
    str,
]


class SupportsRender:
    @abstractmethod
    def render(
        self, ctx: typing.Mapping[str, typing.Any]
    ) -> str: ...  # pragma: nocover


TemplateClass = typing.Callable[[str, RenderTemplate], SupportsRender]


class Loader:
    @abstractmethod
    def list_names(self) -> tuple[str, ...]: ...  # pragma: nocover

    @abstractmethod
    def load(self, name: str) -> typing.Optional[str]: ...  # pragma: nocover
