import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/users'
import LoadingScreen from '@/components/LoadingScreen.vue'
import HomeView from '../views/HomeView.vue';
import SurveyBot from '../components/SurveyBot.vue';
import SignUpView from '@/views/SignUpView.vue'
import SignInView from '@/views/SignInView.vue'
import BankMapView from '@/views/BankMapView.vue';
import MyPageView from '@/views/MyPageView.vue';
import MyPage from '@/components/MyPage.vue';
import ProductListView from '@/views/ProductListView.vue';
import ProductCompareView from '@/views/ProductCompareView.vue';
import PopupMenu from '@/components/PopupMenu.vue';
import ExchangeView from '@/views/ExchangeView.vue';
import NewsView from '@/views/NewsView.vue';
import CommunityView from '@/views/CommunityView.vue';
import UserUpdateView from '@/views/UserUpdateView.vue';
import RecommendationView from '@/views/RecommendationView.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'LoadingScreen',
      component: LoadingScreen, // 처음 로딩 화면
    },
    {
      path: '/main',
      name: 'Main',
      component: HomeView,
    },
    {
      path: '/survey',
      name: 'Survey',
      component: SurveyBot,
    },
    {
      path: '/recommendation',
      name: 'Recommendation',
      component: RecommendationView,
    },
    {
      path: '/login',
      name: 'login',
      component: SignInView,
      beforeEnter: (to, from, next) => {
        // 로그인 페이지로 이동 전 현재 경로를 `redirect`에 저장
        if (!to.query.redirect && from.name) {
          next({
            ...to,
            query: { redirect: from.fullPath },
          });
        } else {
          next();
        }
      },
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUpView,
      beforeEnter: (to, from, next) => {
        // 로그인 페이지로 이동 전 현재 경로를 `redirect`에 저장
        if (!to.query.redirect && from.name) {
          next({
            ...to,
            query: { redirect: from.fullPath },
          });
        } else {
          next();
        }
      },
    },
    {
      path: '/survey',
      name: 'survey',
      component: SurveyBot,
      meta: { requiresAuth: true }, // 인증 필요
    },
    {
      path: "/nearBank",
      name: "nearBank",
      component: BankMapView,
    },
    {
      path: '/mypage/:username*',
      name: 'mypage',
      component: MyPageView,
      beforeEnter: (to, from) => {
        const userStore = useUserStore();
        if (!userStore.isLogin) {
          alert('로그인 후 이용 가능합니다.');
          return { name: 'login' };
        }
      },
      children: [
        {
          path: '',
          name: 'myPage',
          component: MyPage,
        },
      ],
    },
    {
      path: '/user/update',
      name: 'userUpdate',
      component: UserUpdateView,
      beforeEnter: (to, from, next) => {
        const userStore = useUserStore();
        if (!userStore.isLogin) {
          alert('로그인이 필요합니다.');
          next({ name: 'login', query: { redirect: to.fullPath } });
        } else {
          next();
        }
      },
    },
    {
      path: "/productList",
      name: "productList",
      component: ProductListView,
    },
    {
      path: "/productcompare",
      name: "productcompare",
      component: ProductCompareView
    },
    { 
      path: '/popup-menu',
      name: 'PopupMenu',
      component: PopupMenu 
    },
  { 
    path: '/exchange',
    name: 'Exchange',
    component: ExchangeView,
  },
  { 
    path: '/news',
    name: 'News',
    component: NewsView,
  },
  {
    path: '/community',
    name: 'Community',
    component: CommunityView,
  },
  ]
});

export function resetRouter() {
  const newRouter = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
  });
  router.matcher = newRouter.matcher;
}

export default router;
