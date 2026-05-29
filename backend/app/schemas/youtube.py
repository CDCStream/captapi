"""YouTube response schemas."""

from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float
    timestamp: str


class YouTubeTranscript(BaseModel):
    url: str
    title: str | None = None
    transcript: str
    transcriptSegments: list[TranscriptSegment]
    wordCount: int
    segments: int
    language: str | None = None


class YouTubeSummary(BaseModel):
    url: str
    title: str | None = None
    summary: str
    keyPoints: list[str]
    topics: list[str]
    sentiment: str | None = None


class YouTubeVideoDetails(BaseModel):
    url: str
    id: str
    title: str
    description: str | None = None
    channelName: str | None = None
    channelId: str | None = None
    channelUrl: str | None = None
    publishedAt: str | None = None
    durationSeconds: int | None = None
    viewCount: int | None = None
    likeCount: int | None = None
    commentCount: int | None = None
    thumbnailUrl: str | None = None
    tags: list[str] = []


class YouTubeComment(BaseModel):
    id: str | None = None
    author: str | None = None
    text: str
    likeCount: int | None = None
    publishedAt: str | None = None
    replyCount: int | None = None


class YouTubeComments(BaseModel):
    url: str
    totalReturned: int
    comments: list[YouTubeComment]


class YouTubeChannelDetails(BaseModel):
    url: str
    id: str | None = None
    name: str
    description: str | None = None
    subscriberCount: int | None = None
    videoCount: int | None = None
    viewCount: int | None = None
    thumbnailUrl: str | None = None
    bannerUrl: str | None = None
    country: str | None = None


class YouTubeSearchResult(BaseModel):
    url: str
    title: str
    channelName: str | None = None
    viewCount: int | None = None
    publishedAt: str | None = None
    thumbnailUrl: str | None = None
    durationSeconds: int | None = None
