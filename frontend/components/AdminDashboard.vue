<script type="text/x-template" id="admin-dash">
  <div>
    <h5 class="mb-3">Admin Dashboard</h5>
    <div class="row">
      <div class="col-md-8">
        <div class="card mb-3">
          <div class="card-body">
            <h6>Lots</h6>
            <table class="table table-sm">
              <thead><tr><th>Name</th><th>Price/hr</th><th>Avail/Total</th><th>Actions</th></tr></thead>
              <tbody>
                <tr v-for="l in lots" :key="l.id">
                  <td>{{l.name}}</td>
                  <td>₹{{l.price}}</td>
                  <td>{{l.available}} / {{l.total}}</td>
                  <td>
                    <button class="btn btn-sm btn-outline-primary" @click="edit(l)">Edit</button>
                    <button class="btn btn-sm btn-outline-danger ms-2" @click="del(l)">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="mt-3">
              <h6>{{form.id?'Edit Lot':'Create Lot'}}</h6>
              <div class="row g-2">
                <div class="col"><input v-model="form.prime_location_name" class="form-control" placeholder="Name"></div>
                <div class="col"><input v-model.number="form.price" class="form-control" placeholder="Price"></div>
                <div class="col"><input v-model.number="form.number_of_spots" class="form-control" placeholder="Spots"></div>
              </div>
              <div class="row g-2 mt-2">
                <div class="col"><input v-model="form.address" class="form-control" placeholder="Address"></div>
                <div class="col"><input v-model="form.pin_code" class="form-control" placeholder="PIN"></div>
              </div>
              <button class="btn btn-primary mt-2" @click="save">Save</button>
              <button v-if="form.id" class="btn btn-secondary mt-2 ms-2" @click="reset">Cancel</button>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-body">
            <h6>Users</h6>
            <ul class="list-group">
              <li v-for="u in users" :key="u.id" class="list-group-item d-flex justify-content-between">
                <span>{{u.username}}</span><span>{{u.email}}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</script>
<script>
Vue.component('admin-dashboard', {
  template:'#admin-dash',
  data:()=>({lots:[], users:[], form:{id:null, prime_location_name:'', price:20, number_of_spots:0, address:'', pin_code:''}}),
  created(){ this.load(); },
  methods:{
    async load(){
      const {data}=await Api.adminDashboard(); this.lots=data.lots;
      const u=await Api.adminUsers(); this.users=u.data.users;
    },
    edit(l){
      this.form={ id:l.id, prime_location_name:l.name, price:l.price, number_of_spots:l.total, address:'', pin_code:'' };
    },
    reset(){ this.form={id:null, prime_location_name:'', price:20, number_of_spots:0, address:'', pin_code:''}; },
    async save(){
      if(this.form.id){ await Api.updateLot(this.form.id, this.form); }
      else{ await Api.createLot(this.form); }
      this.reset(); await this.load();
    },
    async del(l){
      if(confirm('Delete lot?')){ await Api.deleteLot(l.id); await this.load(); }
    }
  }
})
</script>
