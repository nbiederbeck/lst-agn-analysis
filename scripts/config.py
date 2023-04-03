from typing import Union

from astropy.time import Time
from pydantic import BaseModel


class TimeType(Time):  # from Gammapy
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return Time(v)


class Config(BaseModel):
    source: str
    source_ra_deg: float
    source_dec_deg: float
    pedestal_ul: float
    pedestal_ll: float
    pedestal_sigma: Union[int, None]
    cosmics_ul: float
    cosmics_ll: float
    cosmics_sigma: Union[int, None]
    cosmics_10_ul: float
    cosmics_10_ll: float
    cosmics_10_sigma: Union[int, None]
    cosmics_30_ul: float
    cosmics_30_ll: float
    cosmics_30_sigma: Union[int, None]
    time_start: Union[TimeType, None]
    time_stop: Union[TimeType, None]
