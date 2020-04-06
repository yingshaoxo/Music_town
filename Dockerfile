#FROM python:3.5
#
#RUN pip install --no-cache-dir flask
#
#COPY . /usr/src/music_town/
#
#RUN chmod +x /usr/src/music_town/tool.sh
#
#EXPOSE 2016
#
#CMD ["bash", "/usr/src/music_town/tool.sh", "docker_run"]


FROM ubuntu:19.10
COPY ./dist/app /usr/src/music_town/
EXPOSE 2016
CMD ["/usr/src/music_town/app"]
