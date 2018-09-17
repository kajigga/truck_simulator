# NOTE: Not sure, but I think this state may be obsolete
#
# Check for some required pillar values
test_pillar:
  test.check_pillar:
    - present:
      - truck_id # Passed in as part of the state run
      - 'truckstop:repo_url'
      - 'truckstop:repo_branch'
      - 'truckstop:truckstop_url'
      - 'truckstop:git_test_branch'

checkout_testTruck_code:
  git.latest:
    - name: {{  salt['pillar.get']('truckstop:repo_url') }}
    - rev: {{  salt['pillar.get']('truckstop:git_test_branch') }}
    - branch: {{  salt['pillar.get']('truckstop:git_test_branch') }}
    - force_fetch: True
    - force_reset: True
    - target: /tmp/testTruck
    # - identity: /etc/salt/git_id_rsa # commented out because we'll rely on
    # the git repo being public right now
    - require:
      - test_pillar

# make sure image is present (and rebuilt) before testing
build_image:
  docker_image.present:
    - name: truck
    - build: /tmp/testTruck/
    - tag: latest
    - require:
      - test_pillar

# # start a container using the new image
{% set truck_id = salt['pillar.get']('truck_id') %}
start_test_container:
  docker_container.running:
    - name: {{truck_id}}
    - image: 'truck:latest' # TODO it would make sense to have this in pillar
    - environment:
      - TRUCK_ID: {{truck_id}}
      - TRUCKSTOP_URL: {{ salt['pillar.get']('truckstop:truckstop_url')}}
    - require:
      - build_image
      - test_pillar

