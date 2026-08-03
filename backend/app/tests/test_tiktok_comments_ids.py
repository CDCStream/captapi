"""TikTok comments: authorId / authorSecUid / commentLanguage."""
from __future__ import annotations

from app.services.tiktok_native import _map_comment, _map_reply


def test_map_comment_adds_stable_ids_and_language():
    row = _map_comment({
        'cid': '123',
        'text': 'hola mundo',
        'digg_count': 4,
        'create_time': 1717356633,
        'comment_language': 'es',
        'reply_comment_total': 14,
        'user': {
            'uid': '6958917445306926086',
            'sec_uid': 'MS4wLjABAAAA9rB4k_Ei3NexA5p2',
            'unique_id': 'spanish.fan',
            'nickname': 'Fan',
            'language': 'en',
            'avatar_thumb': {'url_list': ['https://example.com/a.jpg']},
        },
    })
    assert row is not None
    assert row['author'] == 'spanish.fan'
    assert row['authorId'] == '6958917445306926086'
    assert row['authorSecUid'].startswith('MS4wLjAB')
    assert row['commentLanguage'] == 'es'
    assert row['replyCount'] == 14
    assert row['likeCount'] == 4


def test_map_comment_falls_back_to_user_language():
    row = _map_comment({
        'cid': '99',
        'text': 'hi',
        'digg_count': 1,
        'create_time': 1717356633,
        'user': {
            'uid': '1',
            'sec_uid': 'MS4',
            'unique_id': 'u',
            'language': 'fr',
            'avatar_thumb': {'url_list': []},
        },
    })
    assert row is not None
    assert row['commentLanguage'] == 'fr'
    assert row['authorId'] == '1'
    assert row['authorSecUid'] == 'MS4'


def test_map_reply_keeps_ids():
    row = _map_reply({
        'cid': '55',
        'text': 'reply',
        'digg_count': 0,
        'create_time': 1717356633,
        'user': {
            'uid': '42',
            'sec_uid': 'MS4reply',
            'unique_id': 'replier',
            'nickname': 'Replier',
            'language': 'de',
            'is_verified': False,
            'avatar_thumb': {'url_list': ['https://x/y.jpg']},
        },
    })
    assert row is not None
    assert row['authorId'] == '42'
    assert row['authorSecUid'] == 'MS4reply'
    assert row['commentLanguage'] == 'de'
