from extensions import cache


def cache_key(prefix, *args, **kwargs):
    parts = [prefix] + list(map(str, args)) + \
        [f"{k}:{v}" for k, v in sorted(kwargs.items())]
    return "|".join(parts)
