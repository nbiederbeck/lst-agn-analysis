from typing import Union

from pydantic import BaseModel


class Config(BaseModel):
    source: str
    pedestal_ul: Union[float, None]
    pedestal_ll: Union[float, None]
    pedestal_sigma: Union[int, None]
    cosmics_ul: Union[float, None]
    cosmics_ll: Union[float, None]
    cosmics_sigma: Union[int, None]
    cosmics_10_ul: Union[float, None]
    cosmics_10_ll: Union[float, None]
    cosmics_10_sigma: Union[int, None]
    cosmics_30_ul: Union[float, None]
    cosmics_30_ll: Union[float, None]
    cosmics_30_sigma: Union[int, None]
