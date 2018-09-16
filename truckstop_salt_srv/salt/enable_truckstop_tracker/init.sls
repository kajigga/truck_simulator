packages_installed:
  pkg.installed:
    - pkgs: 
      - python-pip
      - python-apt
      - apt-transport-https
      - apt-transport-https
      - ca-certificates
      - curl
      - gnupg2
      - software-properties-common

add_key_if_not_there:
  pkgrepo.managed:
    - name: "deb [arch=amd64] https://download.docker.com/linux/debian stretch stable"
    - gpgcheck: 1
    - key_url: https://download.docker.com/linux/debian/gpg 

refresh_apt_if_needed:
  module.run:
    - name: pkg.refresh_db
    - watch: 
      - add_key_if_not_there

docker_ce_installed:
  pkg.installed:
    - name: docker-ce
    - watch: 
      - refresh_apt_if_needed

install_docker_python_module:
  pip.installed:
    - name: 'docker'
    - require:
      - packages_installed

configure_sdb:
  file.managed:
    - name: /etc/salt/minion.d/sdb.conf
    - contents: |
        truck_db:
          driver: sqlite3
          database: /tmp/sdb.sqlite
          table: sdb
          create_table: True

restart_minion:
  service.running:
    - name: salt-minion
    - watch: 
      - add_beacon
      - configure_sdb

# Need to generate an rsa key
generate_ssh_key_for_gitlab:
  cmd.run:
    - name: ssh-keygen -q -N '' -f /etc/salt/git_id_rsa
    - unless: test -f /etc/salt/git_id_rsa
