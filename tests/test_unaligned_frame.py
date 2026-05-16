import unittest
import pandas as pd
import numpy as np
import io
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from unaligned_frame import UnalignedFrame 

class TestUnalignedFrame(unittest.TestCase):
    def setUp(self):
        """Standard setup: Runs before every individual test."""
        self.data = {
            'A': [1, 2, 3, np.nan],
            'B': [10, np.nan, 30, 40, 50]
        }
        # We pass the dict directly to bypass Pandas' requirement 
        # that all arrays must be the same length.
        self.uf = UnalignedFrame(self.data, preserve_internal=False)

    def test_smart_ingestion(self):
        """Test if trailing NaNs are removed but internal ones kept."""
        # Col A should be trimmed to length 3 (1, 2, 3)
        self.assertEqual(len(self.uf.A), 3)
        # Col B should have length 5 (10, NaN, 30, 40, 50)
        self.assertEqual(len(self.uf.B), 5)
        self.assertTrue(np.isnan(self.uf['B'].iloc[1]))

    def test_attribute_access(self):
        """Verify columns can be accessed as attributes."""
        self.assertIsInstance(self.uf.A, pd.Series)
        with self.assertRaises(AttributeError):
            _ = self.uf.NonExistent

    def test_iloc_access(self):
        """Test positional indexing with bounds checking."""
        # Test valid access
        self.assertEqual(self.uf.iloc[2, 'A'], 3)
        self.assertEqual(self.uf.iloc[4, 1], 50) # Access 'B' (index 1), row 4
        
        # Test out of bounds
        with self.assertRaises(IndexError):
            _ = self.uf.iloc[3, 'A']

    def test_iloc_slicing(self):
        """Verify .iloc supports slicing for both rows and columns."""
        # Row slicing (returns Series)
        row_slice = self.uf.iloc[0:2, 0]
        self.assertEqual(len(row_slice), 2)
        self.assertEqual(row_slice.iloc[1], 2)

        # Column slicing (returns UnalignedFrame)
        col_slice = self.uf.iloc[0:2, 0:2]
        self.assertIsInstance(col_slice, UnalignedFrame)
        self.assertEqual(len(col_slice.A), 2)
        self.assertEqual(len(col_slice.B), 2)
        
        # Verify specific values; use np.isnan because NaN != NaN
        self.assertEqual(col_slice.iloc[0, 1], 10)
        self.assertTrue(np.isnan(col_slice.iloc[1, 1]))

    def test_loc_access(self):
        """Verify .loc supports label-based indexing and slicing."""
        # Single label access
        self.assertEqual(self.uf.loc[2, 'A'], 3)
        
        # Slicing (inclusive)
        loc_slice = self.uf.loc[0:2, 'A':'B']
        self.assertIsInstance(loc_slice, UnalignedFrame)
        self.assertEqual(len(loc_slice.A), 3)
        self.assertEqual(len(loc_slice.B), 3)
        
        # List based access
        loc_list = self.uf.loc[[0, 2], ['A']]
        self.assertIsInstance(loc_list, UnalignedFrame)
        self.assertEqual(len(loc_list.A), 2)

    def test_assignment(self):
        """Test if adding/modifying columns works via __setitem__."""
        self.uf['C'] = [100, 200]
        self.assertEqual(len(self.uf.C), 2)

    def test_head_tail_structure(self):
        """Verify head and tail return dictionaries of the correct length."""
        head_dict = self.uf.head(2)
        tail_dict = self.uf.tail(1)
        self.assertEqual(len(head_dict['A']), 2)
        self.assertEqual(tail_dict['B'].iloc[0], 50)

    def test_to_dataframe(self):
        """Test conversion back to a standard padded Pandas DataFrame."""
        df_exported = self.uf.to_dataframe()
        
        self.assertIsInstance(df_exported, pd.DataFrame)
        # Should be padded to the max length (5)
        self.assertEqual(df_exported.shape, (5, 2))
        # Verify padding on the short column 'A'
        self.assertTrue(np.isnan(df_exported.loc[3, 'A']))
        self.assertTrue(np.isnan(df_exported.loc[4, 'A']))

    def test_to_csv(self):
        """Verify saving to CSV produces expected output."""
        buffer = io.StringIO()
        # Save to buffer to avoid creating actual files
        self.uf.to_csv(buffer, index=False)
        csv_content = buffer.getvalue()
        
        # Check header and content
        self.assertIn("A,B", csv_content)
        self.assertIn("1.0,10.0", csv_content)

    def test_from_csv(self):
        """Verify loading from CSV correctly unaligns the data."""
        # CSV with trailing NaNs in column A
        csv_data = "A,B\n1,10\n2,\n3,30\n,40\n,50"
        buffer = io.StringIO(csv_data)
        
        new_uf = UnalignedFrame.from_csv(buffer)
        
        # Column A should be trimmed to 3 elements
        self.assertEqual(len(new_uf.A), 3)
        # Column B should keep its length of 5 (internal NaN preserved)
        self.assertEqual(len(new_uf.B), 5)

if __name__ == '__main__':
    unittest.main()