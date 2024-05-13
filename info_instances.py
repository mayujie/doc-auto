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

    def get_section_d(self):
        section_d = f"D1. {self.maker}\nD2. ...\nD3. {self.model}"
        return section_d


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
