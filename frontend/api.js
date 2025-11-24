const API = "/api";
function authHeaders() {
  const jwt = localStorage.getItem("jwt");
  return { Authorization: `Bearer ${jwt}` };
}

const Api = {
  login(data) {
    return axios.post(`${API}/auth/login`, data);
  },
  register(data) {
    return axios.post(`${API}/auth/register`, data);
  },

  adminDashboard() {
    return axios.get(`${API}/admin/dashboard`, { headers: authHeaders() });
  },
  adminUsers() {
    return axios.get(`${API}/admin/users`, { headers: authHeaders() });
  },
  createLot(data) {
    return axios.post(`${API}/admin/lots`, data, { headers: authHeaders() });
  },
  updateLot(id, data) {
    return axios.put(`${API}/admin/lots/${id}`, data, {
      headers: authHeaders(),
    });
  },
  deleteLot(id) {
    return axios.delete(`${API}/admin/lots/${id}`, { headers: authHeaders() });
  },

  userLots() {
    return axios.get(`${API}/user/lots`, { headers: authHeaders() });
  },
  book(lot_id) {
    return axios.post(
      `${API}/user/book`,
      { lot_id },
      { headers: authHeaders() }
    );
  },
  release(reservation_id) {
    return axios.post(
      `${API}/user/release`,
      { reservation_id },
      { headers: authHeaders() }
    );
  },
  myReservations() {
    return axios.get(`${API}/user/reservations`, { headers: authHeaders() });
  },
  exportCsv() {
    return axios.post(`${API}/user/export_csv`, {}, { headers: authHeaders() });
  },
  exportStatus(id) {
    return axios.get(`${API}/user/export_status/${id}`, {
      headers: authHeaders(),
    });
  },
};
