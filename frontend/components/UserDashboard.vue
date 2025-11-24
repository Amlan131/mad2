<script type="text/x-template" id="user-dash">
  <div>
    <h5 class="mb-3">User Dashboard</h5>
    <div class="row">
      <div class="col-md-7">
        <div class="card mb-3">
          <div class="card-body">
            <h6>Available Lots</h6>
            <table class="table table-sm">
              <thead><tr><th>Name</th><th>Price/hr</th><th>Available</th><th></th></tr></thead>
              <tbody>
                <tr v-for="l in lots" :key="l.id">
                  <td>{{l.name}}</td><td>₹{{l.price}}</td><td>{{l.available}}</td>
                  <td><button class="btn btn-sm btn-primary" :disabled="l.available===0" @click="book(l)">Book</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card">
          <div class="card-body">
            <h6>My Reservations</h6>
            <table class="table table-sm">
              <thead><tr><th>ID</th><th>Lot</th><th>Spot</th><th>In</th><th>Out</th><th>Cost</th><th></th></tr></thead>
              <tbody>
                <tr v-for="r in rows" :key="r.id">
                  <td>{{r.id}}</td><td>{{r.lot_id}}</td><td>{{r.spot_id}}</td>
                  <td>{{r.parking_in}}</td><td>{{r.parking_out || '-'}}</td><td>{{r.cost || '-'}}</td>
                  <td><button class="btn btn-sm btn-outline-success" v-if="!r.parking_out" @click="release(r)">Release</button></td>
                </tr>
              </tbody>
            </table>
            <div class="mt-2">
              <button class="btn btn-outline-secondary" @click="exportCsv" :disabled="exporting">Export CSV</button>
              <a v-if="csvReady" :href="csvDataUrl" :download="csvName" class="btn btn-link">Download CSV</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</script>
<script>
Vue.component('user-dashboard', {
  template:'#user-dash',
  data:()=>({lots:[], rows:[], exporting:false, taskId:null, csvReady:false, csvName:'', csvDataUrl:''}),
  created(){ this.load(); },
  methods:{
    async load(){ const l=await Api.userLots(); this.lots=l.data.lots; const r=await Api.myReservations(); this.rows=r.data.rows; },
    async book(l){ await Api.book(l.id); await this.load(); },
    async release(r){ await Api.release(r.id); await this.load(); },
    async exportCsv(){
      this.exporting=true; this.csvReady=false;
      const {data}=await Api.exportCsv(); this.taskId=data.task_id;
      const poll = setInterval(async ()=>{
        const st=await Api.exportStatus(this.taskId);
        if(st.data.ready){
          clearInterval(poll);
          this.csvName=st.data.filename;
          const blob=new Blob([st.data.content], {type:'text/csv'});
          this.csvDataUrl=URL.createObjectURL(blob);
          this.csvReady=true; this.exporting=false;
        }
      }, 1500);
    }
  }
})
</script>
