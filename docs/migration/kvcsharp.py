"""A C# lexer good enough to make brace matching safe.

The failure this exists to prevent: counting braces with a raw character counter.
An interpolated string, a verbatim string, a char literal or a comment all contain
braces that are not code, and a counter that trips on one returns early and leaves
a method body dangling at member scope - which is what turns a refactor into 30
CS1519 "Invalid token 'throw' in a member declaration" errors.

So: tokenize, then match. Inside a token stream a brace is a brace.

Handles: line and block comments (nested, as C# allows), regular, verbatim and raw
string literals, char literals, and every interpolation form (the dollar-prefixed
and at-prefixed variants, including the raw ones). Interpolated holes are treated
as part of the string token, which is safe: a hole cannot contain an unbalanced
brace, and a nested interpolated string inside a hole is consumed by the same rule.
"""


class Token:
    __slots__ = ("kind", "start", "end", "text")

    def __init__(self, kind, start, end, text):
        self.kind = kind      # "code" | "comment" | "string" | "char"
        self.start = start
        self.end = end
        self.text = text

    def __repr__(self):
        return f"Token({self.kind}, {self.start}, {self.end})"


def _raw_string_end(src, i, quote_run):
    """End index of a C# raw string literal whose delimiter is quote_run quotes.

    A raw literal ends at a run of at least quote_run quotes, where a longer run is
    legal only if every quote in it belongs to the same closing run. Taking the
    whole run is what C# does, so we do too.
    """
    n = len(src)
    while i < n:
        if src[i] == '"':
            j = i
            while j < n and src[j] == '"':
                j += 1
            if (j - i) >= quote_run:
                return j
            i = j
        else:
            i += 1
    return -1


def _scan_hole(src, i, verbatim=False):
    """Scan an interpolation hole. src[i] is the ENTRY '{'. Return index past its '}'.

    A hole is CODE, not string text: it can contain a nested string literal, and that
    nested literal's quotes must not be mistaken for the enclosing literal's closer.
    Getting this wrong is what truncates `$"...{table.Replace("x", y)}..."` at the
    first inner quote, which then leaves a real '{' outside the string and makes every
    later brace count wrong.

    The entry brace is NOT counted: the loop starts after it at depth 0, so the hole's
    own '}' is the one that trips `depth == 0` and closes it. Counting it instead
    makes the hole swallow the rest of the file.
    """
    n = len(src)
    i += 1
    depth = 0
    while i < n:
        c = src[i]
        if c == "{":
            depth += 1
            i += 1
        elif c == "}":
            if depth == 0:
                return i + 1
            depth -= 1
            i += 1
        elif c == '"':
            # nested string inside the hole
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == '"':
                    j += 1
                    break
                if src[j] == "\n":
                    break
                j += 1
            i = j
        elif c == "'":
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == "'":
                    j += 1
                    break
                if src[j] == "\n":
                    break
                j += 1
            i = j
        else:
            i += 1
    return n


def _string_end(src, p, verbatim, raw_run, interpolated):
    """End index of the string literal whose opening quote run ends at p+raw_run.

    verbatim:     @"..." style, where "" is an escaped quote.
    raw_run:      length of the opening quote run for a raw literal, else 0.
    interpolated: True only for a $-prefixed literal. This flag is load-bearing: a
                  '{' is a hole only in an interpolated literal. In a plain string it
                  is an ordinary character, and treating it as a hole makes the
                  scanner run off swallowing real code until it finds a '}'.
    """
    n = len(src)
    if raw_run:
        if not interpolated:
            return _raw_string_end(src, p + raw_run, raw_run)
        # Raw interpolated: holes are the only thing needing care, and a raw literal
        # ends at its quote run, so scan for that while stepping over holes.
        i = p + raw_run
        while i < n:
            if src[i] == "{":
                i = _scan_hole(src, i, verbatim)
                continue
            if src[i] == '"':
                j = i
                while j < n and src[j] == '"':
                    j += 1
                if (j - i) >= raw_run:
                    return j
                i = j
                continue
            i += 1
        return n
    i = p + 1
    while i < n:
        ch = src[i]
        if verbatim:
            if ch == '"':
                if i + 1 < n and src[i + 1] == '"':
                    i += 2
                    continue
                return i + 1
            if ch == "{" and interpolated:
                i = _scan_hole(src, i, verbatim)
                continue
            i += 1
            continue
        if ch == "\\":
            i += 2
            continue
        if ch == '"':
            return i + 1
        if ch == "\n":
            return i                      # unterminated; do not run away
        if ch == "{" and interpolated:
            i = _scan_hole(src, i, verbatim)
            continue
        i += 1
    return n


