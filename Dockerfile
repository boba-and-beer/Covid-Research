FROM ubuntu:latest
# set up Java Installation for Anserini
RUN apt-get update \  
  && apt-get install -y python3-pip python3-dev \  
  && cd /usr/local/bin \  
  && ln -s /usr/bin/python3 python \  
  && pip3 install flask \
  && curl -O https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz \
  && mv openjdk-11.0.2_linux-x64_bin.tar.gz /usr/lib/jvm/ \
  && cd /usr/lib/jvm/ \
  && tar -zxvf openjdk-10.0.2_linux-x64_bin.tar.gz \
  && update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-11.0.2/bin/java 1 \
  && update-alternatives --set java /usr/lib/jvm/jdk-11.0.2/bin/java
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3","app.py"]
