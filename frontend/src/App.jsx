import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import PrivateRoute from "./components/PrivateRoute.jsx";
import Home from "./pages/Home.jsx";
import Predict from "./pages/Predict.jsx";
import ImagePredict from "./pages/ImagePredict.jsx";
import Appointments from "./pages/Appointments.jsx";
import DoctorProfile from "./pages/DoctorProfile.jsx";
import Login from "./pages/Login.jsx";
import About from "./pages/About.jsx";
import DashboardUser from "./pages/DashboardUser.jsx";
import DashboardDoctor from "./pages/DashboardDoctor.jsx";
import DashboardAdmin from "./pages/DashboardAdmin.jsx";
import Dashboard from "./pages/Dashboard.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/predict" element={<Predict />} />
        <Route path="/predict/image" element={<ImagePredict />} />
        <Route path="/appointments" element={<Appointments />} />
        <Route path="/doctors/:id" element={<DoctorProfile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/about" element={<About />} />
        <Route element={<PrivateRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>
        <Route element={<PrivateRoute roles={["user", "admin"]} />}>
          <Route path="/dashboard/user" element={<DashboardUser />} />
        </Route>
        <Route element={<PrivateRoute roles={["veterinarian", "admin"]} />}>
          <Route path="/dashboard/doctor" element={<DashboardDoctor />} />
        </Route>
        <Route element={<PrivateRoute roles={["admin"]} />}>
          <Route path="/dashboard/admin" element={<DashboardAdmin />} />
        </Route>
      </Route>
    </Routes>
  );
}
