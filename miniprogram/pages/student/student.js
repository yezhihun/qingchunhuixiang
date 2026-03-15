// pages/student/student.js
Page({
  data: {
    student: null,
    loading: true,
    skills: [],
    relationships: [],
    currentClassId: ''
  },
  
  onLoad(options) {
    const { studentId, classId } = options;
    this.setData({
      currentClassId: classId
    });
    this.loadStudentData(studentId);
  },
  
  loadStudentData(studentId) {
    const app = getApp();
    
    // 从服务器获取学生详细信息
    wx.request({
      url: 'http://localhost:5000/api/students/' + studentId,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          this.setData({
            student: res.data.student,
            skills: res.data.skills || [],
            relationships: res.data.relationships || [],
            loading: false
          });
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'error'
          });
          this.setData({ loading: false });
        }
      },
      fail: (err) => {
        console.error('获取学生数据失败:', err);
        wx.showToast({
          title: '网络错误',
          icon: 'error'
        });
        this.setData({ loading: false });
      }
    });
  },
  
  // 与学生互动
  interactWithStudent(e) {
    const action = e.currentTarget.dataset.action;
    const studentId = this.data.student.id;
    
    wx.request({
      url: 'http://localhost:5000/api/interact',
      method: 'POST',
      data: {
        studentId: studentId,
        action: action,
        classId: this.data.currentClassId
      },
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: '互动成功',
            icon: 'success'
          });
          // 刷新学生数据
          this.loadStudentData(studentId);
        } else {
          wx.showToast({
            title: res.data.message || '互动失败',
            icon: 'error'
          });
        }
      },
      fail: (err) => {
        console.error('互动请求失败:', err);
        wx.showToast({
          title: '网络错误',
          icon: 'error'
        });
      }
    });
  },
  
  // 返回教室
  backToClassroom() {
    wx.navigateBack();
  },
  
  onShareAppMessage() {
    return {
      title: `了解${this.data.student?.name || '同学'}`,
      path: `/pages/student/student?studentId=${this.data.student?.id}&classId=${this.data.currentClassId}`,
      imageUrl: '/assets/share_student.jpg'
    };
  }
});