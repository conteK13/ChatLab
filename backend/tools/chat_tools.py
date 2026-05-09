from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.tools import tool
from pydantic import BaseModel, Field

DEFAULT_TIMEZONE = "Asia/Seoul"
DEFAULT_LOCATION = "서울, 대한민국"


class WeatherInput(BaseModel):
    location: str = Field(..., description="날씨를 확인할 장소입니다. 예: 서울, 부산, 제주")


@tool(
    "get_current_time",
    description=(
        "현재 서버 기준 시간을 알려줍니다. "
        "별도의 입력은 필요하지 않습니다."
    ),
)
def get_current_time() -> str:
    now = datetime.now(ZoneInfo(DEFAULT_TIMEZONE))
    return now.strftime(f"현재 시간은 %Y-%m-%d %H:%M:%S ({DEFAULT_TIMEZONE})입니다.")


@tool(
    "get_current_location",
    description=(
        "현재 학습 예제에서 사용하는 기본 장소를 알려줍니다. "
        "별도의 입력은 필요하지 않습니다."
    ),
)
def get_current_location() -> str:
    return f"현재 장소는 {DEFAULT_LOCATION}입니다."


@tool(
    "get_weather",
    args_schema=WeatherInput,
    description="입력받은 장소의 현재 날씨를 알려줍니다. 장소를 입력해야 합니다.",
)
def get_weather(location: str) -> str:
    return (
        f"{location}의 현재 날씨는 학습용 예시로 '맑음, 기온 22도'입니다. "
        "아직 실제 날씨 API에는 연결되어 있지 않습니다."
    )


CHATLAB_TOOLS = [get_current_time, get_current_location, get_weather]


def get_chatlab_tools():
    return CHATLAB_TOOLS.copy()
