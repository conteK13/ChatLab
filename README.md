# ChatLab

ChatLab은 챗봇 구현의 기본 흐름을 단계별로 학습하기 위한 실습 프로젝트입니다. Streamlit 프론트엔드와 FastAPI 백엔드를 기반으로, LangChain 메시지 호출부터 Tool, Agent, Vector RAG까지 차근차근 확장합니다.

## 시작 방법
1. 이 프로젝트는 `uv sync`로 실행 환경을 준비합니다.
    ```bash
    uv sync
    ```

2. 프로젝트 루트에 `.env` 파일을 만들거나 `.env.example`을 복사한 뒤 값을 설정합니다.

3. 가상환경 실행
    ```powershell
    # powershell
    .\.venv\Scripts\Activate.ps1
    ```

    ```bash
    # Bash(window)
    source .venv/Scripts/activate
    ```

    ```bash
    # Bash / Linux / macOS
    source .venv/bin/activate
    ```

4. 백엔드 실행
    ```bash
    # bash
    uv run uvicorn backend.main:app --reload --port 8000
    ```

5. 프론트엔드 실행
  ```bash
  # bash
  uv run streamlit run frontend/app.py
  ```

## 프로젝트 소개

ChatLab은 “챗봇이 어떻게 외부 기능과 지식을 사용하게 되는가”를 실습으로 이해하는 것을 목표로 합니다. 초기 단계에서는 실행 환경과 화면 구조를 준비하고, 이후 각 단계에서 기능을 하나씩 붙여갑니다.

## 구현 예정 단계

0. 초기설정: 단계별 학습 목표와 실행 환경 준비하기
1. 메시지 전송: LangChain으로 메시지를 전송하고 LangSmith로 실행 추적하기
2. Tool 이해: Tool이 필요한 이유 이해하기
3. Tool 만들기: 시각, 위치, 날씨 Tool을 만들고 연결하기
4. Agent: ReAct 방식으로 챗봇 구현하기
5. RAG 이해: LLM이 외부 문서를 활용해 답변하는 흐름 이해하기
6. Vector RAG 구현: 문서를 벡터로 검색해 답변에 활용하기
