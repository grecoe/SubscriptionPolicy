import csv
from .generic import GenericObject


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
