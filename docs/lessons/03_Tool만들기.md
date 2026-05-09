# Tool 만들기

Tool 만들기 단계에서는 LangChain의 `@tool`을 사용해 시간, 위치, 날씨 Tool을 만들고, LLM이 필요할 때 Tool을 호출할 수 있도록 연결합니다. 이번 단계의 핵심은 Tool을 정의하는 것뿐 아니라, LLM이 요청한 Tool을 애플리케이션 코드가 직접 실행하고 그 결과를 다시 LLM에게 전달해야 한다는 점을 이해하는 것입니다.

### 목표

- LangChain `@tool`로 Tool 만들기
- Tool 이름과 설명이 LLM에게 어떤 의미인지 이해하기
- `args_schema`로 Tool 입력값을 명확히 설명하기
- `bind_tools()`로 LLM에게 사용 가능한 Tool 목록 전달하기
- LLM이 만든 Tool call을 애플리케이션에서 실행하기
- Tool 실행 결과를 `ToolMessage`로 다시 LLM에 전달하기
- 단순 Tool calling과 ReAct/Agent 방식의 차이 이해하기

- **완료 기준** : 현재 시간, 현재 위치, 현재 날씨 요청에서 LLM이 Tool을 호출할 수 있고, 애플리케이션이 Tool 결과를 다시 LLM에 전달해 최종 응답을 만들 수 있는 상태입니다. 또한 여러 Tool을 순차적으로 사용해야 하는 상황에서 단순 Tool calling만으로는 흐름 제어가 부족할 수 있음을 설명할 수 있어야 합니다.

---
### 이번 단계에서 만든 Tool

이번 단계에서는 `backend/tools/chat_tools.py`에 세 가지 Tool을 만듭니다.

- `get_current_time` : 현재 서버 기준 시간을 반환합니다.
- `get_current_location` : 학습용 기본 위치인 `서울, 대한민국`을 반환합니다.
- `get_weather` : 입력받은 장소의 현재 날씨를 반환합니다.

날씨 Tool은 아직 실제 기상청 API에 연결하지 않습니다. 이번 단계에서는 외부 API 연동보다 "LLM이 Tool을 선택하고, 애플리케이션이 실행 결과를 다시 넘겨주는 흐름"을 이해하는 데 집중합니다.

---
### Tool 설명이 중요한 이유

Tool은 단순한 Python 함수가 아니라, LLM이 사용할 수 있도록 설명이 붙은 함수입니다.

```python
@tool(
    "get_weather",
    args_schema=WeatherInput,
    description="입력받은 장소의 현재 날씨를 알려줍니다. 장소를 입력해야 합니다.",
)
def get_weather(location: str) -> str:
    ...
```

LLM은 함수의 구현 코드를 직접 읽고 판단하지 않습니다. 대신 Tool 이름, description, 입력 스키마를 보고 어떤 상황에서 어떤 Tool을 호출할지 결정합니다.

그래서 description은 "개발자용 주석"이라기보다 "LLM에게 알려주는 사용 설명서"에 가깝습니다.

---
### `args_schema`의 역할

날씨 Tool은 장소 입력이 필요합니다. 이때 `args_schema`를 사용하면 Tool이 어떤 입력을 받아야 하는지 더 명확히 표현할 수 있습니다.

```python
class WeatherInput(BaseModel):
    location: str = Field(..., description="날씨를 확인할 장소입니다. 예: 서울, 부산, 제주")
```

이 정보는 LLM이 Tool call을 만들 때 참고하는 입력 스키마가 됩니다. LangSmith에서도 Tool의 파라미터 이름, 타입, 필수 여부 같은 정보를 확인할 수 있습니다.

이번 예제에서는 `location`만 받습니다. 사용자가 "부산 날씨 알려줘"라고 말하면 LLM은 `location`에 `부산`을 넣어 `get_weather` Tool을 호출할 수 있습니다.

---
### LLM에게 Tool 전달하기

Tool을 만들기만 해서는 LLM이 Tool의 존재를 알 수 없습니다. 사용 가능한 Tool 목록을 LLM에게 전달해야 합니다.

