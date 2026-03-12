// app.js
App({
  onLaunch() {
    // 初始化WebSocket连接
    this.initWebSocket();
    
    // 获取用户信息
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: res => {
              this.globalData.userInfo = res.userInfo;
            }
          });
        }
      }
    });
  },
  
  initWebSocket() {
    // WebSocket连接配置
    const wsUrl = 'ws://localhost:5000/ws'; // 开发环境地址
    this.globalData.socketTask = wx.connectSocket({
      url: wsUrl,
      success: () => {
        console.log('WebSocket连接成功');
      },
      fail: (err) => {
        console.error('WebSocket连接失败', err);
      }
    });
    
    // 监听WebSocket消息
    wx.onSocketMessage((res) => {
      const data = JSON.parse(res.data);
      this.handleSocketMessage(data);
    });
  },
  
  handleSocketMessage(data) {
    // 处理服务器推送的消息
    switch(data.type) {
      case 'class_update':
        // 班级状态更新
        this.updateClassData(data.payload);
        break;
      case 'event_notification':
        // 事件通知
        this.showEventNotification(data.payload);
        break;
      default:
        break;
    }
  },
  
  globalData: {
    userInfo: null,
    socketTask: null,
    currentClassId: null,
    currentStudentId: null
  }
});