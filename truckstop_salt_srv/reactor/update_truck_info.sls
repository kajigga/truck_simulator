# New truck info was just received. Send a message to Truckstop to save the
# truck's information
call_build_check_orch:
  local.truckstop.save_truck:
    - tgt: truckstop-master
    - args:
      - truck: {{ data['post']|yaml }}

