# Open Sillok 참여 안내

조선왕조실록의 한문 원문을 한 기사씩 영어로 번역하고, 공개 PR과 검수를 통해 함께 개선하는 프로젝트입니다. 자기 AI 계정이나 로컬 모델을 가져와 작업할 수 있습니다.

처음에는 짧은 기사 한 건을 골라 주세요. 사이트의 기여 화면에서 원문·출처·번역 틀·작업 지침이 담긴 JSON 파일을 받을 수 있습니다. [공개 GitHub 저장소](https://github.com/nakosung/open-sillok)에서 같은 기사에 열린 이슈와 PR이 있는지 확인하고 작업 이슈를 만듭니다. 다운로드만으로 기사가 예약되지는 않습니다.

AI에는 `AGENTS.md`, `docs/translation-guide.md`, `docs/glossary.md`, 작업 파일을 함께 전달합니다. 원문의 모든 절, 숫자, 부정 표현, 발언 주체와 날짜를 확인하고, 불확실한 해석은 별도 주석에 남깁니다. 기존 국역문이나 공식 영문 번역을 복사하지 않습니다.

Python 3.11 이상이 있다면 다음 순서로 작업합니다. `YOUR_GITHUB_HANDLE`과 `YOUR_MODEL`은 실제 자신의 정보로 바꿉니다.

```sh
python3 scripts/work.py start kca_10401007_002 --contributor YOUR_GITHUB_HANDLE --model YOUR_MODEL
```

`.work/kca_10401007_002/translation.json`을 완성한 뒤:

```sh
python3 scripts/work.py check kca_10401007_002
python3 scripts/work.py apply kca_10401007_002
python3 scripts/check-content.py
```

생성된 `content/en/kca/kca_10401007_002.json`만 커밋하여 PR을 제출합니다. 첫 PR은 한 기사, 이후에도 최대 다섯 기사로 제한합니다. 영어를 다듬는 작업과 한문 원문 전체를 검수하는 작업은 구분합니다. AI 자기 검토와 자동 검사 통과는 독립적인 사람의 검수를 뜻하지 않습니다.

기여자와 사용 모델을 기록하고, 기존 기여자의 표기를 보존합니다. 새 영문 기여물은 권리가 존재하고 기여자가 보유하는 범위에서 CC BY-SA 4.0, 코드와 문서는 MIT로 제공합니다. 원문과 공식 번역의 권리를 프로젝트가 다시 정하지 않습니다.

저장소 운영 및 외부 자동 배포 연결 안내는 `docs/launch.md`에 있습니다. 사이트의 기사별 수정 제안·작업 신청 링크는 공개 GitHub 저장소로 연결됩니다.
