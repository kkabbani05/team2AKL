import pytest
import sys
import os
import json
from unittest.mock import patch, mock_open, MagicMock
import login_service
import api_client
import session_manager


class TestLoginSuccess:
    """Test successful login scenarios"""
    
    @patch("session_manager.save_session")
    @patch("api_client.fetch_board")
    @patch("api_client.login_with_server")
    @patch("builtins.open", new_callable=mock_open)
    @patch("builtins.print")
    def test_successful_login(self, mock_print, mock_file, mock_login_api, mock_fetch_board, mock_save_session):
        """Scenario: Successful login with server running"""
        # Setup mocks
        mock_login_api.return_value = (123, None)  # user_id=123, no error
        mock_fetch_board.return_value = {"guesses": []}  # Mock board data
        
        # Call login
        login_service.login("tom", [])
        
        # Assertions
        mock_login_api.assert_called_once_with("tom")
        mock_save_session.assert_called_once_with(123, "tom")
        mock_fetch_board.assert_called_once_with(123)
        
        # Check current_player.txt was written
        mock_file.assert_called_with("current_player.txt", "w")
        
        # Check success message printed
        printed_calls = [str(call) for call in mock_print.call_args_list]
        assert any("May the odds be in your favor tom" in str(call) for call in printed_calls)
    
    @patch("session_manager.save_session")
    @patch("api_client.fetch_board")
    @patch("api_client.login_with_server")
    @patch("builtins.open", new_callable=mock_open)
    @patch("builtins.print")
    def test_login_case_insensitive_output(self, mock_print, mock_file, mock_login_api, mock_fetch_board, mock_save_session):
        """Scenario: Login is case-insensitive in output"""
        # User types "ALICE", should preserve case in output
        mock_login_api.return_value = (456, None)
        mock_fetch_board.return_value = {"guesses": []}
        
        login_service.login("ALICE", [])
        
        # Check output preserves original case
        printed_calls = [str(call) for call in mock_print.call_args_list]
        assert any("May the odds be in your favor ALICE" in str(call) for call in printed_calls)


class TestLoginServerDown:
    """Test server down scenarios"""
    
    @patch("session_manager.save_session")
    @patch("api_client.login_with_server")
    @patch("builtins.print")
    def test_server_down_connection_error(self, mock_print, mock_login_api, mock_save_session):
        """Scenario: Login fails when server is down"""
        # API returns server_down error
        mock_login_api.return_value = (None, "server_down")
        
        login_service.login("alice", [])
        
        # Should not save session
        mock_save_session.assert_not_called()
        
        # Should print error message
        printed_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Looks like the wurdal servers are taking a loss" in str(call) for call in printed_calls)


class TestLoginUserNotFound:
    """Test user not found scenarios"""
    
    @patch("session_manager.save_session")
    @patch("api_client.login_with_server")
    @patch("builtins.print")
    def test_user_not_found_404(self, mock_print, mock_login_api, mock_save_session):
        """Scenario: Login fails with unregistered user"""
        # API returns user_not_found error
        mock_login_api.return_value = (None, "user_not_found")
        
        login_service.login("jordan", [])
        
        # Should not save session
        mock_save_session.assert_not_called()
        
        # Should print exact error message with username
        printed_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Could not find user jordan" in str(call) for call in printed_calls)
        assert any("wurdal register jordan" in str(call) for call in printed_calls)
    
    @patch("session_manager.save_session")
    @patch("api_client.login_with_server")
    @patch("builtins.print")
    def test_user_not_found_preserves_case(self, mock_print, mock_login_api, mock_save_session):
        """Scenario: Error message preserves original username case"""
        mock_login_api.return_value = (None, "user_not_found")
        
        login_service.login("JORDAN", [])
        
        # Should preserve uppercase in error
        printed_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Could not find user JORDAN" in str(call) for call in printed_calls)


class TestLogout:
    """Test logout scenarios"""
    
    @patch("session_manager.clear_session")
    @patch("builtins.open", new_callable=mock_open)
    @patch("builtins.print")
    def test_logout_success(self, mock_print, mock_file, mock_clear_session):
        """Test successful logout"""
        
        login_service.logout()
        
        # Session should be cleared
        mock_clear_session.assert_called_once()
        
        # current_player.txt should be cleared
        mock_file.assert_called_with("current_player.txt", "w")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
