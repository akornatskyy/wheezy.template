import typing
from abc import abstractmethod

from wheezy.template.comp import List, Tuple

Token = Tuple[int, str, str]


class Builder:
    lineno: int

    @abstractmethod
    def start_block(self) -> None:
        ...  # pragma: nocover

    @abstractmethod
    def end_block(self) -> None:
        ...  # pragma: nocover

    @abstractmethod
    def add(self, lineno: int, code: str) -> None:
        ...  # pragma: nocover

    @abstractmethod
    def build_block(self, nodes: typing.Iterable[Token]) -> None:
        ...  # pragma: nocover

    @abstractmethod
    def build_token(
        self,
        lineno: int,
        token: str,
        value: typing.Union[str, typing.Iterable[Token]],
    ) -> None:
        ...  # pragma: nocover


Tokenizer = typing.Callable[[typing.Match], Token]
LexerRule = Tuple[typing.Pattern, Tokenizer]
PreProcessorRule = typing.Callable[[str], str]
PostProcessorRule = typing.Callable[[List[Token]], str]
BuilderRule = typing.Callable[
    [
        Builder,
        int,
        str,
        typing.Union[str, List[str], typing.Iterable[Token]],
    ],
    bool,
]
ParserRule = typing.Callable[[str], typing.Union[str, List[str]]]


class ParserConfig:
    end_tokens: List[str]
    continue_tokens: List[str]
    compound_tokens: List[str]
    out_tokens: List[str]


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
    def render(self, ctx: typing.Mapping[str, typing.Any]) -> str:
        ...  # pragma: nocover


TemplateClass = typing.Callable[[str, RenderTemplate], SupportsRender]


class Loader:
    @abstractmethod
    def list_names(self) -> Tuple[str, ...]:
        ...  # pragma: nocover

    @abstractmethod
    def load(self, name: str) -> typing.Optional[str]:
        ...  # pragma: nocover
