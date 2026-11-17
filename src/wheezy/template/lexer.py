import typing
from collections.abc import Mapping

from wheezy.template.typing import (
    LexerRule,
    PostProcessorRule,
    PreProcessorRule,
    Token,
)


def lexer_scan(
    extensions: list[typing.Any],
) -> Mapping[str, typing.Any]:
    """Scans extensions for ``lexer_rules`` and ``preprocessors``
    attributes.
    """
    lexer_rules: dict[int, LexerRule] = {}
    preprocessors: list[PreProcessorRule] = []
    postprocessors: list[PostProcessorRule] = []
    for extension in extensions:
        if hasattr(extension, "lexer_rules"):
            lexer_rules.update(extension.lexer_rules)
        if hasattr(extension, "preprocessors"):
            preprocessors.extend(extension.preprocessors)
        if hasattr(extension, "postprocessors"):
            postprocessors.extend(extension.postprocessors)
    return {
        "lexer_rules": [lexer_rules[k] for k in sorted(lexer_rules.keys())],
        "preprocessors": preprocessors,
        "postprocessors": postprocessors,
    }


class Lexer:
    """Tokenizes input source per rules supplied."""

    def __init__(
        self,
        lexer_rules: list[LexerRule],
        preprocessors: list[PreProcessorRule] | None = None,
        postprocessors: list[PostProcessorRule] | None = None,
        **ignore: typing.Any,
    ) -> None:
        """Initializes with ``rules``. Rules must be a list of
        two elements tuple: ``(regex, tokenizer)`` where
        tokenizer if a callable of the following contract::

            def tokenizer(match):
                return end_index, token, value
        """
        self.rules = lexer_rules
        self.preprocessors = preprocessors or []
        self.postprocessors = postprocessors or []

    def tokenize(self, source: str) -> list[Token]:
        """Translates ``source`` accoring to lexer rules into
        an iteratable of tokens.
        """
        for preprocessor in self.preprocessors:
            source = preprocessor(source)
        tokens: list[Token] = []
        append = tokens.append
        pos = 0
        lineno = 1
        end = len(source)
        while pos < end:
            for regex, tokenizer in self.rules:
                m = regex.match(source, pos, end)
                if m is not None:
                    npos, token, value = tokenizer(m)
                    assert npos > pos
                    append((lineno, token, value))
                    lineno += source[pos:npos].count("\n")
                    pos = npos
                    break
            else:
                raise AssertionError("Lexer pattern mismatch.")
        for postprocessor in self.postprocessors:
            postprocessor(tokens)
        return tokens