```python
tools = get_chatlab_tools()
tool_call_llm = ChatOpenAI(model=settings.openai_model).bind_tools(tools)
```

`bind_tools()`는 LLM이 호출할 수 있는 Tool 목록과 스키마를 함께 전달합니다. 이 상태에서 사용자가 "현재 시간을 알려줘"라고 물어보면, LLM은 일반 텍스트 답변 대신 `get_current_time` Tool call을 만들 수 있습니다.

---
### Tool call은 실행이 아니다

중요한 점은 LLM이 Tool call을 만들었다고 해서 Tool이 자동으로 실행되는 것은 아니라는 점입니다.

이번 단계의 흐름은 다음과 같습니다.

```text
사용자 메시지
  -> Tool 목록이 연결된 LLM 호출
  -> LLM이 Tool call 생성
  -> 애플리케이션이 Tool call을 읽고 실제 Tool 실행
  -> Tool 결과를 ToolMessage로 추가
  -> 일반 LLM이 최종 응답 생성
```

`backend/services/llm_service.py`에서는 LLM 응답의 `tool_calls`를 확인하고, 호출된 Tool 이름에 맞는 Tool을 직접 실행합니다.

```python
for tool_call in response.tool_calls:
    tool_name = tool_call["name"]
    selected_tool = tools_by_name[tool_name]
    tool_result = selected_tool.invoke(tool_call["args"])
```

그 다음 Tool 결과를 `ToolMessage`로 만들어 메시지 목록에 추가합니다.

```python
ToolMessage(
    content=str(tool_result),
    tool_call_id=tool_call["id"],
)
```

마지막으로 Tool이 없는 일반 LLM을 한 번 더 호출해 사용자가 읽을 수 있는 최종 답변을 만듭니다.

---
### 왜 두 번 호출하는가

첫 번째 LLM 호출은 "어떤 Tool을 써야 하는가"를 결정합니다. 이때 LLM은 자연어 답변 대신 Tool call을 만들 수 있습니다.

두 번째 LLM 호출은 "Tool 결과를 사용자에게 어떻게 설명할 것인가"를 담당합니다. Tool 결과는 보통 함수 실행 결과이기 때문에, 사용자에게 보여줄 자연스러운 문장으로 정리하는 과정이 필요합니다.

이번 단계에서는 두 번째 호출에 Tool을 연결하지 않습니다. 두 번째 호출에도 Tool을 연결하면 모델이 다시 Tool call을 만들 수 있고, 그러면 최종 응답이 비어 보이거나 기대한 답변이 나오지 않을 수 있습니다.

---
### 직접 확인하기

`http/tool_message.http`에는 Tool 호출을 확인하기 위한 요청 예시가 들어 있습니다.

백엔드를 실행합니다.

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

그 다음 VS Code REST Client 같은 도구에서 다음 요청을 실행합니다.

- `Ask Current Time Without Tool`
- `Ask Current Location With Tools`
- `Ask Weather With Tools`

요청 이름에는 이전 단계와 비교하기 위한 표현이 남아 있지만, 현재 코드에서는 `/chat/message`에 Tool 목록이 연결되어 있습니다. 따라서 같은 "현재 시간을 알려줘" 요청도 이제는 LLM이 `get_current_time` Tool call을 만들 수 있습니다.

LangSmith에서는 다음을 확인합니다.

- LLM 입력에 Tool 목록이 전달되었는가
- 어떤 Tool이 호출되었는가
- Tool call의 입력값은 무엇인가
- Tool 실행 결과가 다시 LLM에 전달되었는가
- 최종 LLM 응답은 어떻게 생성되었는가

---
### 단순 Tool calling의 한계

이번 구현은 Tool call을 한 번 처리하고 최종 답변을 만드는 단순한 구조입니다. 현재 시간처럼 하나의 Tool만 필요한 질문에는 잘 맞습니다.

하지만 사용자가 다음처럼 질문하면 흐름이 더 복잡해질 수 있습니다.

```text
지금 날씨 알려줘.
```

