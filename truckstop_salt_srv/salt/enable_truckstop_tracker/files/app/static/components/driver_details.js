{% raw %}
Vue.component('driver-details', {
    props: ['driver'],
    template: `<div class='driver'>
    <img :src='driver.picture.medium' width='75px' :alt='driver.name.first +" "+ driver.name.last'/>
    <span class='name'>{{driver.name.first}}</span> <span class='name'>{{ driver.name.last }}</span>
    </div>`

});
{% endraw %}
