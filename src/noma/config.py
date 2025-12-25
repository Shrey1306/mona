"""Configuration management for Noma."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Neo4jConfig:
    url: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "Neo4jConfig":
        return cls(
            url=os.environ.get("NEO4J_URL", "neo4j://localhost:7687"),
            user=os.environ.get("NEO4J_USER", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", ""),
        )


@dataclass
class AWSConfig:
    access_key: str
    secret_key: str
    region: str
    bucket: str

    @classmethod
    def from_env(cls) -> "AWSConfig":
        return cls(
            access_key=os.environ.get("AWS_ACCESS_KEY_ID", ""),
            secret_key=os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
            region=os.environ.get("AWS_REGION", "us-east-1"),
            bucket=os.environ.get("AWS_S3_BUCKET", ""),
        )


@dataclass
class AppConfig:
    neo4j: Neo4jConfig
    aws: AWSConfig
    openai_api_key: str
    debug: bool
    host: str
    port: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            neo4j=Neo4jConfig.from_env(),
            aws=AWSConfig.from_env(),
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            debug=os.environ.get("DEBUG", "false").lower() == "true",
            host=os.environ.get("HOST", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5001")),
        )


def get_config() -> AppConfig:
    return AppConfig.from_env()

