from typing import List, Optional

import numpy as np
from astropy.time import Time
from pydantic import BaseModel, root_validator, validator


def ul_or_inf(limit: Optional[float]) -> float:
    if limit is None:
        return np.inf
    return limit


def ll_or_inf(limit: Optional[float]) -> float:
    if limit is None:
        return -np.inf
    return limit


class TimeType(Time):  # from Gammapy
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v == np.inf:
            return Time(np.iinfo(np.int64).max, format="unix")
        if v == -np.inf:
            return Time(np.iinfo(np.int64).min, format="unix")
        return Time(v)


class Limits(BaseModel):
    ul: Optional[float]
    ll: Optional[float]
    sigma: Optional[float]

    _val_ul = validator("ul", allow_reuse=True)(ul_or_inf)
    _val_ll = validator("ll", allow_reuse=True)(ll_or_inf)

    @classmethod
    @root_validator
    def lower_upper(cls, values):
        ll = values["ll"]
        ul = values["ll"]
        if ll > ul:
            raise ValueError(
                "Lower Limit MUST NOT be larger than Upper Limit, " f"got ({ll}, {ul})",
            )
        return values


class Config(BaseModel):
    source: str
    source_ra_deg: float
    source_dec_deg: float
    pedestal: Limits
    cosmics: Limits
    cosmics_10: Limits
    cosmics_30: Limits

    time_start: Optional[TimeType]
    time_stop: Optional[TimeType]

    always_include: List[int] = []
    never_include: List[int] = []

    _val_time_start = validator("time_start", allow_reuse=True, pre=True)(ll_or_inf)
    _val_time_stop = validator("time_stop", allow_reuse=True, pre=True)(ul_or_inf)

    # # TODO this is only relevant for the data-check
    # @root_validator
    # def warn_if_sigma(cls, values):
    #     for name, cfg in values.items():
    #         if isinstance(cfg, Limits) and cfg.sigma is not None:
    #             log = logging.getLogger('data-check')
    #             log.warning(
    #                 f"{name}.sigma is not None, will calculate new limits.",
    #             )
    #     return values

    class Config:
        json_encoders = {
            Time: lambda t: t.datetime,
        }
