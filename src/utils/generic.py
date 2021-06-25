

class GenericObjectJson:
    def __init__(self, props):
        """props is a dict"""
        for prop in props:
            setattr(self, prop, props[prop])

class GenericObject:
    def __init__(self, props, vals):
        """
        props = list of names
        vals = list of corresponding values
        """
        idx = 0

        while idx < len(props):
            # Theres lots of numbers so try and convert
            prop_val = vals[idx]
            try:
                prop_val = int(prop_val)
            except ValueError as ex:
                try:
                    prop_val = float(prop_val)
                except ValueError as ex:
                    pass

            setattr(self, props[idx], prop_val)
            idx += 1