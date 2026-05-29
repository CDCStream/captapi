"""Generic schemas shared across TikTok / Instagram / Facebook."""

from pydantic import BaseModel


class SocialAuthor(BaseModel):
    username: str | None = None
    displayName: str | None = None
    url: str | None = None
    followers: int | None = None
    verified: bool | None = None
    profileImage: str | None = None


class SocialEngagement(BaseModel):
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    saves: int | None = None


class SocialVideoDetails(BaseModel):
    platform: str
    url: str
    id: str | None = None
    caption: str | None = None
    description: str | None = None
    publishedAt: str | None = None
    durationSeconds: float | None = None
    thumbnailUrl: str | None = None
    videoUrl: str | None = None
    author: SocialAuthor | None = None
    engagement: SocialEngagement | None = None
    hashtags: list[str] = []
    musicName: str | None = None


class SocialComment(BaseModel):
    id: str | None = None
    text: str
    author: str | None = None
    likeCount: int | None = None
    publishedAt: str | None = None
    replyCount: int | None = None


class SocialComments(BaseModel):
    platform: str
    url: str
    totalReturned: int
    comments: list[SocialComment]


class SocialChannelDetails(BaseModel):
    platform: str
    url: str
    username: str | None = None
    displayName: str | None = None
    bio: str | None = None
    followers: int | None = None
    following: int | None = None
    postCount: int | None = None
    verified: bool | None = None
    profileImage: str | None = None
    externalUrl: str | None = None


class SocialSearchResult(BaseModel):
    platform: str
    url: str
    caption: str | None = None
    author: str | None = None
    publishedAt: str | None = None
    thumbnailUrl: str | None = None
    engagement: SocialEngagement | None = None
