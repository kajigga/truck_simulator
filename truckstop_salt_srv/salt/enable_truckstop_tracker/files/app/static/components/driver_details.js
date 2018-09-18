Vue.component('driver-details', {
    props: ['driver'],
    template: `
    <p>{{driver.name.first}} {{ driver.name.last }}</p>
    
    `

});

