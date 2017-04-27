# docker-grader
A grading system using docker



## Installation prerequisites

* Install rabbitmq and other packages:
```
sudo apt-get install rabbitmq-server libxml2-dev libxslt1-dev python3-dev python-dev unzip
```

* Install python-vitruaevn

```
sudo apt install python-virtualenv
```

* Create virtual environment into /vagrant

```
cd /vagrant
virtualenv -p python3 venv3
```

* Activate virtual environment `venv3`

```
. ./venv3/bin/activate
```

* Install requrements
```
cd django
pip install -r requirements.txt
```


* Migrate the database
```
./manage.py migrate
```

* Create superuser

```
./manage.py createsuperuser
```

* Activate celery

```
cd django
celery -A grader worker -l info
```

* Install docker

```
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
   
sudo apt-get update

sudo apt-get install docker-ce

```

* Add group `docker`

```
sudo groupadd docker
sudo usermod -aG docker ubuntu
```

* Pull docker images

```
docker pull gcc:latest
docker pull python:latest
```

