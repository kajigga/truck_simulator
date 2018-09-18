{% raw %}
Vue.component('truck-details', {
    props: ['truck'],
    template: `
    <tr>
        <td>{{ truck.id}}</td>
        <td>{{ truck.destination}}</td>
        <td><driver-details :driver=truck.driver></driver-details></td>
        <td>{{ parseInt(truck.distance_travelled) }}</td>
        <td>{{ truck.location}}</td>
        <td>{{ truck.cargo.used }} of {{ truck.cargo.capacity }}</td>
        <td>{{ truck.status}}</td>
    </tr>
    `

});
{% endraw %}

