"""Configuration loader for Bedrock or direct Anthropic modes."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    # Mode
    execution_mode: str  # "bedrock" or "anthropic"

    # AWS Bedrock
    aws_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    bedrock_model_id: str
    bedrock_guardrail_id: str
    bedrock_guardrail_version: str
    bedrock_knowledge_base_id: str

    # Anthropic direct
    anthropic_api_key: str
    anthropic_model: str

    # Agent behavior
    llm_temperature: float
    max_agent_iterations: int

    # Observability
    enable_metrics: bool
    log_level: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            execution_mode=os.getenv("EXECUTION_MODE", "anthropic").lower(),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            bedrock_model_id=os.getenv(
                "BEDROCK_MODEL_ID",
                "anthropic.claude-3-5-sonnet-20241022-v2:0",
            ),
            bedrock_guardrail_id=os.getenv("BEDROCK_GUARDRAIL_ID", ""),
            bedrock_guardrail_version=os.getenv("BEDROCK_GUARDRAIL_VERSION", "DRAFT"),
            bedrock_knowledge_base_id=os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            max_agent_iterations=int(os.getenv("MAX_AGENT_ITERATIONS", "5")),
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        if self.execution_mode not in ("bedrock", "anthropic"):
            raise ValueError(
                f"Invalid EXECUTION_MODE: {self.execution_mode}. "
                "Must be 'bedrock' or 'anthropic'."
            )
        if self.execution_mode == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY required when EXECUTION_MODE=anthropic")


config = Config.from_env()
