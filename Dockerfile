FROM python:3.5

COPY . /usr/src/music_town/
RUN pip install --no-cache-dir -r /usr/src/music_town/requirements.txt

RUN chmod +x /usr/src/music_town/docker_run.sh

EXPOSE 2016

CMD ["bash", "/usr/src/music_town/tool.sh", "docker_run"]
