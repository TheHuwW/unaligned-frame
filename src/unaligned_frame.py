import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union

class UnalignedFrame:
    """
    A container for pandas Series of unequal lengths, providing a DataFrame-like API.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None, preserve_internal: bool = True, _trim: bool = True):
        """
        Initialize the UnalignedFrame.

        Args:
            data (dict, optional): A dictionary where keys are column names and values
                are array-like objects. Defaults to None.
            preserve_internal (bool, optional): If True, internal NaNs are kept while
                trailing NaNs are trimmed. Defaults to True.
            _trim (bool, optional): Internal flag to bypass smart ingestion. Defaults to True.
        """
        self._data = {}
        if data:
            for col, values in data.items():
                series = pd.Series(values)

                # Smart Ingestion: Trim trailing NaNs to "unalign" the data.
                if _trim and not series.empty:
                    mask = series.notna()
                    if mask.any():
                        last_valid_index = mask.index[mask][-1]
                        # Slice up to the last valid index
                        series = series.loc[:last_valid_index]
                    else:
                        series = pd.Series([], dtype=series.dtype)
                self._data[col] = series

    @property
    def columns(self) -> List[str]:
        """Returns the column labels of the frame."""
        return list(self._data.keys())

    @property
    def shape(self) -> Tuple[int, int]:
        """Returns a tuple representing the dimensionality (max_rows, columns)."""
        max_rows = max([len(s) for s in self._data.values()]) if self._data else 0
        return (max_rows, len(self._data))

    def __len__(self):
        """Returns the length of the longest column."""
        return self.shape[0]

    def __getattr__(self, name):
        """Allow attribute access to columns."""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __getitem__(self, key):
        """Get column by name."""
        if key in self._data:
            return self._data[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        """Set or create a column."""
        self._data[key] = pd.Series(value)

    def __delitem__(self, key):
        """Delete a column."""
        if key in self._data:
            del self._data[key]
        else:
            raise KeyError(key)

    def __repr__(self):
        summary = [f"UnalignedFrame ({len(self._data)} columns)"]
        for col, s in self._data.items():
            summary.append(f" - {col}: Length {len(s)}, End Index {s.index[-1] if not s.empty else 'N/A'}")
        return "\n".join(summary)

    @property
    def iloc(self):
        """Purely integer-location based indexing for selection by position."""
        return _ILocIndexer(self)

    @property
    def loc(self):
        """Access a group of rows and columns by label(s) or a boolean array."""
        return _LocIndexer(self)

    def head(self, n: int = 5) -> "UnalignedFrame":
        """
        Return the first n rows for each column.
        
        Returns:
            UnalignedFrame: A new frame containing the top rows.
        """
        return UnalignedFrame({k: v.head(n) for k, v in self._data.items()}, _trim=False)

    def tail(self, n: int = 5) -> "UnalignedFrame":
        """
        Return the last n rows for each column.

        Returns:
            UnalignedFrame: A new frame containing the bottom rows.
        """
        return UnalignedFrame({k: v.tail(n) for k, v in self._data.items()}, _trim=False)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts to a standard padded Pandas DataFrame.
        
        Shorter columns will be padded with NaN values to match the longest column.
        """
        return pd.DataFrame(self._data)

    def to_csv(self, path_or_buf, **kwargs):
        """
        Write the UnalignedFrame to a comma-separated values (csv) file.
        
        Note: This exports as a padded DataFrame.
        """
        self.to_dataframe().to_csv(path_or_buf, **kwargs)

    @classmethod
    def from_csv(cls, path_or_buf, **kwargs):
        df = pd.read_csv(path_or_buf, **kwargs)
        return cls(df.to_dict(orient='list'))


class _BaseIndexer:
    def __init__(self, obj):
        self.obj = obj

    def _get_col_name(self, col_key):
        if isinstance(col_key, int):
            return self.obj.columns[col_key]
        return col_key

class _ILocIndexer(_BaseIndexer):
    def __getitem__(self, key):
        row_key, col_key = key if isinstance(key, tuple) else (key, slice(None))

        # Handle Column Selection
        col_names = self.obj.columns
        if isinstance(col_key, (slice, list, np.ndarray)):
            target_cols = col_names[col_key]
        else:
            target_cols = [self._get_col_name(col_key)]

        new_data = {}
        for col in target_cols:
            series = self.obj._data[col]
            if isinstance(row_key, int) and row_key >= len(series):
                raise IndexError(f"Index {row_key} is out of bounds for column '{col}' with length {len(series)}")
            new_data[col] = series.iloc[row_key]

        if not isinstance(col_key, (slice, list, np.ndarray)):
            return new_data[target_cols[0]]

        return UnalignedFrame(new_data, _trim=False)

class _LocIndexer(_BaseIndexer):
    def __getitem__(self, key):
        row_key, col_key = key if isinstance(key, tuple) else (key, slice(None))

        col_names = self.obj.columns
        if isinstance(col_key, slice):
            try:
                start = col_names.index(col_key.start) if col_key.start else 0
                stop = col_names.index(col_key.stop) + 1 if col_key.stop else len(col_names)
                target_cols = col_names[start:stop]
            except ValueError as e:
                raise KeyError(f"Column label not found in slice: {col_key}") from e
        elif isinstance(col_key, (list, np.ndarray)):
            target_cols = col_key
        else:
            target_cols = [col_key]

        new_data = {col: self.obj._data[col].loc[row_key] for col in target_cols}

        if not isinstance(col_key, (slice, list, np.ndarray)):
            return new_data[target_cols[0]]

        return UnalignedFrame(new_data, _trim=False)