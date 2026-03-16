// pages/broadcast/broadcast.js
Page({
  data: {
    broadcastActive: false,
    currentTime: '',
    currentProgram: '',
    programSchedule: [
      { time: '18:30-18:40', name: '新闻简报', active: false },
      { time: '18:40-19:00', name: '点歌台', active: false },
      { time: '19:00-19:20', name: '校园故事分享', active: false },
      { time: '19:20-19:30', name: '天气预报', active: false }
    ],
    featuredStories: [],
    backgroundMusic: '',
    loading: true
  },

  onLoad(options) {
    this.loadBroadcastData();
    this.initWebSocket();
    this.updateClock();
  },

  onUnload() {
    if (this.clockInterval) {
      clearInterval(this.clockInterval);
      this.clockInterval = null;
    }
  },

  initWebSocket() {
    const app = getApp();
    if (app.globalData.socketTask) {
      // 监听广播事件
      const broadcastListener = app.handleSocketMessage.bind(app, 'broadcast_update', (data) => {
        this.updateBroadcastDisplay(data);
      });
      
      this.broadcastListener = broadcastListener;
    }
  },

  updateClock() {
    this.clockInterval = setInterval(() => {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      this.setData({ currentTime: `${hours}:${minutes}` });
      
      // 检查是否在广播时间
      const isBroadcastTime = hours >= 18 && hours < 20;
      this.setData({ broadcastActive: isBroadcastTime });
      
      // 更新节目单激活状态
      const updatedSchedule = this.data.programSchedule.map(program => {
        const [start, end] = program.time.split('-');
        const startHour = parseInt(start.split(':')[0]);
        const startMin = parseInt(start.split(':')[1]);
        const endHour = parseInt(end.split(':')[0]);
        const endMin = parseInt(end.split(':')[1]);
        
        const currentTotal = now.getHours() * 60 + now.getMinutes();
        const startTotal = startHour * 60 + startMin;
        const endTotal = endHour * 60 + endMin;
        
        return {
          ...program,
          active: currentTotal >= startTotal && currentTotal < endTotal
        };
      });
      
      this.setData({ programSchedule: updatedSchedule });
    }, 1000);
  },

  loadBroadcastData() {
    // 从后端获取广播数据
    wx.request({
      url: 'http://localhost:5000/api/broadcast',
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          this.setData({
            featuredStories: res.data.data.stories || [],
            backgroundMusic: res.data.data.music || '',
            loading: false
          });
        } else {
          this.loadMockData();
        }
      },
      fail: () => {
        this.loadMockData();
      }
    });
  },

  loadMockData() {
    const mockStories = [
      {
        id: 'story_001',
        title: '那个帮你值日的同桌，现在还好吗？',
        content: '今天他偷偷帮我擦了黑板，就像当年的你...',
        author: '高一(1)班 李明',
        timestamp: '18:45'
      },
      {
        id: 'story_002', 
        title: '篮球场上的汗水',
        content: '夕阳下，他在看台上独自练习投篮，汗水闪闪发光',
        author: '高二(2)班 张伟',
        timestamp: '18:52'
      },
      {
        id: 'story_003',
        title: '草坪上的梦想',
        content: '好友分享零食，讨论着未来的大学和梦想',
        author: '高三(1)班 王芳',
        timestamp: '19:05'
      }
    ];

    this.setData({
      featuredStories: mockStories,
      backgroundMusic: '同桌的你',
      loading: false
    });
  },

  updateBroadcastDisplay(data) {
    this.setData({
      featuredStories: data.stories || this.data.featuredStories,
      backgroundMusic: data.music || this.data.backgroundMusic,
      currentProgram: data.currentProgram || this.data.currentProgram
    });
  },

  playStory(e) {
    const storyId = e.currentTarget.dataset.storyId;
    const story = this.data.featuredStories.find(s => s.id === storyId);
    
    if (story) {
      // 播放故事音频或显示详情
      wx.navigateTo({
        url: `/pages/story/story?storyId=${storyId}`
      });
    }
  },

  shareBroadcast() {
    wx.shareAppMessage({
      title: '青春回响 - 校园广播时间',
      path: '/pages/broadcast/broadcast',
      imageUrl: '/assets/broadcast_cover.jpg'
    });
  },

  onShareAppMessage() {
    return {
      title: '青春回响 - 校园广播黄金时段',
      path: '/pages/broadcast/broadcast',
      imageUrl: '/assets/broadcast_cover.jpg'
    };
  }
});