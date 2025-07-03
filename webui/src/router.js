import { createRouter, createWebHistory } from "vue-router"

// ALLE Imports direkt am Anfang!
import Login from "./views/Login.vue"
import Dashboard from "./views/Dashboard.vue"
import Packages from "./views/Packages.vue"
import Groups from "./views/Groups.vue"
import Payments from "./views/Payments.vue"
import Debug from "./views/Debug.vue"
import TestUrl from "./views/TestUrl.vue"
import NotFound from "./views/NotFound.vue"
import Monitoring from "./views/Monitoring.vue"
import PackageDetails from "./views/PackageDetails.vue"
import SignalGroups from "./views/SignalGroups.vue"

// Admin Imports
import UserManager from "./views/admin/UserManager.vue"
import PackageManager from "./views/admin/PackageManager.vue"
import PartnerManager from "./views/admin/PartnerManager.vue"
import SignalGroupsManager from "./views/admin/SignalGroupsManager.vue"

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/debug", component: Debug },
  { path: "/test-url", component: TestUrl },
  { path: "/dashboard", component: Dashboard },
  { path: "/packages", component: Packages },
  { path: "/packages/details/:id", component: PackageDetails },
  { path: "/groups", component: Groups },
  { path: "/payments", component: Payments },
  { path: "/monitoring", component: Monitoring },
  { path: "/signal-groups", component: SignalGroups },
  
  // Admin Routes
  { path: "/admin/users", component: UserManager },
  { path: "/admin/packages", component: PackageManager },
  { path: "/admin/partners", component: PartnerManager },
  { path: "/admin/signal-groups", component: SignalGroupsManager },
  
  {
    path: "/:pathMatch(.*)*",
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Expliziter Export
export default router
