// pages/skills/skills.js
Page({
  data: {
    studentId: null,
    skills: [],
    loading: true
  },

  onLoad(options) {
    if (options.studentId) {
      this.setData({ studentId: options.studentId });
      this.loadStudentSkills(options.studentId);
    }
  },

  loadStudentSkills(studentId) {
    // 从全局数据或API获取学生技能
    const app = getApp();
    
    // 模拟技能数据
    setTimeout(() => {
      this.setData({
        skills: [
          { id: 'academic', name: '学业能力', level: 75, max: 100, color: '#4299e1' },
          { id: 'social', name: '社交能力', level: 60, max: 100, color: '#48bb78' },
          { id: 'athletic', name: '体育能力', level: 45, max: 100, color: '#ed8936' },
          { id: 'artistic', name: '艺术天赋', level: 80, max: 100, color: '#9f7aea' },
          { id: 'leadership', name: '领导力', level: 30, max: 100, color: '#e53e3e' }
        ],
        loading: false
      });
    }, 800);
  },

  onSkillClick(e) {
    const skillId = e.currentTarget.dataset.skillId;
    wx.showToast({
      title: `提升 ${this.data.skills.find(s => s.id === skillId).name}`,
      icon: 'none'
    });
    
    // 这里可以添加技能提升逻辑
    // 通过WebSocket发送到后端
  },

  onBackToStudent() {
    wx.navigateBack();
  }
});