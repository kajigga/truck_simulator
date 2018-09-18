{% raw %}
Vue.component('driver-details', {
    props: ['driver'],
    template: `
        <div class='driver'>
            <div class='photo'>
                <img :src='driver.picture.medium' width='75px' :alt='driver.name.first +" "+ driver.name.last'/>
            </div>
            <div class='driver-info'>
                <span class='name'>{{driver.name.first}}</span> <span class='name'>{{ driver.name.last }}</span>
                <br/>
                <span class='phone'>{{ driver.phone }}</span>
                <br/>
                <span class='cell'>{{ driver.cell }}</span>
                <br/>
                <span class='email'>{{ driver.email }}</span>
            </div>
        </div>
    `

});
{% endraw %}
