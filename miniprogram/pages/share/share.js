// pages/share/share.js
Page({
  data: {
    shareContent: '',
    shareImage: '',
    loading: false
  },

  onLoad(options) {
    // 获取要分享的内容
    const { content, image } = options;
    if (content) {
      this.setData({
        shareContent: decodeURIComponent(content),
        shareImage: image || '/assets/default_share.jpg'
      });
    }
  },

  onShareAppMessage() {
    return {
      title: this.data.shareContent || '青春回响 - 重回高中时代',
      path: '/pages/index/index',
      imageUrl: this.data.shareImage
    };
  },

  saveToAlbum() {
    const that = this;
    that.setData({ loading: true });
    
    wx.downloadFile({
      url: that.data.shareImage,
      success: function(res) {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: function() {
            wx.showToast({
              title: '保存成功',
              icon: 'success'
            });
          },
          fail: function() {
            wx.showToast({
              title: '保存失败',
              icon: 'error'
            });
          },
          complete: function() {
            that.setData({ loading: false });
          }
        });
      },
      fail: function() {
        wx.showToast({
          title: '下载失败',
          icon: 'error'
        });
        that.setData({ loading: false });
      }
    });
  },

  backToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
});