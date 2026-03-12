// pages/index/index.js
Page({
  data: {
    schools: [],
    loading: true,
    userInfo: null
  },
  
  onLoad() {
    this.loadUserInfo();
    this.loadSchools();
  },
  
  loadUserInfo() {
    const app = getApp();
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo
      });
    } else {
      // 监听用户信息变化
      app.userInfoReadyCallback = userInfo => {
        this.setData({
          userInfo: userInfo
        });
      };
    }
  },
  
  loadSchools() {
    // 模拟加载学校列表
    setTimeout(() => {
      this.setData({
        schools: [
          { id: 'school_001', name: '第一高中', classes: 3, students: 75 },
          { id: 'school_002', name: '第二高中', classes: 4, students: 100 },
          { id: 'school_003', name: '第三高中', classes: 5, students: 125 }
        ],
        loading: false
      });
    }, 1000);
  },
  
  selectSchool(e) {
    const schoolId = e.currentTarget.dataset.schoolId;
    wx.navigateTo({
      url: `/pages/classroom/classroom?schoolId=${schoolId}`
    });
  },
  
  onShareAppMessage() {
    return {
      title: '青春回响 - 重回高中时代',
      path: '/pages/index/index',
      imageUrl: '/assets/share_cover.jpg'
    };
  }
});