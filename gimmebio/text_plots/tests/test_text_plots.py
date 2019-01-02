"""Test suite for text plots."""

from unittest import TestCase

from gimmebio.text_plots import (
    text_histogram,
    text_scatter_plot
)


class TestTextPlots(TestCase):
    """Test suite for text plots."""

    def test_histogram(self):
        """Test that we get a histogram with the correct number of lines."""
        text_histo = text_histogram([1., 1., 2., 3., 3., 3.])
        lines = [line for line in text_histo.split('\n') if len(line.strip())]
        self.assertTrue(len(lines), 4)

    def test_scatter_plot(self):
        """Check that we correctly convert a seq to a matrix."""
        text_scatter = text_scatter_plot([(1., 1.), (2., 2.), (3., 3.)])
        lines = [line for line in text_scatter.split('\n') if len(line.strip())]
        self.assertTrue(len(lines), 4)
