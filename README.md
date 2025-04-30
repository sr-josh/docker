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


# Postgres

```bash
# DB에 연결이 되지 않고 OperationalError가 발생하는 것은
# docker container를 통해 실행하지 않았기 때문..

winpty docker run -it \
	-e POSTGRES_USER="root" \
	-e POSTGRES_PASSWORD="root" \
	-e POSTGRES_DB="ny_taxi" \
	-v /c:/data/docker/ny_taxi_data:/var/lib/postgresql/data \
	-p 5432:5432 \
	--network=pg-network \
	--name pg-database \
	postgres:13

	# -v volume directory 설정 local:cont, linux인 경우 $(pwd) 사용 가능
	
	
	#@.@ docker: Error response from daemon: invalid mode: \Program Files\Git\var\lib\postgresql\data
	#-> 경로가 잘못된 경우 ex) C:앞에 슬래쉬 누락
```

```bash
# pgcli를 통해서 db에 접속
# git bash에서는 아무런 반응이 없어서 powershell에서 실행함
pip install pgcli
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

```bash
SELECT version();             -- PostgreSQL 버전 확인
SELECT current_database();    -- 현재 DB 확인
\dt                           -- 현재 스키마의 테이블 목록
\d                            -- describe table
\dn                           -- 스키마 목록
\l                            -- 데이터베이스 목록
```

# Jupyter Notebook

```bash
pip install jupyter
jupyter notebook #브라우저에서 jupyter가 실행됨
```

```bash
pip install pandas
import pandas as pd
pd.__version__

#csv를 읽어 df에 저장
df = pd.read_csv('yellow.csv', nrows=100) #100줄만
df
#타입 변경
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

#df로부터 테이블 생성하는 DDL 생성
print(pd.io.sql.get_schema(df, name='yellow_taxi_data'))
```

```bash
# git bash 창을 여러 개 열었을 때
# Error: Could not fork child process: There are no available terminals (-1)
# -> 윈도우에서는 사용자 세션에서 생성할 수 있는 프로세스 수에 제한이 있어 
# 계속 열고 닫고를 반복하면 한계에 도달할 수 있다.
# 재부팅하면 간단하게 해결됨!
```

```bash
pip install psycopg2-binary
pip install sqlalchemy

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
engine.connect()

print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
```

```bash
df_iter = pd.read_csv('yellow.csv', iterator=True, chunksize=100000)
df = next(df_iter)
#len(df)
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

#df.head(n=0) header only
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace') #테이블이 존재하면 drop하고 다시 생성
%time df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append') #데이터만 추가
```

```bash
from time import time

while True:
    t_start = time()
    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append') 
    t_end = time()
    print('insert... %.3f' % (t_end - t_start))
    
```


# pgAdmin

```bash
# 구글에 검색해서 이미지 이름만 따오면 간편하게 설치가 가능
# 필요한 파라미터는 gpt에게 문의

winpty docker run -it \
	-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
	-e PGADMIN_DEFAULT_PASSWORD="root" \
	-p 8080:80 \
	--network=pg-network \
	--name pg-admin\
	dpage/pgadmin4
	
	
```

localhost:8080으로 접속해서 위 이메일, 비밀번호를 입력한다.

register server > host name에 network연결시 지정한 이름을 넣어줘야 한다

postgres와 pdadmin 컨테이너를 네트워크로 연결해준다

```bash
docker network create pg-network

docker run ... 	
	--network=pg-network \
	--name container-name \
	
# docker: Error response from daemon: Conflict. The container name "/pg-database" is already in use by container "d650f5de227c545900721aaa124c5403b3c8713cb45d05affe1da114d966cf5e". You have to remove (or rename) that container to be able to reuse that name.
# -> container가 이미 존재하는 경우
docker stop pg-database  # 컨테이너 종료
docker rm pg-database    # 컨테이너 삭제
```

```bash
# Unable to connect to server
# [Errno -2] Name does not resolve
# -> 연결 정보가 잘못 되었는지 확인한다
# 네트워크 설정이 dpage/pgadmin4 이전에 있어야 한다
```



# Ingesting some data to postgres

```bash
jupyter nbconvert --to=script upload-data.ipynb #ipynb 파일을 스크립트로 변환
```

ingest_data.py

```python
#!/usr/bin/env python
# coding: utf-8

import os
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine
# pd.__version__

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    csv_name = 'yellow.csv'

    os.system(f"wget {url} -O {csv_name}") #안 되면 curl -O {url}
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append') 

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists='append') 
            t_end = time()
            print('insert... %.3f' % (t_end - t_start))
        except StopIteration:
            print("completed")
            break

# 직접 스크립트 실행시에만 __name__ == '__main__'이 되고
# module로 import하면 import ingest_data -> __name__ == 'ingest_data'
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postges')
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password name for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='db for postgres')
    parser.add_argument('--table_name', help='table name for postgres')
    parser.add_argument('--url', help='url for postgres')

    args = parser.parse_args()
    main(args)

```

## 1. 직접 실행

postgresql을 실행한 뒤

bash

```bash
python ingest_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --url="http://localhost/yellow.csv" #로컬에서 다운로드
```


## 2. Dockerizing


Dockerfile

```docker
FROM python:3.9.1

# for download
RUN apt-get install wget
# postgres db adapter for python, sqlalchemy needs it
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY ingest_data.py ingest_data.py 

ENTRYPOINT [ "python", "ingest_data.py" ]
```

```yaml
docker build -t taxi_ingest:v001 .

docker run -it \
    --network=pg-network \
    taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --url="http://localhost/yellow.csv"
```


## 3. docker-compose.yaml 다수의 컨테이너를 구동

```yaml

services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    volumes:
      - "./data_pgadmin:/var/lib/pgadmin"
    ports:
      - "8080:80"
```
