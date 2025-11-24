<script type="text/x-template" id="login-tpl">
  <div class="row">
    <div class="col-md-5 mx-auto">
      <div class="card">
        <div class="card-body">
          <h5 class="mb-3">Login</h5>
          <div class="mb-2">
            <label>Username</label>
            <input v-model="username" class="form-control" required>
          </div>
          <div class="mb-2">
            <label>Password</label>
            <input v-model="password" class="form-control" type="password" required>
          </div>
          <button class="btn btn-primary w-100" @click="login">Login</button>
          <hr>
          <h6>Register (User)</h6>
          <div class="mb-2"><input v-model="ruser" placeholder="username" class="form-control"></div>
          <div class="mb-2"><input v-model="remail" placeholder="email" class="form-control"></div>
          <div class="mb-2"><input v-model="rpass" type="password" placeholder="password" class="form-control"></div>
          <button class="btn btn-outline-secondary w-100" @click="register">Register</button>
          <div v-if="err" class="alert alert-danger mt-2">{{err}}</div>
        </div>
      </div>
    </div>
  </div>
</script>
<script>
Vue.component('login', {
  template: '#login-tpl',
  data: ()=>({username:'', password:'', ruser:'', remail:'', rpass:'', err:''}),
  methods:{
    async login(){
      this.err='';
      try{
        const {data}=await Api.login({username:this.username, password:this.password});
        this.$emit('logged', data);
      }catch(e){ this.err='Invalid credentials'; }
    },
    async register(){
      this.err='';
      try{
        await Api.register({username:this.ruser, email:this.remail, password:this.rpass});
        const {data}=await Api.login({username:this.ruser, password:this.rpass});
        this.$emit('logged', data);
      }catch(e){ this.err='Registration failed'; }
    }
  }
})
</script>
