from epg_grabber.constants import EPG_GENERATOR, EPG_XMLTV_TIMEFORMAT
from pydantic import BaseModel, Field, validator
from datetime import datetime
from string import punctuation
from typing import List, Optional, Union, Dict
from pytz import timezone


class Channel(BaseModel):
    id: str = Field(alias="@id")
    display_name: Union[str, Dict] = Field(alias="display-name")
    xml_id: Optional[str] = None  # Store the Tag (HDT) value
    channel_id: Optional[str] = None  # Store the original numeric channel ID
    icon: Union[str, Dict]
    url: str = Field(default="https://dstv.com")

    class Config:
        allow_population_by_field_name = True

    @validator("id", pre=True)
    def tvg_id_sanitize(cls, value):
        value = [value.replace(char, "")
                 for char in punctuation if char != "."][0]
        value = value.replace(" ", "")
        return value.lower()

    @validator("xml_id", pre=True)
    def use_xml_id(cls, value, values):
        return value.upper() if value else None

    @validator("display_name")
    def lang_dict(cls, value):
        if isinstance(value, Dict):
            value = value["#text"]

        return dict({"@lang": "en", "#text": value.strip()})

    @validator("icon")
    def icon_str(cls, value):
        if isinstance(value, Dict):
            value = value["@src"]

        return dict({"@src": value})


class ChannelMetadata(BaseModel):
    channels: List[Channel]


class Programme(BaseModel):
    start: datetime = Field(alias="@start")
    stop: datetime = Field(alias="@stop")
    channel: str = Field(alias="@channel")
    title: str
    desc: Optional[str]
    episode: Optional[str]
    category: Optional[str]
    rating: Optional[str]

    class Config:
        allow_population_by_field_name = True

    @validator("start", "stop")
    def xmltv_datetime_string(cls, value):

        if not value.tzinfo:
            utc = timezone('utc')
            value = utc.localize(value)
        
        xmltv_string = value.strftime(EPG_XMLTV_TIMEFORMAT)
        return xmltv_string

    @validator("title", "desc")
    def lang_dict(cls, value: str):
        if not value:
            value = ''

        return dict({"@lang": "en", "#text": value.strip()})


class TvDataItem(BaseModel):
    generator: str = Field(default=EPG_GENERATOR, alias="@generator-info-name")
    channel: List[Channel]
    programme: List[Programme]


class TvData(BaseModel):
    tv: TvDataItem


class InputConfigItem(BaseModel):
    site: str
    channels: List[str]


class InputConfig(BaseModel):
    days: Optional[int]
    configs: List[InputConfigItem]
    workers: Optional[int]
