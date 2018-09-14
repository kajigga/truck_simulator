# Send a command to Truckstop to update the website's data file
update_truck_data:
  local.truckstop.update_data_file:
    - tgt: truckstop-master
