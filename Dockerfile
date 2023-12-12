FROM ubuntu:latest

RUN sudo apt-get update && sudo apt-get upgrade -y

RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

RUN brew update && \
    brew install pyenv

RUN pyenv install 3.12.1 && \
    pip install --upgrade pip \
    pip install pipenv --user

COPY . /usr/share/presence_backend/

WORKDIR /usr/share/presence_backend/

CMD ["pp"]