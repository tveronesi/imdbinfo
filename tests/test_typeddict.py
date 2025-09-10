"""Tests for TypedDict functionality in get_trivia and get_reviews functions."""
import pytest
from imdbinfo.models import TriviaItem, ReviewItem, InterestScore
from imdbinfo.parsers import parse_json_trivia, parse_json_reviews


def test_trivia_item_structure():
    """Test that TriviaItem has the correct structure."""
    mock_data = {
        'trivia': {
            'edges': [{
                'node': {
                    'displayableArticle': {
                        'body': {
                            'plaidHtml': '<p>Interesting trivia fact</p>'
                        }
                    },
                    'interestScore': {
                        'usersVoted': 150,
                        'usersInterested': 120
                    }
                }
            }]
        }
    }
    
    trivia_list = parse_json_trivia(mock_data)
    
    assert len(trivia_list) == 1
    trivia_item = trivia_list[0]
    
    # Check that it has the required keys
    assert 'body' in trivia_item
    assert 'interestScore' in trivia_item
    
    # Check the types and values
    assert trivia_item['body'] == '<p>Interesting trivia fact</p>'
    assert isinstance(trivia_item['interestScore'], dict)
    assert trivia_item['interestScore']['usersVoted'] == 150
    assert trivia_item['interestScore']['usersInterested'] == 120


def test_review_item_structure():
    """Test that ReviewItem has the correct structure."""
    mock_data = {
        'reviews': {
            'edges': [{
                'node': {
                    'spoiler': True,
                    'summary': {'originalText': 'Amazing movie with great plot'},
                    'text': {'originalText': {'plaidHtml': '<p>This movie is fantastic...</p>'}},
                    'authorRating': 9,
                    'helpfulness': {
                        'upVotes': 25,
                        'downVotes': 3
                    }
                }
            }]
        }
    }
    
    reviews_list = parse_json_reviews(mock_data)
    
    assert len(reviews_list) == 1
    review_item = reviews_list[0]
    
    # Check that it has the required keys
    expected_keys = ['spoiler', 'summary', 'text', 'authorRating', 'downVotes', 'upVotes']
    for key in expected_keys:
        assert key in review_item
    
    # Check the types and values
    assert review_item['spoiler'] is True
    assert review_item['summary'] == 'Amazing movie with great plot'
    assert review_item['text'] == '<p>This movie is fantastic...</p>'
    assert review_item['authorRating'] == 9
    assert review_item['downVotes'] == 3
    assert review_item['upVotes'] == 25


def test_trivia_item_with_none_values():
    """Test TriviaItem handles None values properly."""
    mock_data = {
        'trivia': {
            'edges': [{
                'node': {
                    'displayableArticle': {},  # Missing body
                    'interestScore': {
                        'usersVoted': 0,
                        'usersInterested': 0
                    }
                }
            }]
        }
    }
    
    trivia_list = parse_json_trivia(mock_data)
    trivia_item = trivia_list[0]
    
    assert trivia_item['body'] is None
    assert trivia_item['interestScore']['usersVoted'] == 0
    assert trivia_item['interestScore']['usersInterested'] == 0


def test_review_item_with_none_values():
    """Test ReviewItem handles None values properly."""
    mock_data = {
        'reviews': {
            'edges': [{
                'node': {
                    'spoiler': None,
                    'summary': None,
                    'text': None,
                    'authorRating': None,
                    'helpfulness': {
                        'upVotes': None,
                        'downVotes': None
                    }
                }
            }]
        }
    }
    
    reviews_list = parse_json_reviews(mock_data)
    review_item = reviews_list[0]
    
    # All values should be None
    assert review_item['spoiler'] is None
    assert review_item['summary'] is None
    assert review_item['text'] is None
    assert review_item['authorRating'] is None
    assert review_item['downVotes'] is None
    assert review_item['upVotes'] is None


def test_empty_trivia_and_reviews():
    """Test parsers handle empty data properly."""
    empty_data = {'trivia': {'edges': []}, 'reviews': {'edges': []}}
    
    trivia_list = parse_json_trivia(empty_data)
    reviews_list = parse_json_reviews(empty_data)
    
    assert trivia_list == []
    assert reviews_list == []


def test_multiple_items():
    """Test parsers handle multiple trivia and review items."""
    mock_data = {
        'trivia': {
            'edges': [
                {
                    'node': {
                        'displayableArticle': {'body': {'plaidHtml': '<p>First trivia</p>'}},
                        'interestScore': {'usersVoted': 10, 'usersInterested': 8}
                    }
                },
                {
                    'node': {
                        'displayableArticle': {'body': {'plaidHtml': '<p>Second trivia</p>'}},
                        'interestScore': {'usersVoted': 20, 'usersInterested': 15}
                    }
                }
            ]
        },
        'reviews': {
            'edges': [
                {
                    'node': {
                        'spoiler': False,
                        'summary': {'originalText': 'First review'},
                        'text': {'originalText': {'plaidHtml': '<p>Good movie</p>'}},
                        'authorRating': 7,
                        'helpfulness': {'upVotes': 5, 'downVotes': 1}
                    }
                },
                {
                    'node': {
                        'spoiler': True,
                        'summary': {'originalText': 'Second review'},
                        'text': {'originalText': {'plaidHtml': '<p>Great movie</p>'}},
                        'authorRating': 8,
                        'helpfulness': {'upVotes': 10, 'downVotes': 0}
                    }
                }
            ]
        }
    }
    
    trivia_list = parse_json_trivia(mock_data)
    reviews_list = parse_json_reviews(mock_data)
    
    assert len(trivia_list) == 2
    assert len(reviews_list) == 2
    
    # Check first trivia
    assert trivia_list[0]['body'] == '<p>First trivia</p>'
    assert trivia_list[0]['interestScore']['usersVoted'] == 10
    
    # Check second trivia
    assert trivia_list[1]['body'] == '<p>Second trivia</p>'
    assert trivia_list[1]['interestScore']['usersVoted'] == 20
    
    # Check first review
    assert reviews_list[0]['summary'] == 'First review'
    assert reviews_list[0]['authorRating'] == 7
    
    # Check second review
    assert reviews_list[1]['summary'] == 'Second review'
    assert reviews_list[1]['authorRating'] == 8