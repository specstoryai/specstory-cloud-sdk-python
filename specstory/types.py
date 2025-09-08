"""Type definitions for SpecStory SDK

This file will be replaced by auto-generated types from OpenAPI
"""

from typing import TypedDict, Optional, List, Dict, Any


class ProjectDict(TypedDict, total=False):
    """Project type definition"""
    id: str
    name: str
    ownerId: str
    icon: str
    color: str
    createdAt: str
    updatedAt: str


class SessionMetadataDict(TypedDict, total=False):
    """Session metadata"""
    clientName: Optional[str]
    clientVersion: Optional[str]
    agentName: Optional[str]
    deviceId: Optional[str]
    gitBranches: Optional[List[str]]
    llmModels: Optional[List[str]]
    tags: Optional[List[str]]


class SessionDict(TypedDict, total=False):
    """Session type definition"""
    id: str
    projectId: str
    name: str
    markdownContent: str
    markdownSize: int
    rawDataSize: int
    metadata: SessionMetadataDict
    createdAt: str
    updatedAt: str
    startedAt: Optional[str]
    endedAt: Optional[str]
    etag: Optional[str]