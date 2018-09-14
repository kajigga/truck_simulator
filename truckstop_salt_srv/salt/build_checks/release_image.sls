# Releasing a new image means the following:
# - Build new docker image with predefined tag

checkout_testTruck_code:
  git.latest:
    - name: git@10.62.10.25:kajigga/truckstop.git
    - rev: dev
    - branch: dev
    - force_fetch: True
    - force_reset: True
    - target: /tmp/testTruck
    - identity: /etc/salt/git_id_rsa

# # build an image based on the dev branch

# make sure image is present and rebuilt 
build_image:
  docker_image.present:
    - name: "truck"
    - build: /tmp/testTruck/
    - tag: prod
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
