# Releasing a new image means the following:
# - Build new docker image with predefined tag

# Check for some required pillar values
test_build_checks_pillar:
  test.check_pillar:
    - present:
      - 'truckstop:repo_url'
      - 'truckstop:repo_branch'

checkout_testTruck_code:
  git.latest:
    - name: {{ salt['pillar.get']('truckstop:repo_url') }}
    - rev: {{ salt['pillar.get']('truckstop:repo_branch') }}
    - branch: {{ salt['pillar.get']('truckstop:repo_branch') }}
    - force_fetch: True
    - force_reset: True
    - target: /tmp/testTruck
    - identity: /etc/salt/git_id_rsa
    - require:
      - test_pillar

# # build an image based on the dev branch

# make sure image is present and rebuilt 
build_truck_image:
  docker_image.present:
    - name: "truck"
    - build: /tmp/testTruck/
    - tag: latest
    #- dockerfile: /tmp/testTruck/DockerFile
    - force: true
    - require:
      - checkout_testTruck_code

# TODO 
# - upload new docker image to image repository
# - send update information to current running trucks
# alert_of_firmware_upgrade:
#  module.run:
# - "firmware upgrades" can happen anytime a truck is stopped
# - "hardware upgrades" can only happen when the truck is in the maintenance
#   building
# - signals should be sent(or made available) to all trucks to return to
#   receive hardware upgrades
