curl -O https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
mv openjdk-11.0.2_linux-x64_bin.tar.gz /usr/lib/jvm/
cd /usr/lib/jvm/; tar -zxvf openjdk-11.0.2_linux-x64_bin.tar.gz
update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-11.0.2/bin/java 1
update-alternatives --set java /usr/lib/jvm/jdk-11.0.2/bin/java

wget https://www.dropbox.com/s/j1epbu4ufunbbzv/lucene-index-covid-2020-03-27.tar.gz
tar xvfz lucene-index-covid-2020-03-27.tar.gz
