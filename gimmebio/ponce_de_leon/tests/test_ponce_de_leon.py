#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ponce_de_leon` package."""


import unittest
from click.testing import CliRunner

from ponce_de_leon import api, cli

from .constants import *


def helper_test_help(runner, group, subcommand=None):
    args = ['--help']
    if subcommand:
        args = [subcommand, '--help']
    help_result = runner.invoke(group, args)
    assert help_result.exit_code == 0, help_result.output
    assert 'Show this message and exit.' in help_result.output, help_result.output
 

class TestPonce_de_leon(unittest.TestCase):
    """Tests for `ponce_de_leon` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_bc_by_region(self):
        """Test bc-by-region runs."""
        runner = CliRunner()
        helper_test_help(runner, cli.filter, 'bc-by-region')
        result = runner.invoke(
            cli.filter,
            ['bc-by-region', '-f', FASTQ_FILEPATH, BED_FILEPATH, SAM_FILEPATH]
        )
        assert result.exit_code == 0, result.output


    def test_read_by_bc(self):
        """Test read-by-bc runs."""
        runner = CliRunner()
        helper_test_help(runner, cli.filter, 'read-by-bc')        
        result = runner.invoke(
            cli.filter,
            ['read-by-bc', BC_LIST_FILEPATH, FASTQ_FILEPATH]
        )
        assert result.exit_code == 0, result.output

    def test_sam_by_bc(self):
        """Test sam-by-bc runs."""
        runner = CliRunner()
        helper_test_help(runner, cli.filter, 'sam-by-bc')
        result = runner.invoke(
            cli.filter,
            ['sam-by-bc', BC_LIST_FILEPATH, SAM_FILEPATH]
        )
        assert result.exit_code == 0, result.output
        
    def test_kmerize(self):
        """Test kmerize runs."""
        runner = CliRunner()
        helper_test_help(runner, cli.main, 'kmerize')
        result = runner.invoke(
            cli.main,
            ['kmerize', '-k 5', FASTQ_FILEPATH]
        )
        assert result.exit_code == 0, result.output

    def test_kmerize_sam(self):
        """Test kmerize runs."""
        runner = CliRunner()
        helper_test_help(runner, cli.main, 'kmerize')
        result = runner.invoke(
            cli.main,
            [ 'kmerize', '--sam-file', '-k 5', SAM_FILEPATH]
        )
        assert result.exit_code == 0, result.output

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_filter_subcommand_group(self):
        """Test the subcommand filter CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.filter)
        assert result.exit_code == 0
        help_result = runner.invoke(cli.filter, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

