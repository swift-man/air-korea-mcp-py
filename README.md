# air-korea-mcp

한국환경공단 에어코리아 OpenAPI를 MCP 서버로 감싼 최소 파이썬 예제입니다.

대상 데이터셋:
- 공공데이터포털 `한국환경공단_에어코리아_대기오염정보`
- 문서: <https://www.data.go.kr/data/15073861/openapi.do>

구현된 MCP 도구:
- `get_air_quality_forecast`
- `get_pm25_weekly_forecast`
- `get_station_measurements`
- `get_bad_khai_stations`
- `get_sido_measurements`

추가 리소스:
- `airkorea://reference`

## 왜 MCP 서버로 만들기 쉬운가

이 API는 다음 특성 때문에 MCP 도구로 감싸기 적합합니다.

- REST 기반입니다.
- JSON 응답을 지원합니다.
- 기능 경계가 분명합니다.
- 인증이 단순한 서비스키 방식입니다.

즉, MCP 도구 하나를 OpenAPI 오퍼레이션 하나에 거의 1:1로 대응시킬 수 있습니다.

## 전제 조건

- Python `3.10+`
- 공공데이터포털에서 발급한 서비스키
- 개발계정 호출 한도와 이용 조건 준수

공식 MCP Python SDK v1.x는 Python `>=3.10`을 요구합니다. 현재 저장소에 있는 코드는 그 기준에 맞춰 작성했습니다.

## 구조

SOLID 관점에서 책임을 다음처럼 나눴습니다.

- `settings.py`: 환경 변수와 런타임 설정 로딩
- `validation.py`: 입력 검증
- `gateway.py`: HTTP 전송과 Air Korea 응답 정규화
- `service.py`: MCP 도구가 호출하는 유스케이스 계층
- `server.py`: MCP 도구 등록

즉 서버 계층은 구체적인 HTTP 구현보다 서비스 추상화에 의존하고, 서비스는 게이트웨이를 주입받도록 분리했습니다.

## 환경 변수

둘 중 하나만 설정하면 됩니다.

- `AIR_KOREA_SERVICE_KEY`: 디코딩된 원본 서비스키
- `AIR_KOREA_SERVICE_KEY_ENCODED`: 이미 URL 인코딩된 서비스키

선택 항목:

- `AIR_KOREA_API_BASE`: 기본값 `https://apis.data.go.kr/B552584/ArpltnInforInqireSvc`
- `AIR_KOREA_TIMEOUT_SECONDS`: 기본값 `15`
- `AIR_KOREA_MCP_TRANSPORT`: 기본값 `streamable-http`
- `AIR_KOREA_MCP_HOST`: 기본값 `127.0.0.1`
- `AIR_KOREA_MCP_PORT`: 기본값 `8000`
- `AIR_KOREA_MCP_PATH`: 기본값 `/mcp`

예시:

```bash
export AIR_KOREA_SERVICE_KEY='your-decoded-service-key'
```

Streamable HTTP 기본 접속 주소:

```text
http://127.0.0.1:8000/mcp
```

## 설치

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .
```

리눅스에서 `git pull` 후 바로 설치하려면:

```bash
./scripts/setup_linux.sh
```

## 실행

기본 실행은 Streamable HTTP transport 입니다.

```bash
./scripts/run_http.sh
```

또는:

```bash
AIR_KOREA_MCP_TRANSPORT=streamable-http python -m air_korea_mcp
```

기본 엔드포인트:

```text
http://127.0.0.1:8000/mcp
```

예를 들어 Claude Code에서는:

```bash
claude mcp add --transport http air-korea http://127.0.0.1:8000/mcp
```

stdio가 필요하면 별도 스크립트를 사용합니다.

```bash
./scripts/run_stdio.sh
```

`.env` 파일이 있으면 `scripts/run_http.sh`와 `scripts/run_stdio.sh`가 함께 읽습니다.

`.env` 예시는 [.env.example](/Users/kim_seung_jin/개발/air-korea-mcp-py/.env.example)에 있습니다.

중요:
- `scripts/run_stdio.sh`는 사람이 터미널에서 직접 쓰는 CLI가 아닙니다.
- MCP 클라이언트가 stdio로 붙어야 합니다.
- 일반 터미널에서 실행 후 Enter를 누르면 빈 줄이 stdin으로 들어가서 `Invalid JSON: EOF while parsing a value` 같은 오류가 납니다.

## 테스트

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Claude Desktop / Codex 예시

```json
{
  "mcpServers": {
    "air-korea": {
      "command": "air-korea-mcp",
      "env": {
        "AIR_KOREA_SERVICE_KEY": "your-decoded-service-key"
      }
    }
  }
}
```

## 도구 설명

### `get_air_quality_forecast`

대기질(미세먼지/오존) 예보통보 조회입니다.

- `inform_code`: `PM10`, `PM25`, `O3`
- `search_date`: `YYYY-MM-DD`

### `get_pm25_weekly_forecast`

초미세먼지 주간예보 조회입니다.

- `search_date`: `YYYY-MM-DD`

### `get_station_measurements`

측정소별 실시간 측정정보 조회입니다.

- `station_name`: 예: `종로구`
- `data_term`: `DAILY`, `MONTH`, `3MONTH`

### `get_bad_khai_stations`

통합대기환경지수 나쁨 이상 측정소 목록조회입니다.

### `get_sido_measurements`

시도별 실시간 측정정보 조회입니다.

- `sido_name`: `전국`, `서울`, `부산`, `대구`, `인천`, `광주`, `대전`, `울산`, `경기`, `강원`, `충북`, `충남`, `전북`, `전남`, `경북`, `경남`, `제주`, `세종`

## 주의 사항

- 공공데이터포털 문서에는 요청 URL이 `http`로 표기되어 있지만, 실제 호출은 `https`로도 동작합니다.
- 서비스키가 없으면 게이트웨이는 `401 Unauthorized`를 반환할 수 있습니다.
- `station_name`은 공식 측정소명을 정확히 넣는 편이 안전합니다.
- LLM이 같은 요청을 반복 호출할 수 있으므로, 실제 운영용 서버에는 캐시와 호출 제한 보호막을 추가하는 편이 좋습니다.
