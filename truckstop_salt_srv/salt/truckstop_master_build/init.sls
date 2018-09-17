# Make sure there is a user names saltdev on the system
create_user:
  user.present:
    - name: saltdev

# TODO I'm pretty sure this needs to be made platform-agnostice by looking up the os
# family and listing them accordingly
# Make sure the cherrypy and a few other items needed for git are installed
install_pip:
  pkg.installed:
    - pkgs: 
      - python-pip

{% for pip_pkg in ['cherrypy','docker', 'GitPython'] %}
pip_{{pip_pkg}}_installed:
  pip.installed:
    - name: {{ pip_pkg }}
    - require:
      - install_pip
    - require_in:
      - salt-master_running
{% endfor %}

# Create a certificate for the api
create_certificate:
  cmd.run:
    - name: salt-call --local tls.create_self_signed_cert
    - creates: 
      - /etc/pki/tls/certs/localhost.crt
      - /etc/pki/tls/certs/localhost.key

# Make sure the master has rest_api config and it is in the proper
# configuration
setup_master_conf:
  file.recurse:
    - name: /etc/salt/master.d/
    - source: salt://truckstop_master_build/files/master.d
    - template: jinja

setup_minion_conf:
  file.recurse:
    - name: /etc/salt/minion.d/
    - source: salt://truckstop_master_build/files/minion.d



# start, or restart, salt-master when one of the watched state ids changes
salt-master_running:
  service.running:
    - name: salt-master
    - enable: true
    - watch:
      - setup_master_conf

# start, or restart, the salt-api when one of the watched state ids changes
salt_api_running:
  service.running:
    - name: salt-api
    - enable: true
    - watch: 
      - salt-master_running
      - create_certificate

# start, or restart, salt-minion when one of the watched state ids changes
salt_minion_running:
  service.running:
    - name: salt-minion
    - enable: true
    - watch:
      - setup_minion_conf
