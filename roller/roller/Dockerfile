FROM python:3 as python-base

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.13

# System deps:
RUN apt install curl -y 
RUN apt install unzip -y
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" 
RUN mv kubectl /usr/local/bin/
# still leverage kubectl for 'cordon' :()
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

RUN chmod +x /usr/local/bin/kubectl
#RUN apt purge curl -y
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
#WORKDIR /code
#COPY poetry.lock pyproject.toml /code/

# Project initialization:
#RUN poetry config virtualenvs.create false \
#  && poetry install --no-interaction --no-ansi

# Creating folders, and files for a project:

COPY ./utils/vault /usr/local/bin/ 
RUN chmod +x /usr/local/bin/vault
#COPY ./utils/aws /code/


#ENTRYPOINT ["/code/entrypoint.sh"]





