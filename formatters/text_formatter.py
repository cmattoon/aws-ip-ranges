import dataclasses

from typing import Optional, List

from .formatter import Formatter

class TextFormatter(Formatter):
    """Plain text output"""
    code = 'text'
    
    def __init__(self, data, *args, **kwargs):
        super().__init__(data, args, kwargs)

        self._as_table = kwargs.get('table') is True

    def table(self, header_row: bool = True, headers: Optional[List[str]] = None) -> str:
        """
        Returns a markdown-style table

        Args:
            header_row (bool): Whether self.data[0] is a header row.
            headers (List[str]): Supply explicit headers for when header_row is False
        """

        row = self.data[0]
        if self.is_dataclass():
            fields = dataclasses.fields(row)
            headers = [f.name for f in fields]
        else:
            if header_row is True:
                headers = [str(c) for c in row]
            else:
                headers = ['??' for _ in range(len(row))]

        pads = [len(h) for h in headers]
        rows = []

        data = self.data[1:] if header_row is True else self.data
        
        for item in data:
            if dataclasses.is_dataclass(item):
                cols = []
                for i, field in enumerate(dataclasses.fields(item)):
                    value = str(getattr(item, field.name))
                    pads[i] = max(pads[i], len(value))
                    cols.append(value)
                rows.append(cols)
            else:
                _row = []
                for i, col in enumerate(item):
                    value = str(col)
                    pads[i] = max(pads[i], len(value))
                    _row.append(value)
                rows.append(_row)

        table = " | ".join(header.ljust(pads[i]) for i, header in enumerate(headers)) + "\n"
        table += "-+-".join("-" * width for width in pads) + "\n"

        for row in rows:
            table += " | ".join(str(row[i]).ljust(pads[i]) for i, _ in enumerate(headers)) + "\n"
        # data_rows = "\n".join(
        #     " | ".join(row[i].ljust(pads[i]) for i, _ in enumerate(headers))
        #     for row in rows
        # )
        #return f"{table}\n{data_rows}"
        return table
    
    def string(self):
        """Implements Formatter.string"""
        if len(self.data) == 0:
            return ""
        
        if type(self.data) is list and dataclasses.is_dataclass(self.data[0]):
            self._as_table = True
            
        if self._as_table:
            return self.table()

        # If it's a list of strings, print them out line by line
        if type(self.data) is list:
            for item in self.data:
                print(item)
            return
        return str(self.data)


