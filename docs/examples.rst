Examples and Complex Use Cases
==============================

This page provides examples of how to use **Unaligned Frame** in more complex scenarios.

Aligning Data for Visualization
-------------------------------
Since most plotting libraries (like Matplotlib) expect data to be of equal length, you can use ``to_dataframe()`` to quickly pad your unaligned sequences with NaNs for plotting.

.. code-block:: python

   import matplotlib.pyplot as plt
   from unaligned_frame import UnalignedFrame

   data = {
       'Sensor_A': [20.1, 20.2, 20.5],
       'Sensor_B': [19.8, 19.9, 20.0, 20.1, 20.3]
   }
   uf = UnalignedFrame(data)

   # Pad with NaNs and plot
   uf.to_dataframe().plot()
   plt.title("Unaligned Sensor Data")
   plt.show()

Filtering and Subset Selection
------------------------------
You can use ``.loc`` to select specific windows of time (or indices) across all columns, even if they have different end points.

.. code-block:: python

   # Select rows 0 to 2 for all sensors
   subset = uf.loc[0:2, :]
   
   # Column A remains length 3, Column B is now length 3 (was 5)
   print(subset.shape)  # (3, 2)

Handling Batch Data Processing
------------------------------
You can iterate over columns to perform individual processing, leveraging the fact that each column is a native ``pd.Series``.

.. code-block:: python

   results = {}
   for col in uf.columns:
       series = uf[col]
       results[col] = series.mean()

   print(results)

Smart Ingestion with Internal Gaps
----------------------------------
UnalignedFrame preserves internal ``NaN`` values (representing missing data) while still trimming trailing padding.

.. code-block:: python

   # The NaN at index 1 is preserved, but the one at index 3 is trimmed
   data = {'A': [10, None, 30, None]}
   uf = UnalignedFrame(data)
   print(len(uf.A))  # Output: 3