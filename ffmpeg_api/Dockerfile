FROM jrottenberg/ffmpeg:3.2-ubuntu

RUN apt update && apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y && apt update
RUN apt install -y python3.9 python3.9-venv python3.9-dev curl 
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.9 get-pip.py
RUN pip3.9 install poetry 

WORKDIR /app
COPY . .

RUN poetry install

ENTRYPOINT [ "poetry", "run", "uvicorn", "ffmpeg_server:app", "--reload", "--host", "0.0.0.0" ]