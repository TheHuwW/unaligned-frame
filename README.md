# Unaligned Frame

A Python container for handling collections of `pandas.Series` with unequal lengths, providing a familiar DataFrame-like API.

## Features

- **Smart Ingestion**: Automatically trims trailing NaNs while preserving internal data gaps.
- **DataFrame-like Indexing**: Supports `.iloc` and `.loc` for both positional and label-based access.
- **Familiar API**: Provides `.head()`, `.tail()`, `.columns`, and `.shape` properties.
- **Easy Conversion**: Export to a standard padded `pandas.DataFrame` or CSV with a single call.

## Installation

Since this package is not on PyPI, you can install it directly from GitHub:

```bash
pip install git+https://github.com/TheHuwW/unaligned-frame.git
```

## Usage

```python
import numpy as np
from unaligned_frame import UnalignedFrame

data = {
    'A': [1, 2, 3, np.nan],
    'B': [10, np.nan, 30, 40, 50]
}

uf = UnalignedFrame(data)

# Column A is automatically trimmed to length 3
print(len(uf.A)) # Output: 3

# Access data like a DataFrame
print(uf.iloc[2, 'A']) # Output: 3

# Convert to a standard DataFrame (padded with NaNs)
df = uf.to_dataframe()
```

## Running Tests

```bash
python -m unittest discover tests
```
