from app.utils.url import canonical_instagram_media_url
from app.services.instagram_native import _unescape_ig_json_url


def test_canonical_strips_igsh_share_param() -> None:
    dirty = 'https://www.instagram.com/reel/DXyjOZbtq68/?igsh=Mnh6djhpNGwwczF1'
    assert canonical_instagram_media_url(dirty) == 'https://www.instagram.com/reel/DXyjOZbtq68/'


def test_canonical_keeps_reel_vs_p() -> None:
    assert canonical_instagram_media_url('https://www.instagram.com/p/DZVOFgQoCoC/').endswith('/p/DZVOFgQoCoC/')
    assert canonical_instagram_media_url('https://www.instagram.com/reel/DZVOFgQoCoC/').endswith('/reel/DZVOFgQoCoC/')


def test_unescape_ig_json_url() -> None:
    raw = r'https:\\/\\/scontent.cdninstagram.com\\/o1\\/v\\/t2\\/clip.mp4'
    assert _unescape_ig_json_url(raw) == 'https://scontent.cdninstagram.com/o1/v/t2/clip.mp4'
