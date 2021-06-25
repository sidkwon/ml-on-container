# AWS MFG Boost - ML on Container hands-on

# 1. 준비

## SageMaker Jupyter notebook instance 접속

### Open Terminal

Menu File > New > Terminal

### Activate **`tensorflow2_p36`** conda environment

- Conda is a virtual environment manager, a software that allows you to create, removing or packaging virtual environments as well as installing software

```bash
sh-4.2$ bash
(base) [ec2-user@ip-172-16-125-172 ~]$ conda env list
# conda environments:
#
base                  *  /home/ec2-user/anaconda3
...
tensorflow2_p36          /home/ec2-user/anaconda3/envs/tensorflow2_p36

(base) [ec2-user@ip-172-16-125-172 ~]$ source activate tensorflow2_p36

(tensorflow2_p36) [ec2-user@ip-172-16-125-172 ~]$ cd ~/SageMaker
```

## git clone

```bash
$ git clone https://github.com/sidkwon/ml-on-container.git
$ cd ml-on-container
```

# 2. 로컬에서 train.py 실행

```bash
$ sudo mkdir -p /opt/ml/model
$ sudo chown ec2-user:ec2-user -R /opt/ml/model
$ python train.py
```

# 3. tensorflow docker container 실행

```bash
$ docker run -it --rm tensorflow/tensorflow bash

(Container안에서 아래 명령어 수행)
root@1382004b5a16:/# python -c "import tensorflow as tf;print(tf.__version__)"
2.5.0

root@1382004b5a16:/# exit
```

**docker run 옵션**: [http://pyrasis.com/book/DockerForTheReallyImpatient/Chapter20/28](http://pyrasis.com/book/DockerForTheReallyImpatient/Chapter20/28)

- -i : i, --interactive=false: 표준 입력(stdin)을 활성화하며 컨테이너와 연결(attach)되어 있지 않더라도 표준 입력을 유지합니다. 보통 이 옵션을 사용하여 Bash에 명령을 입력합니다.
- -t, --tty=false: TTY 모드(pseudo-TTY)를 사용합니다. Bash를 사용하려면 이 옵션을 설정해야 합니다. 이 옵션을 설정하지 않으면 명령을 입력할 수는 있지만 셸이 표시되지 않습니다.
- -rm=false: 컨테이너 안의 프로세스가 종료되면 컨테이너를 자동으로 삭제합니다.

# 4. tensorflow docker container에서 학습 실행

## Variables 선언

```bash
# Variables
$ export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r ".Account")
$ export AWS_REGION=$(python -c 'import boto3; print(boto3.Session().region_name)')
$ export RANDOM_STRING=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 16 | head -n 1)
```

## MNIST 분류 모델을 저장할 디렉터리 생성

```bash
$ mkdir -p /tmp/tf-models
```

## 컨테이너 이미지 빌드

```bash
$ docker build --tag mfgboost-tf-training:0.1 . --file Dockerfile
```

## 컨테이너 이미지 확인

```bash
$ docker images
```

## 컨테이너 실행

```bash
$ docker run --mount type=bind,source=/tmp/tf-models,target=/opt/ml/model mfgboost-tf-training:0.1

$ ls -lat /tmp/tf-models
```

## 컨테이너 이미지를 저장할 ECR(Elastic Container Registry) 생성

```bash
$ aws ecr create-repository --repository-name mfgboost-train-$RANDOM_STRING
```

## 컨테이너 이미지를 ECR에 push

```bash
# Authrization
$ aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tagging
$ docker tag mfgboost-tf-training:0.1 $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/mfgboost-train-$RANDOM_STRING:0.1

# Verify
$ docker images

# Push
$ docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/mfgboost-train-$RANDOM_STRING:0.1

# Verify
$ aws ecr list-images --repository-name mfgboost-train-$RANDOM_STRING
```

## 로컬 컨테이너, 컨테이너 이미지, 모델 모두 삭제

```bash
# Remove all containers
$ docker rm $(docker ps -a -q)

# Remove all images
$ docker rmi -f $(docker images -a -q)

# Delete model
$ sudo rm -rf /tmp/tf-models/*

# Verify
$ docker ps -a
$ docker images
```

## ECR에 저장된 컨테이너 이미지를 pull 하여 학습

```bash
$ docker run --mount type=bind,source=/tmp/tf-models,target=/opt/ml/model $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/mfgboost-train-$RANDOM_STRING:0.1
```

## 학습 후 모델 확인

```bash
$ ls /tmp/tf-models/mnist
```
<!-- blank line -->

## Mission!!!
- Dropout의 비율을 0.4에서 0.2로 수정 후 저장
- New container image build (imagename: mfgboost-tf-training:0.2)
- New container image를 tag한 후 ECR에 push

<!-- blank line -->
----
<!-- blank line -->

# 5. tensorflow docker container에서 추론 실행

## TF Serving 컨테이너 실행

```bash
$ docker run --rm -p 8501:8501 --name tf-serving-mnist --mount type=bind,source=/tmp/tf-models/mnist,target=/models/mnist -e MODEL_NAME=mnist tensorflow/serving
```

## 추론

### mnist_inference.ipynb 참조
### Mission!
mnist_inference.ipynb 파일의 mnist_inference(100) 셀을 실행하면 다음과 같은 오류가 발생한다. 오류가 발생하는 이유를 생각해 보고 mnist_inference 함수를 수정해 보자. (hint: train.py를 참조한다)

```bash
{'error': 'input must be 4-dimensional[784]\n\t [[{{node sequential/conv2d/Relu}}]]'}
```

# Clean-up

```bash
# Remove all containers
$ docker rm $(docker ps -a -q)

# Remove all images
$ docker rmi -f $(docker images -a -q)

# Remove ECR repository
$ aws ecr delete-repository --repository-name mfgboost-train-$RANDOM_STRING
```
