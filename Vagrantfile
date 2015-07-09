# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  config.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update

      apt-get -y install python-dev libffi-dev libssl-dev
      apt-get -y install libmagickwand-dev
      apt-get -y install python-pip

      pip install virtualenv

      pip install Wand
      pip install Flask
      pip install requests
      pip install requests[security]
      pip install rq

      # install redis
      apt-get -y install build-essential
      apt-get -y install tcl8.5
      wget http://download.redis.io/releases/redis-stable.tar.gz
      tar xzf redis-stable.tar.gz
      cd redis-stable
      make
      sudo make install
      cd utils
      sudo ./install_server.sh
  SHELL

end
