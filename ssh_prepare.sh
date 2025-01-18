apt-get update -y
apt-get install -y openssh-client
mkdir -p ~/.ssh
echo "$SSH_PRIVATEKEY" > ~/.ssh/id_ed25519
chmod 0600 ~/.ssh/id_ed25519
echo "Host *\n\tStrictHostKeyChecking accept-new\n\n" > ~/.ssh/config
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_ed25519
echo $SSH_EC2 > ~/.ssh/toypage.pem