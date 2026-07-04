"""Official Python SDK for the Captapi social media API.

Usage:
    from captapi import Captapi

    client = Captapi(api_key="YOUR_KEY")  # or set CAPTAPI_API_KEY
    result = client.youtube.transcript(url="https://youtube.com/watch?v=...")
    print(result["data"])

Async:
    from captapi import AsyncCaptapi

    async with AsyncCaptapi() as client:
        result = await client.tiktok.profile(url="https://tiktok.com/@user")
"""

from ._generated import AsyncCaptapi, Captapi
from ._transport import DEFAULT_BASE_URL, CaptapiError

__version__ = "0.1.0"
__all__ = ["Captapi", "AsyncCaptapi", "CaptapiError", "DEFAULT_BASE_URL", "__version__"]
