// pages/classroom/classroom.js
Page({
  data: {
    classId: '',
    className: '',
    students: [],
    loading: true,
    currentEvent: null,
    timeInfo: {
      day: 1,
      period: '上午',
      time: '08:00'
    }
  },

  onLoad(options) {
    const { schoolId } = options;
    this.setData({ classId: schoolId });
    this.loadClassroomData(schoolId);
    this.initWebSocket();
  },

  onUnload() {
    // 页面卸载时清理WebSocket监听
    if (this.socketListeners) {
      this.socketListeners.forEach(listener => listener());
      this.socketListeners = [];
    }
  },

  initWebSocket() {
    const app = getApp();
    if (app.globalData.socketTask) {
      // 监听班级更新事件
      const classUpdateListener = app.handleSocketMessage.bind(app, 'class_update', (data) => {
        if (data.classId === this.data.classId) {
          this.updateClassroomDisplay(data);
        }
      });
      
      // 监听事件通知
      const eventListener = app.handleSocketMessage.bind(app, 'event_notification', (data) => {
        this.showEventNotification(data);
      });

      this.socketListeners = [classUpdateListener, eventListener];
    }
  },

  loadClassroomData(classId) {
    // 从后端获取教室数据
    wx.request({
      url: 'http://localhost:5000/api/classroom/' + classId,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          this.setData({
            className: res.data.data.className,
            students: res.data.data.students,
            loading: false
          });
        }
      },
      fail: (err) => {
        console.error('加载教室数据失败', err);
        // 使用模拟数据作为备选
        this.loadMockData();
      }
    });
  },

  loadMockData() {
    // 模拟学生数据
    const mockStudents = [
      {
        id: 'student_001',
        name: '李明',
        avatar: '/assets/avatars/student1.png',
        mood: 'happy',
        energy: 85,
        relationships: { 'student_002': 70, 'student_003': 45 },
        skills: ['学习', '体育', '音乐']
      },
      {
        id: 'student_002', 
        name: '王芳',
        avatar: '/assets/avatars/student2.png',
        mood: 'normal',
        energy: 72,
        relationships: { 'student_001': 85, 'student_003': 60 },
        skills: ['学习', '艺术', '社交']
      },
      {
        id: 'student_003',
        name: '张伟',
        avatar: '/assets/avatars/student3.png', 
        mood: 'tired',
        energy: 60,
        relationships: { 'student_001': 40, 'student_002': 55 },
        skills: ['体育', '技术', '学习']
      }
    ];

    this.setData({
      className: '高一(1)班',
      students: mockStudents,
      loading: false
    });
  },

  updateClassroomDisplay(data) {
    // 更新教室显示
    this.setData({
      students: data.students,
      timeInfo: data.timeInfo || this.data.timeInfo
    });
  },

  showEventNotification(eventData) {
    // 显示事件通知
    this.setData({
      currentEvent: eventData
    });
    
    // 3秒后自动隐藏
    setTimeout(() => {
      this.setData({ currentEvent: null });
    }, 3000);
  },

  viewStudentDetail(e) {
    const studentId = e.currentTarget.dataset.studentId;
    wx.navigateTo({
      url: `/pages/student/student?studentId=${studentId}&classId=${this.data.classId}`
    });
  },

  handleInteraction(e) {
    const { studentId, action } = e.currentTarget.dataset;
    // 发送交互请求到后端
    wx.request({
      url: 'http://localhost:5000/api/interaction',
      method: 'POST',
      data: {
        classId: this.data.classId,
        studentId: studentId,
        action: action
      },
      success: (res) => {
        if (res.data.success) {
          // 刷新教室数据
          this.loadClassroomData(this.data.classId);
        }
      }
    });
  },

  onShareAppMessage() {
    return {
      title: `青春回响 - ${this.data.className}`,
      path: `/pages/classroom/classroom?schoolId=${this.data.classId}`,
      imageUrl: '/assets/share_classroom.jpg'
    };
  }
});