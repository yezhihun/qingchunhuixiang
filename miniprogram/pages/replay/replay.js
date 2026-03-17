// pages/replay/replay.js
Page({
  data: {
    replayType: 'daily', // daily, weekly, memory
    replayData: null,
    loading: true,
    apiUrl: 'http://172.16.45.229:5000'
  },

  onLoad(options) {
    const { type = 'daily' } = options;
    this.setData({ replayType: type });
    this.loadReplayData(type);
  },

  loadReplayData(type) {
    wx.request({
      url: `${this.data.apiUrl}/api/replay/${type}`,
      method: 'GET',
      success: (res) => {
        if (res.data) {
          this.setData({
            replayData: res.data,
            loading: false
          });
        }
      },
      fail: (err) => {
        console.error('加载回放数据失败', err);
        this.setData({ loading: false });
      }
    });
  },

  onShareAppMessage() {
    if (this.data.replayData) {
      return {
        title: this.data.replayData.title || '青春回响 - 班级回忆',
        path: `/pages/replay/replay?type=${this.data.replayType}`,
        imageUrl: '/assets/share_replay.jpg'
      };
    }
  },

  shareReplay() {
    if (!this.data.replayData) return;
    
    // 生成分享图片
    wx.canvasToTempFilePath({
      canvasId: 'replayCanvas',
      success: (res) => {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => {
            wx.showToast({ title: '已保存到相册' });
          }
        });
      }
    });
  },

  viewStudentDetail(e) {
    const studentId = e.currentTarget.dataset.studentId;
    wx.navigateTo({
      url: `/pages/student/student?studentId=${studentId}`
    });
  }
});