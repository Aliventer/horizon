def to_separate_args(content: str, sep='|'):
    return list(map(lambda s: s.strip(), content.split(sep)))


def prepare_bot_module(name: str):
    if not name.startswith('cogs.'):
        name = 'cogs.' + name
    return name
