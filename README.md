# Python pipeline

git bash

```bash
docker build -t test:pandas .
# -t(태그 지정) 이름:태그 기본값은 latest
# -f(Dockerfile명 지정)

# failed to read dockerfile: open Dockerfile: no such File or Directory
# -> docker를 사용하기 전에 반드시 docker desktop이 실행 중인지 확인

# docker run -it 실패
# ERROR: error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping": open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
# the input device is not a TTY.  If you are using mintty, try prefixing the command with 'winpty'

$winpty docker run -it test:pandas 123

# -i (--interactive) : 표준 입력을 계속 열어둠
# -t (--tty) : 터미널(TTY) 세션을 할당해서 셸 환경처럼 사용 가능하게 함

```

Dockerfile

```bash
# base image
FROM python:3.9.1

# installing prerequisites
RUN pip install pandas

# working directory inside cont
WORKDIR /app

# copy the script to the cont
COPY pipeline.py pipeline.py

# what to do first
ENTRYPOINT ["python", "pipeline.py"]
```

pipeline.py

```bash
import sys
import pandas

print(sys.argv)

# index 0 is name of the file
day = sys.argv[1]

print(f'job finished for day={day}')

```
