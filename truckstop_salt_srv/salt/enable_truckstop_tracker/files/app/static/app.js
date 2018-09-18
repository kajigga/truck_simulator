// Initialize Vue.js app
var app = new Vue({
  el: '#app',
  data: {
    message: 'Hello Vue!',
    trucks: []
  }
})

// Initialize and add the map
var map;
var timer;
var markers = {};
function initMap() {
  var center_point = {
    "lat": 41.7632725,
    "lng": -72.68462149999999
  };
  // The map, centered at Uluru
  map = new google.maps.Map(document.getElementById('map'), {zoom: 5, center: center_point});
  load_truck_locations();
  timer = setInterval(load_truck_locations, 1000);
}
function load_truck_locations(){
  
  var cache_buster = new Date().getTime();
  axios.get('/static/data.js', params={'buster': cache_buster}).then(function(response){
      // The marker, positioned at Uluru
      var location, truck_id;
      app.trucks = [];
      for(var x=0, l=response.data.length; x<l; x++){
          location = response.data[x].location;
          truck_id = response.data[x].id;
          app.trucks.push(response.data[x]);
          var latlng;
          if(truck_id && location !== ''){

            var color =  'blue'; // red, green, purple, yellow, blue
            switch(response.data[x]['status']){
              case 'stationary':
                color = 'yellow';
                break;
              case 'active':
                color = 'green';
                break;
              case 'broken_down':
                color = 'red';
                break;
            }
            // console.log('truck_id', truck_id);
            // console.log('location', location);
            var icon = 'http://maps.google.com/mapfiles/ms/icons/'+color+'-dot.png';
            if( !markers.hasOwnProperty(truck_id)){
                markers[truck_id] = new google.maps.Marker({
                    // icon: 'https://maps.google.com/mapfiles/kml/shapes/truck.png',
                    icon: icon,
                    position: location,
                    title: truck_id,
                    map: map});
            }else{
                markers[truck_id].setPosition(location);
                markers[truck_id].setIcon(icon);
            }
          }
      }
  });
}
