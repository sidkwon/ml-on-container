# FROM: 어떤 도커 컨테이너 이미지를 기반으로 이미지를 생성할지 설정
# FROM <이미지> 또는 FROM <이미지>:<태그>
# TensorFlow Docker Images
# https://hub.docker.com/r/tensorflow/tensorflow/
FROM tensorflow/tensorflow

# MAINTAINER: 이미지를 생성한 사람의 정보를 설정
MAINTAINER MFG Boost Program

# Install required package
RUN pip install sklearn

# Prepare training
RUN mkdir -p /opt/ml/code
RUN mkdir -p /opt/ml/model

# VOLUME: 디렉터리의 내용을 컨테이너에 저장하지 않고 호스트에 저장하도록 설정, docker run 할 때 --mount 옵션과 같이 사용
VOLUME /opt/ml/model

# COPY: 로컬 파일을 컨테이너 이미지에 추가
COPY train.py /opt/ml/code

# WORKDIR: RUN, CMD, ENTRYPOINT의 명령이 실행될 디렉터리를 설정
WORKDIR /opt/ml/code

# ENTRYPOINT: 컨테이너가 시작되었을 때 스크립트 혹은 명령을 실행
ENTRYPOINT ["python", "train.py"]