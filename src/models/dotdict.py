class DotDict(dict):
    """
    A dictionary subclass that allows accessing keys as attributes.
    Example:
        d = DotDict({'key': 'value'})
        print(d.key)  # Outputs: 'value'
    """
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]