def tokenize(src):
    """Return a list of Tokens covering the whole source. Never raises on odd input:
    an unterminated construct consumes to end of input rather than looping."""
    toks = []
    i, n = 0, len(src)
    code_start = 0

    def flush(upto):
        if upto > code_start:
            toks.append(Token("code", code_start, upto, src[code_start:upto]))

    while i < n:
        c = src[i]

        # ---- comments -------------------------------------------------------
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            j = src.find("\n", i)
            j = n if j < 0 else j
            flush(i)
            toks.append(Token("comment", i, j, src[i:j]))
            i = code_start = j
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            flush(i)
            depth, j = 1, i + 2
            while j < n and depth:
                if src.startswith("/*", j):
                    depth += 1
                    j += 2
                elif src.startswith("*/", j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            toks.append(Token("comment", i, j, src[i:j]))
            i = code_start = j
            continue

        # ---- strings --------------------------------------------------------
        # A leading run of $ and @, then the quote.
        p, has_dollar = i, False
        while p < n and src[p] in "$@":
            if src[p] == "$":
                has_dollar = True
            p += 1
        if p < n and src[p] == '"':
            is_verbatim = "@" in src[i:p]
            flush(i)
            raw_run = 0
            if not is_verbatim and src.startswith('"""', p):
                while p + raw_run < n and src[p + raw_run] == '"':
                    raw_run += 1
            j = _string_end(src, p, is_verbatim, raw_run, has_dollar)
            toks.append(Token("string", i, j, src[i:j]))
            i = code_start = j
            continue
        if has_dollar:
            i += 1          # a bare $ that is not a string prefix - ordinary code
            continue

        # ---- char literal ---------------------------------------------------
        if c == "'":
            flush(i)
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == "'":
                    j += 1
                    break
                if src[j] == "\n":
                    break
                j += 1
            toks.append(Token("char", i, j, src[i:j]))
            i = code_start = j
            continue

        i += 1

    flush(n)
    return toks


def mask(src):
    """Return src with every non-code region blanked out (newlines preserved).

    Brace matching over this is equivalent to matching over the token stream, and
    keeping the string the same length means offsets stay usable for slicing.
    """
    out = list(src)
    for t in tokenize(src):
        if t.kind == "code":
            continue
        for k in range(t.start, min(t.end, len(out))):
            if out[k] != "\n":
                out[k] = " "
    return "".join(out)


def match_brace(src, open_index):
    """Index of the '}' matching the '{' at open_index, or -1.

    open_index indexes into the ORIGINAL src; the scan runs over the masked copy so
    braces inside strings, chars and comments cannot be counted.
    """
    m = mask(src)
    if open_index >= len(m) or m[open_index] != "{":
        return -1
    depth = 0
    for j in range(open_index, len(m)):
        ch = m[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


def match_in(masked, open_index):
    """Match braces in an ALREADY-masked copy of a source file.

    Prefer this in a loop. match_brace(src, i) re-tokenizes the whole file every call,
    so scanning one file's definitions through it costs one tokenization per definition.
    Mask once, then match many.
    """
    if open_index < 0 or open_index >= len(masked) or masked[open_index] != "{":
        return -1
    depth = 0
    for j in range(open_index, len(masked)):
        ch = masked[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


def balance(src):
    """Net brace depth of src's code tokens, or None if unbalanced."""
    m = mask(src)
    depth = 0
    for ch in m:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return None
    return depth if depth == 0 else None