이 질문에는 장소가 들어 있지 않습니다. 이상적인 흐름은 다음과 같습니다.

```text
1. 현재 위치를 확인한다.
2. 확인한 위치로 날씨를 조회한다.
3. 날씨 결과를 사용자에게 답한다.
```

즉 `get_current_location`을 호출한 뒤, 그 결과를 사용해 다시 `get_weather`를 호출해야 합니다. 이런 식으로 여러 Tool을 순차적으로 사용하려면 단순히 한 번 Tool call을 처리하는 구조만으로는 부족할 수 있습니다.

이 문제를 직접 반복문으로 해결할 수도 있지만, 다음 단계에서는 ReAct/Agent 방식을 사용해 "생각하기, Tool 선택, 실행 결과 반영, 다시 판단하기" 흐름을 더 자연스럽게 다룹니다.

---
### 왜 Tool 호출을 계속 반복하지 않는가

LLM이 Tool call을 만들 때마다 Tool을 실행하고, 그 결과를 다시 LLM에게 전달하는 반복문을 만들 수도 있습니다. 그러면 모델이 추가 Tool이 필요하다고 판단할 때 여러 번 Tool을 사용할 수 있습니다.

하지만 이 반복문은 반드시 종료 조건이 필요합니다. LLM이 몇 번 Tool을 호출할지는 미리 알 수 없고, 경우에 따라 같은 Tool을 같은 입력으로 반복 호출할 수도 있습니다.

또한 반복 Tool 호출을 직접 구현하기 시작하면 다음과 같은 실행 정책을 애플리케이션이 직접 정해야 합니다.

- Tool을 최대 몇 번까지 호출할 것인가
- 같은 Tool을 같은 입력으로 반복 호출할 때 어떻게 막을 것인가
- Tool 실행 중 오류가 발생하면 어떻게 복구할 것인가
- 여러 Tool 결과 중 어떤 정보를 최종 답변에 사용할 것인가
- Tool 호출 과정이 길어질 때 비용과 응답 시간을 어떻게 제한할 것인가

즉, 반복 Tool 호출 루프를 안정적으로 만들려면 단순한 메시지 전송 코드를 넘어서 Agent 실행 흐름을 직접 관리해야 합니다.

그래서 이번 단계에서는 Tool call을 한 번 실행하고 결과를 다시 LLM에 전달하는 가장 작은 구조까지만 다룹니다. 다음 단계에서는 ReAct/Agent를 사용해 Tool 선택, 실행, 관찰, 다음 판단을 반복하는 흐름을 더 체계적으로 다룹니다.

---
### 자주 묻는 질문
#### Tool을 호출하지 않는 질문도 답변되는가

네. LLM이 Tool이 필요 없다고 판단하면 `tool_calls`가 비어 있고, 기존처럼 LLM의 일반 응답을 그대로 반환합니다.

---
#### Tool 결과를 왜 바로 사용자에게 반환하지 않는가

Tool 결과는 함수 실행 결과입니다. 그대로 보여줘도 되는 경우가 있지만, 사용자가 자연스럽게 읽을 수 있는 답변으로 정리하려면 LLM에게 Tool 결과를 다시 전달해 최종 문장을 생성하는 편이 좋습니다.

---
#### 현재 위치는 실제 사용자 위치인가

아닙니다. 이번 단계의 `get_current_location`은 학습용으로 항상 `서울, 대한민국`을 반환합니다.

IP나 브라우저 위치 권한을 사용하면 실제 위치를 추정할 수도 있지만, 정확도와 개인정보 이슈가 있고 구현 범위도 커집니다. 이번 단계에서는 ReAct 전환을 설명하기 위한 기본 위치 Tool로만 사용합니다.

---
#### 날씨는 실제 날씨인가

아닙니다. 이번 단계의 `get_weather`는 학습용 예시 응답을 반환합니다. 실제 기상청 API 연동은 지역명과 좌표 변환, 발표 시간 계산, API 키 관리 같은 주제가 추가되므로 별도 단계에서 다루는 것이 좋습니다.
