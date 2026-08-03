"""Facebook comments reaction mapping tests."""
from __future__ import annotations

from app.services import facebook_comments_native as n


def test_reactions_from_top_reactions_edges():
    feedback = {
        'reactors': {'count_reduced': '95'},
        'top_reactions': {
            'edges': [
                {'node': {'id': '1635855486666999'}, 'reaction_count': 79},
                {'node': {'id': '478547315650144'}, 'reaction_count': 11},
                {'node': {'id': '1678524932434102'}, 'reaction_count': 4},
                {'node': {'id': '115940658764963'}, 'reaction_count': 1},
            ]
        },
    }
    total, reactions = n.reactions_from_feedback(feedback)
    assert total == 95
    assert reactions['like'] == 79
    assert reactions['wow'] == 11
    assert reactions['love'] == 4
    assert reactions['haha'] == 1
    assert reactions['anger'] == 0
    assert set(reactions) == set(n._REACTION_KEYS)


def test_map_comment_author_id_and_reactions():
    node = {
        'legacy_fbid': '1003271445544158',
        'created_time': 1717356633,
        'depth': 0,
        'body': {'text': 'how is this different from JWST?'},
        'author': {
            'id': 'pfbid02SdzVLPYTHY2eGMdrwFrLw54sVZdguAGnLUj4RPL3HxFtG2D4PBBjptiMEwpB21Ehl',
            'name': 'Robin Bergsagel',
            'gender': 'FEMALE',
            'url': None,
        },
        'feedback': {
            'id': 'ZmVlZGJhY2s6MTU0MTc1MzUyMzk4NjY4NV8xMDAzMjcxNDQ1NTQ0MTU4',
            'url': 'https://www.facebook.com/NASA/posts/x?comment_id=1003271445544158',
            'reactors': {'count_reduced': '7'},
            'top_reactions': {
                'edges': [{'node': {'id': '1635855486666999'}, 'reaction_count': 7}]
            },
            'replies_fields': {'total_count': 6, 'count': 1},
        },
    }
    row = n._map_comment(node, include_reply_count=True)
    assert row is not None
    assert row['author']['id'].startswith('pfbid')
    assert row['author']['name'] == 'Robin Bergsagel'
    assert row['author']['gender'] == 'FEMALE'
    assert row['author']['shortName'] == 'Robin'
    assert row['likeCount'] == 7
    assert row['reactionCount'] == 7
    assert row['reactions']['like'] == 7
    assert row['replyCount'] == 6
    assert row['authorUrl'] is None


def test_resolve_comments_url_from_feedback_id():
    fid = n._b64_encode('feedback:1447656323383848')
    url = n.resolve_comments_url(url=None, feedback_id=fid)
    assert url == 'https://www.facebook.com/1447656323383848'
    assert n.feedback_post_id(fid) == '1447656323383848'


def test_post_feedback_id_from_comment_feedback():
    comment_fid = n._b64_encode('feedback:1541753523986685_1003271445544158')
    post_fid = n.post_feedback_id_from_comment_feedback(comment_fid)
    assert post_fid is not None
    assert n.feedback_post_id(post_fid) == '1541753523986685'
