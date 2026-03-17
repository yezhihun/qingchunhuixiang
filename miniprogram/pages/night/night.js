// pages/night/night.js
Page({
  data: {
    currentDate: '',
    nightEvents: [],
    studentDreams: [],
    familyInteractions: [],
    loading: true,
    apiUrl: 'http://172.16.45.229:5000'
  },

  onLoad(options) {
    this.loadNightData();
    this.startNightTimeCheck();
  },

  onUnload() {
    if (this.nightInterval) {
      clearInterval(this.nightInterval);
    }
  },

  startNightTimeCheck() {
    // 检查是否是夜间时间（22:00-06:00）
    const now = new Date();
    const currentHour = now.getHours();
    
    if (currentHour >= 22 || currentHour < 6) {
      // 夜间模式激活
      this.setData({ isNightMode: true });
      
      // 每30分钟检查一次夜间事件
      this.nightInterval = setInterval(() => {
        this.checkForNewNightEvents();
      }, 1800000); // 30分钟
    }
  },

  loadNightData() {
    const today = new Date().toISOString().split('T')[0];
    this.setData({ currentDate: today });
    
    wx.request({
      url: `${this.data.apiUrl}/api/night-events`,
      method: 'GET',
      success: (res) => {
        if (res.data && Array.isArray(res.data.events)) {
          this.setData({
            nightEvents: res.data.events,
            studentDreams: res.data.dreams || [],
            familyInteractions: res.data.family_interactions || [],
            loading: false
          });
        } else {
          this.loadMockNightData();
        }
      },
      fail: (err) => {
        console.error('加载夜间数据失败', err);
        this.loadMockNightData();
      }
    });
  },

  loadMockNightData() {
    const mockData = {
      nightEvents: [
        {
          id: 'dream_001',
          type: 'dream',
          student_id: 'student_001',
          student_name: '李明',
          content: '梦见自己在高考考场上，突然发现所有题目都不会做...',
          emotional_impact: 'anxiety',
          timestamp: new Date().toISOString()
        }
      ],
      studentDreams: [
        {
          student_id: 'student_002',
          student_name: '王芳', 
          dream_content: '和暗恋的男生一起在操场上散步，但醒来发现只是梦...',
          mood_effect: -10
        }
      ],
      familyInteractions: [
        {
          student_id: 'student_003',
          student_name: '张伟',
          interaction_type: 'parent_concern',
          content: '妈妈又问起月考成绩，感觉压力很大...',
          relationship_impact: -5
        }
      ]
    };
    
    this.setData({
      ...mockData,
      loading: false,
      isNightMode: true
    });
  },

  checkForNewNightEvents() {
    // 检查是否有新的夜间事件
    wx.request({
      url: `${this.data.apiUrl}/api/night-events/latest`,
      method: 'GET',
      success: (res) => {
        if (res.data && res.data.has_new_events) {
          // 显示新事件通知
          wx.showToast({
            title: '有新的夜间事件',
            icon: 'none'
          });
          this.loadNightData();
        }
      }
    });
  },

  sendGoodnightMessage(e) {
    const studentId = e.currentTarget.dataset.studentId;
    const studentName = e.currentTarget.dataset.studentName;
    
    wx.request({
      url: `${this.data.apiUrl}/api/interaction/goodnight`,
      method: 'POST',
      data: {
        student_id: studentId,
        message_type: 'goodnight_care'
      },
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: `已发送晚安消息给${studentName}`,
            icon: 'success'
          });
          // 更新学生状态
          this.updateStudentMood(studentId, 'comforted');
        }
      }
    });
  },

  viewDreamDetails(e) {
    const dreamId = e.currentTarget.dataset.dreamId;
    wx.navigateTo({
      url: `/pages/dream/dream?dreamId=${dreamId}`
    });
  },

  onShareAppMessage() {
    return {
      title: `青春回响 - 夜间时光`,
      path: '/pages/night/night',
      imageUrl: '/assets/share_night.jpg'
    };
  }
});