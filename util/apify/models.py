from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any


@dataclass
class ExternalUrl:
    """Represents an external URL link in a profile's biography."""

    title: str
    lynx_url: str
    url: str
    link_type: str


@dataclass
class Profile:
    """Represents an Instagram profile."""

    inputUrl: str
    id: str
    username: str
    url: str
    fullName: str
    biography: str
    externalUrls: List[ExternalUrl] = field(default_factory=list)
    externalUrl: Optional[str] = None
    externalUrlShimmed: Optional[str] = None
    followersCount: int = 0
    followsCount: int = 0
    hasChannel: bool = False
    highlightReelCount: int = 0
    isBusinessAccount: bool = False
    joinedRecently: bool = False
    businessCategoryName: Optional[str] = None
    private: bool = False
    verified: bool = False
    profilePicUrl: Optional[str] = None
    profilePicUrlHD: Optional[str] = None
    igtvVideoCount: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
        """Create a Profile instance from a dictionary."""
        external_urls = []
        if "externalUrls" in data and data["externalUrls"]:
            external_urls = [
                ExternalUrl(
                    title=url.get("title", ""),
                    lynx_url=url.get("lynx_url", ""),
                    url=url.get("url", ""),
                    link_type=url.get("link_type", ""),
                )
                for url in data["externalUrls"]
            ]

        return cls(
            inputUrl=data.get("inputUrl", ""),
            id=data.get("id", ""),
            username=data.get("username", ""),
            url=data.get("url", ""),
            fullName=data.get("fullName", ""),
            biography=data.get("biography", ""),
            externalUrls=external_urls,
            externalUrl=data.get("externalUrl"),
            externalUrlShimmed=data.get("externalUrlShimmed"),
            followersCount=data.get("followersCount", 0),
            followsCount=data.get("followsCount", 0),
            hasChannel=data.get("hasChannel", False),
            highlightReelCount=data.get("highlightReelCount", 0),
            isBusinessAccount=data.get("isBusinessAccount", False),
            joinedRecently=data.get("joinedRecently", False),
            businessCategoryName=data.get("businessCategoryName"),
            private=data.get("private", False),
            verified=data.get("verified", False),
            profilePicUrl=data.get("profilePicUrl"),
            profilePicUrlHD=data.get("profilePicUrlHD"),
            igtvVideoCount=data.get("igtvVideoCount", 0),
        )


@dataclass
class Post:
    """Represents an Instagram post."""

    id: str
    type: str
    shortCode: str
    caption: str
    url: str
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    commentsCount: int = 0
    firstComment: Optional[str] = None
    dimensionsHeight: int = 0
    dimensionsWidth: int = 0
    displayUrl: Optional[str] = None
    images: List[str] = field(default_factory=list)
    alt: Optional[str] = None
    likesCount: int = 0
    timestamp: Optional[datetime] = None
    ownerUsername: Optional[str] = None
    ownerUrl: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Post":
        """Create a Post instance from a dictionary."""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            shortCode=data.get("shortCode", ""),
            caption=data.get("caption", ""),
            url=data.get("url", ""),
            hashtags=data.get("hashtags", []),
            mentions=data.get("mentions", []),
            commentsCount=data.get("commentsCount", 0),
            firstComment=data.get("firstComment"),
            dimensionsHeight=data.get("dimensionsHeight", 0),
            dimensionsWidth=data.get("dimensionsWidth", 0),
            displayUrl=data.get("displayUrl"),
            images=data.get("images", []),
            alt=data.get("alt"),
            likesCount=data.get("likesCount", 0),
            timestamp=datetime.fromisoformat(data.get("timestamp")) if data.get("timestamp") else None,
            ownerUsername=data.get("ownerUsername"),
            ownerUrl=data.get("ownerUrl"),
        )
