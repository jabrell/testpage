FROM ubuntu

ENV SERVER_USER=abrell
ENV SERVER_IP=wwz-noe.wwz.unibas.ch
ENV DOCKER_IMAGE=registry.gitlab.com/jan.abrell/toypage:latest
ENV SSH_PRIVATEKEY id_ed25519
ENV SSH_PUBLICKEY id_ed25519.pub
ENV TEST 1234

COPY ${SSH_PRIVATEKEY} /my_tmp/id_ed25519

RUN apt-get update &&\
    apt-get install -y openssh-client&&\
    mkdir ~/.ssh/ &&\
    echo "Host *\n\tStrictHostKeyChecking accept-new\n\n" > ~/.ssh/config &&\
    cp /my_tmp/id_ed25519 ~/.ssh/id_ed25519 

RUN ssh  ${SERVER_USER}@${SERVER_IP} "touch i_was_here.txt"
    
# COPY ${SSH_PRIVATEKEY} /.ssh/id_ed25519
# COPY ${SSH_PUBLICKEY} /.ssh/id_ed25519.pub
# COPY app.py /app.py
#ssh -v -o StrictHostKeyChecking=no ec2-user@ec2-52-59-210-234.eu-central-1.compute.amazonaws.com "touch i_was_here.txt"

