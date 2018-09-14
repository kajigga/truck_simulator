# A successfull build just arrived.
# 
# Run the build checks

{% set post = salt['pillar.get']('post') %}

# The following state checks out the most recent code, builds an image, and
# runs the truck.run_setup_build_checks:
run_buildchecks:
  salt.state:
    - tgt: truckstop-master
    - sls: build_checks
    - pillar: 
        post: {{ post|yaml}}


# # check for incoming telemetry from the test truck
# # aka Wait for events on the bus
# A successful launch results in a new production docker
# image being built and saved for future trucks to use.


wait_for_ping_from_test_truck:
  salt.wait_for_event:
    - name: truckstop/test_truck/location
    - id_list: 
      - truckstop-master
    - timeout: 65
    - require:
      - run_setup_build_checks

fail_to_receive_startup_event:
  salt.runner:
    - name: event.send
    - tag: truckstop/build/{{post['buildName']}}/failed
    - data: 
        build_data: {{ post|yaml}}
    - onfail_any:
      - wait_for_ping_from_test_truck

# We may want to remove the container as well

received_startup_event:
  salt.runner:
    - name: event.send
    - tag: truckstop/build/{{post['buildName']}}/successful
    - data: 
        build_data: {{ post|yaml}}
    - watch:
      - wait_for_ping_from_test_truck

stop_test_container:
  salt.state:
    - tgt: truckstop-master
    - sls: build_checks.stop_test_truck
    - pillar: 
        post: {{ post }}
    - watch:
      - wait_for_ping_from_test_truck
      - fail_to_receive_startup_event

# release_new_image_for_trucks:
release_new_image_for_trucks:
  salt.state:
    - tgt: truckstop-master
    - sls: build_checks.release_image
    - pillar: 
        post: {{ post }}
    - watch:
      - received_startup_event
