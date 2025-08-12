#!/usr/bin/env python3
"""
Simple test to verify both data source options work correctly.
This test doesn't require API keys - it just tests the class initialization and configuration.
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.github_projects_fetcher import GitHubProjectsFetcher
from agent.standup_agent import AutoStandupAgent
from config import Config

class TestDataSourceIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test configuration."""
        # Create temporary config for testing
        self.test_config_content = """
[settings]
mode = repo
owner = test-owner
repo = test-repo
hours = 24
llm_provider = groq
model = test-model
slack_channel = #test-channel
data_source = notion
posting_methods = slack

[members]
testuser_github = testuser
testuser_slack_id = U123456789
"""
        
        self.github_projects_config_content = """
[settings]
mode = repo
owner = test-owner
repo = test-repo
hours = 24
llm_provider = groq
model = test-model
slack_channel = #test-channel
data_source = github_projects
posting_methods = slack

[members]
testuser_github = testuser
testuser_slack_id = U123456789
"""

    def test_github_projects_fetcher_initialization(self):
        """Test that GitHubProjectsFetcher can be initialized."""
        with patch.dict(os.environ, {'G_TOKEN': 'test-token'}):
            # Create temporary config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
                f.write(self.test_config_content)
                config_path = f.name
            
            try:
                # Mock the Config class to use our test config
                with patch('tools.github_projects_fetcher.config') as mock_config:
                    mock_config.get.side_effect = lambda section, key, fallback=None: {
                        ('settings', 'mode'): 'repo',
                        ('settings', 'owner'): 'test-owner',
                        ('settings', 'repo'): 'test-repo',
                        ('settings', 'hours'): '24',
                        ('settings', 'organization'): None
                    }.get((section, key), fallback)
                    
                    fetcher = GitHubProjectsFetcher()
                    self.assertIsNotNone(fetcher)
                    self.assertEqual(fetcher.mode, 'repo')
                    self.assertEqual(fetcher.owner, 'test-owner')
                    self.assertEqual(fetcher.repo, 'test-repo')
                    
            finally:
                os.unlink(config_path)

    def test_agent_with_notion_data_source(self):
        """Test that agent correctly initializes with Notion data source."""
        with patch.dict(os.environ, {'G_TOKEN': 'test-token', 'NOTION_TOKEN': 'test-notion-token', 'DATABASE_ID': 'test-db-id'}):
            # Create temporary config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
                f.write(self.test_config_content)
                config_path = f.name
            
            try:
                with patch('agent.standup_agent.Config') as mock_config:
                    mock_config_instance = MagicMock()
                    mock_config_instance.get.side_effect = lambda section, key, fallback=None: {
                        ('settings', 'data_source'): 'notion',
                        ('settings', 'llm_provider'): 'groq',
                        ('settings', 'model'): 'test-model',
                        ('settings', 'posting_methods'): 'slack',
                        ('settings', 'mode'): 'repo',
                        ('settings', 'owner'): 'test-owner',
                        ('settings', 'repo'): 'test-repo',
                        ('settings', 'hours'): '24'
                    }.get((section, key), fallback)
                    mock_config_instance.get_section.return_value = {
                        'testuser_github': 'testuser',
                        'testuser_slack_id': 'U123456789'
                    }
                    mock_config.return_value = mock_config_instance
                    
                    # Mock the LLM provider creation
                    with patch('agent.standup_agent.create_llm_provider') as mock_llm:
                        mock_llm.return_value = MagicMock()
                        
                        # Mock the fetchers and posters
                        with patch('agent.standup_agent.GitHubFetcher') as mock_github, \
                             patch('agent.standup_agent.NotionFetcher') as mock_notion, \
                             patch('agent.standup_agent.GitHubProjectsFetcher') as mock_projects, \
                             patch('agent.standup_agent.SlackPoster') as mock_slack:
                            
                            agent = AutoStandupAgent()
                            self.assertEqual(agent.data_source, 'notion')
                            # Verify that NotionFetcher was used
                            mock_notion.assert_called_once()
                            
            finally:
                os.unlink(config_path)

    def test_agent_with_github_projects_data_source(self):
        """Test that agent correctly initializes with GitHub Projects data source."""
        with patch.dict(os.environ, {'G_TOKEN': 'test-token'}):
            # Create temporary config file  
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
                f.write(self.github_projects_config_content)
                config_path = f.name
            
            try:
                with patch('agent.standup_agent.Config') as mock_config:
                    mock_config_instance = MagicMock()
                    mock_config_instance.get.side_effect = lambda section, key, fallback=None: {
                        ('settings', 'data_source'): 'github_projects',
                        ('settings', 'llm_provider'): 'groq',
                        ('settings', 'model'): 'test-model',
                        ('settings', 'posting_methods'): 'slack',
                        ('settings', 'mode'): 'repo',
                        ('settings', 'owner'): 'test-owner',
                        ('settings', 'repo'): 'test-repo',
                        ('settings', 'hours'): '24'
                    }.get((section, key), fallback)
                    mock_config_instance.get_section.return_value = {
                        'testuser_github': 'testuser',
                        'testuser_slack_id': 'U123456789'
                    }
                    mock_config.return_value = mock_config_instance
                    
                    # Mock the LLM provider creation
                    with patch('agent.standup_agent.create_llm_provider') as mock_llm:
                        mock_llm.return_value = MagicMock()
                        
                        # Mock the fetchers and posters
                        with patch('agent.standup_agent.GitHubFetcher') as mock_github, \
                             patch('agent.standup_agent.GitHubProjectsFetcher') as mock_projects, \
                             patch('agent.standup_agent.SlackPoster') as mock_slack:
                            
                            agent = AutoStandupAgent()
                            self.assertEqual(agent.data_source, 'github_projects')
                            # Verify that GitHubProjectsFetcher was used
                            mock_projects.assert_called_once()
                            
            finally:
                os.unlink(config_path)

    def test_status_mapping(self):
        """Test that GitHub issue status mapping works correctly."""
        with patch.dict(os.environ, {'G_TOKEN': 'test-token'}):
            with patch('tools.github_projects_fetcher.Config') as mock_config:
                mock_config_instance = MagicMock()
                mock_config_instance.get.side_effect = lambda section, key, fallback=None: {
                    ('settings', 'mode'): 'repo',
                    ('settings', 'owner'): 'test-owner',
                    ('settings', 'repo'): 'test-repo',
                    ('settings', 'hours'): '24'
                }.get((section, key), fallback)
                mock_config.return_value = mock_config_instance
                
                fetcher = GitHubProjectsFetcher()
                
                # Test various status mappings
                self.assertEqual(fetcher._determine_status('open', []), 'To Do')
                self.assertEqual(fetcher._determine_status('closed', []), 'Done')
                self.assertEqual(fetcher._determine_status('open', ['in progress']), 'In Progress')
                self.assertEqual(fetcher._determine_status('open', ['blocked']), 'Blocked')
                self.assertEqual(fetcher._determine_status('open', ['review']), 'Under Review')
                self.assertEqual(fetcher._determine_status('open', ['testing']), 'Testing')

if __name__ == '__main__':
    unittest.main()