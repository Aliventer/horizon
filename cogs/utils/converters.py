def to_separate_args(content: str, sep='|'):
    return list(map(lambda s: s.strip(), content.split(sep)))
