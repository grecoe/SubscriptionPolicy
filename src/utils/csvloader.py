import csv

class GenericObject:
    def __init__(self, props, vals):
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

class S360Reader:
    @staticmethod
    def read_file(file_name):
        generic_object_return = []

        header = None
        rows = []

        with open(file_name, encoding="utf8", newline='') as csvfile:
            #spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            csvreader = csv.reader(csvfile, dialect='excel')
            for row in csvreader:
                if not header:
                    header = row
                else:
                    generic_object_return.append(
                        GenericObject(header, row)
                    )
                    rows.append(row)

        return generic_object_return
