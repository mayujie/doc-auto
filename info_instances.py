from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class CarInfo:
    maker: str
    model: str
    vin_number: str
    start_date: str
    end_date: str
    plate_number: Optional[str] = None


@dataclass
class SectionInfo:
    value: str
    position: Tuple[int, int]


@dataclass
class RegistrationProofInfo:
    section_D: SectionInfo
    section_E: SectionInfo
    section_H: SectionInfo
    section_I: SectionInfo
