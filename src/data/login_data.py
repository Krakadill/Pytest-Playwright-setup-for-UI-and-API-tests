import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# src/data/login_data.py -> parents[2] is the project root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class Credentials:
    email: str
    password: str


CREDENTIALS = Credentials(
    email=os.environ["EMAIL"],
    password=os.environ["PASSWORD"],
)