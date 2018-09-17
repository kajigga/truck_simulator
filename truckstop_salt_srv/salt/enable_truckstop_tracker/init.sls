{% load_yaml as pkg_map %}
RedHat:
  repo_name: https://download.docker.com/linux/centos/docker-ce.repo
  gpgkey: https://download.docker.com/linux/centos/gpg
  packages:
    - python2-pip
    - gnupg2
    - curl
    - yum-utils
    - device-mapper-persistent-data
    - lvm2
Debian:
  repo_name: "deb [arch=amd64] https://download.docker.com/linux/debian stretch stable"
  gpgkey: https://download.docker.com/linux/debian/gpg
  packages:
    - python-pip
    - python-apt
    - apt-transport-https
    - apt-transport-https
    - ca-certificates
    - curl
    - gnupg2
    - software-properties-common

{% endload %}

{% set pkg_info = salt['grains.filter_by'](pkg_map) %}

packages_installed:
  pkg.installed:
    - pkgs: 
      {% for pkg in pkg_info.packages %}
      - {{ pkg }}
      {% endfor %}


add_key_if_not_there:
  pkgrepo.managed:
    - name: {{ pkg_info.repo_name }}
    - gpgcheck: 1
    - key_url: {{ pkg_info.gpgkey }}
    - refresh: true

docker_ce_installed:
  pkg.installed:
    - name: docker-ce

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
      - configure_sdb

# Need to generate an rsa key
# generate_ssh_key_for_gitlab:
#   cmd.run:
#     - name: ssh-keygen -q -N '' -f /etc/salt/git_id_rsa
#     - unless: test -f /etc/salt/git_id_rsa
