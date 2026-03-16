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
    },
    // 使用真实服务器地址
    apiUrl: 'http://172.16.45.229:5000'
  },

  onLoad(options) {
    const { schoolId } = options;
    this.setData({ classId: schoolId });
    this.loadClassroomData(schoolId);
    this.initWebSocket();
    
    // 开始模拟时间推进
    this.startTimeSimulation();
  },

  onUnload() {
    // 页面卸载时清理WebSocket监听和定时器
    if (this.socketListeners) {
      this.socketListeners.forEach(listener => listener());
      this.socketListeners = [];
    }
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  },

  initWebSocket() {
    const app = getApp();
    const socketUrl = 'ws://172.16.45.229:5000';
    
    // 创建WebSocket连接
    this.socketTask = wx.connectSocket({
      url: socketUrl,
      success: () => {
        console.log('WebSocket连接成功');
      },
      fail: (err) => {
        console.error('WebSocket连接失败', err);
      }
    });
    
    // 监听WebSocket消息
    wx.onSocketMessage((res) => {
      try {
        const data = JSON.parse(res.data);
        this.handleSocketMessage(data);
      } catch (e) {
        console.error('解析WebSocket消息失败', e);
      }
    });
    
    // 监听WebSocket连接打开
    wx.onSocketOpen(() => {
      // 加入班级房间
      wx.sendSocketMessage({
        data: JSON.stringify({
          type: 'join_class',
          class_id: this.data.classId
        })
      });
    });
  },

  startTimeSimulation() {
    // 模拟游戏时间推进（每秒现实时间 = 1分钟游戏时间）
    this.timeInterval = setInterval(() => {
      const now = new Date();
      const gameTime = new Date(now.getTime() + (now.getHours() * 60 + now.getMinutes()) * 60000);
      
      const timeInfo = {
        day: Math.floor(gameTime.getTime() / (24 * 60 * 60 * 1000)) % 7 + 1,
        period: this.getPeriod(gameTime.getHours()),
        time: `${gameTime.getHours().toString().padStart(2, '0')}:${gameTime.getMinutes().toString().padStart(2, '0')}`
      };
      
      this.setData({ timeInfo });
    }, 1000);
  },

  getPeriod(hour) {
    if (hour >= 6 && hour < 12) return '上午';
    if (hour >= 12 && hour < 18) return '下午';
    if (hour >= 18 && hour < 22) return '晚上';
    return '深夜';
  },

  handleSocketMessage(data) {
    // 处理服务器推送的消息
    switch(data.type) {
      case 'class_update':
        this.updateClassroomDisplay(data);
        break;
      case 'event_notification':
        this.showEventNotification(data);
        break;
      case 'student_behavior':
        this.updateStudentBehavior(data);
        break;
      default:
        break;
    }
  },

  loadClassroomData(classId) {
    // 从后端API获取教室数据
    wx.request({
      url: `${this.data.apiUrl}/api/classes/${classId}`,
      method: 'GET',
      success: (res) => {
        if (Array.isArray(res.data)) {
          // 获取班级信息
          wx.request({
            url: `${this.data.apiUrl}/api/students/${classId}`,
            method: 'GET',
            success: (studentsRes) => {
              if (Array.isArray(studentsRes.data)) {
                this.setData({
                  className: res.data[0]?.name || '未知班级',
                  students: studentsRes.data,
                  loading: false
                });
              } else {
                this.loadMockData();
              }
            },
            fail: (err) => {
              console.error('加载学生数据失败', err);
              this.loadMockData();
            }
          });
        } else {
          this.loadMockData();
        }
      },
      fail: (err) => {
        console.error('加载班级数据失败', err);
        this.loadMockData();
      }
    });
  },

  loadMockData() {
    // 模拟学生数据（备用）
    const mockStudents = [
      {
        id: 'student_001',
        name: '李明',
        avatar: '/assets/avatars/student1.png',
        mood: 'happy',
        energy: 85,
        social_points: 70,
        academic_points: 80,
        last_active: new Date().toISOString()
      },
      {
        id: 'student_002', 
        name: '王芳',
        avatar: '/assets/avatars/student2.png',
        mood: 'normal',
        energy: 72,
        social_points: 85,
        academic_points: 88,
        last_active: new Date().toISOString()
      },
      {
        id: 'student_003',
        name: '张伟',
        avatar: '/assets/avatars/student3.png', 
        mood: 'tired',
        energy: 60,
        social_points: 55,
        academic_points: 75,
        last_active: new Date().toISOString()
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
    if (data.students) {
      this.setData({
        students: data.students
      });
    }
    if (data.timeInfo) {
      this.setData({
        timeInfo: data.timeInfo
      });
    }
  },

  updateStudentBehavior(data) {
    // 更新单个学生行为
    const students = [...this.data.students];
    const index = students.findIndex(s => s.id === data.student_id);
    if (index !== -1) {
      students[index] = { ...students[index], ...data.updates };
      this.setData({ students });
    }
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
      url: `${this.data.apiUrl}/api/interaction`,
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