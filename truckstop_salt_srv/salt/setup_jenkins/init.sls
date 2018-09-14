# This state file is a work in progress. The idea is to install all of the
# required jenkins plugins and add a default job definition to monitor for
# changes to a git repository and run the job when changes are detected or a
# post-commit hook message is received.

pip_installed:
  pkg.installed:
    - name: python-pip

install_jenkins_python_module:
  pip.installed:
    - name: python-jenkins
    - require:
      - pip_installed

# install plugins
{% set do_restart = False %}

{% for plugin in ['cobertura', 'warnings', 'junit', 'violations', 'gitlab-plugin', 'outbound-webhook', 'docker-plugin'] %}
{% set plugin_installed = salt['jenkins.plugin_installed'](plugin) %}
{% if not plugin_installed %}


plugin_not_installed_{{plugin}}:
  test.configurable_test_state:
    - name: {{plugin}} not installed
    - changes: True
    - result: True
    - comment: {{ plugin }} not installed {{ plugin_installed }}


{% set do_restart = True %}
install_plugin_{{plugin}}:
  module.run:
    - name: jenkins.run
    - func: jenkins.run
    - script: 'Jenkins.instance.updateCenter.getPlugin("{{plugin}}").deploy()'
    - require:
      - install_jenkins_python_module
    - require_in:
      - restart_jenkins
{% endif %}
{% endfor %}

{% if do_restart %}
# restart jenkins
# https://support.cloudbees.com/hc/en-us/articles/216118748-How-to-Start-Stop-or-Restart-your-Instance-
restart_jenkins:
  module.run:
    - name: jenkins.run
    - func: jenkins.run
    - script: 'Jenkins.instance.safeRestart()'
    - require:
      - install_jenkins_python_module
    - require_in:
      - create_job_xml

# How do I wait for 20 seconds before continuing?
{% endif %}

# setup job
# https://docs.saltstack.com/en/latest/ref/states/all/salt.states.jenkins.html
# this is useful mostly useful for setting up a job
#
# make sure to configure a pillar with the necessary information
# Example Pillar
# truckstop:
#   repo_url: http://<gitlab_host_ip>:<port>/
#   repo_branch: dev
#   edge_server: 
#     url: http://<ip_hostname>:<port>/hook/truck/build/status
#     send_on_start: true
#     send_on_success: true
#     send_on_failure: true

create_job_xml:
  file.managed:
    - name: /tmp/truck_job.xml
    - source: salt://setup_jenkins/files/watchTruckJob.xml
    - template: jinja

job_exists:
  jenkins.present:
    - name: testTruck
    - config: /tmp/truck_job.xml
    - require:
      - install_jenkins_python_module
      - create_job_xml

