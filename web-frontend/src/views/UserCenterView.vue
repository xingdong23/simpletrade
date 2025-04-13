<template>
  <div>
    <!-- 顶部标签导航 -->
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="个人资料" name="profile">
        <div style="margin-bottom: 20px;">
          <el-row type="flex" justify="space-between" align="middle">
            <el-col :span="12">
              <h2 style="font-size: 20px; font-weight: 600; margin: 0;">个人资料</h2>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" icon="el-icon-edit" @click="editProfile">编辑资料</el-button>
            </el-col>
          </el-row>
        </div>
        
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <el-row :gutter="20">
            <el-col :span="6">
              <div style="text-align: center;">
                <el-avatar :size="120" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"></el-avatar>
                <el-button type="text" style="margin-top: 10px;">更换头像</el-button>
              </div>
            </el-col>
            <el-col :span="18">
              <el-descriptions title="基本信息" :column="2" border>
                <el-descriptions-item label="用户名">张三</el-descriptions-item>
                <el-descriptions-item label="注册时间">2023-01-15</el-descriptions-item>
                <el-descriptions-item label="邮箱">zhangsan@example.com</el-descriptions-item>
                <el-descriptions-item label="手机">138****1234</el-descriptions-item>
                <el-descriptions-item label="账户类型">个人投资者</el-descriptions-item>
                <el-descriptions-item label="账户状态">
                  <el-tag type="success">正常</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </el-col>
          </el-row>
        </el-card>
        
        <!-- 交易统计 -->
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <div slot="header" class="clearfix">
            <span>交易统计</span>
            <el-radio-group v-model="tradingStatsTimeframe" size="small" style="float: right;">
              <el-radio-button label="month">月</el-radio-button>
              <el-radio-button label="quarter">季</el-radio-button>
              <el-radio-button label="year">年</el-radio-button>
            </el-radio-group>
          </div>
          <el-row :gutter="20">
            <el-col :span="6">
              <div style="text-align: center;">
                <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">总交易次数</h3>
                <p style="font-size: 24px; font-weight: 600; color: #303133; margin: 0;">128</p>
              </div>
            </el-col>
            <el-col :span="6">
              <div style="text-align: center;">
                <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">盈利交易</h3>
                <p style="font-size: 24px; font-weight: 600; color: #67C23A; margin: 0;">75</p>
                <div style="margin-top: 10px; font-size: 14px; color: #909399;">
                  胜率: 58.6%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div style="text-align: center;">
                <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">亏损交易</h3>
                <p style="font-size: 24px; font-weight: 600; color: #F56C6C; margin: 0;">53</p>
                <div style="margin-top: 10px; font-size: 14px; color: #909399;">
                  亏损率: 41.4%
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div style="text-align: center;">
                <h3 style="margin: 0 0 10px; font-size: 16px; color: #606266;">总收益率</h3>
                <p style="font-size: 24px; font-weight: 600; color: #67C23A; margin: 0;">+12.5%</p>
                <div style="margin-top: 10px; font-size: 14px; color: #909399;">
                  超过市场: +5.2%
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
        
        <!-- 最近登录记录 -->
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>最近登录记录</span>
          </div>
          <el-table :data="loginRecords" style="width: 100%">
            <el-table-column prop="time" label="登录时间" width="180"></el-table-column>
            <el-table-column prop="ip" label="IP地址" width="180"></el-table-column>
            <el-table-column prop="location" label="登录地点" width="180"></el-table-column>
            <el-table-column prop="device" label="设备" width="180"></el-table-column>
            <el-table-column prop="status" label="状态">
              <template slot-scope="scope">
                <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'" size="small">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="账户设置" name="settings">
        <div style="margin-bottom: 20px;">
          <h2 style="font-size: 20px; font-weight: 600; margin: 0;">账户设置</h2>
        </div>
        
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <div slot="header" class="clearfix">
            <span>基本设置</span>
          </div>
          <el-form :model="settingsForm" label-width="120px">
            <el-form-item label="用户名">
              <el-input v-model="settingsForm.username"></el-input>
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="settingsForm.email"></el-input>
            </el-form-item>
            <el-form-item label="手机号码">
              <el-input v-model="settingsForm.phone"></el-input>
            </el-form-item>
            <el-form-item label="语言">
              <el-select v-model="settingsForm.language" style="width: 100%;">
                <el-option label="简体中文" value="zh-CN"></el-option>
                <el-option label="English" value="en-US"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="时区">
              <el-select v-model="settingsForm.timezone" style="width: 100%;">
                <el-option label="(GMT+08:00) 北京时间" value="Asia/Shanghai"></el-option>
                <el-option label="(GMT+00:00) 格林威治标准时间" value="GMT"></el-option>
                <el-option label="(GMT-05:00) 东部标准时间" value="America/New_York"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <div slot="header" class="clearfix">
            <span>安全设置</span>
          </div>
          <el-form label-width="120px">
            <el-form-item label="修改密码">
              <el-button type="primary" plain @click="changePassword">修改密码</el-button>
            </el-form-item>
            <el-form-item label="两步验证">
              <el-switch v-model="securitySettings.twoFactorAuth"></el-switch>
              <span style="margin-left: 10px; color: #909399; font-size: 14px;">
                {{ securitySettings.twoFactorAuth ? '已开启' : '未开启' }}
              </span>
            </el-form-item>
            <el-form-item label="登录通知">
              <el-switch v-model="securitySettings.loginNotification"></el-switch>
              <span style="margin-left: 10px; color: #909399; font-size: 14px;">
                {{ securitySettings.loginNotification ? '已开启' : '未开启' }}
              </span>
            </el-form-item>
            <el-form-item label="异常登录保护">
              <el-switch v-model="securitySettings.unusualLoginProtection"></el-switch>
              <span style="margin-left: 10px; color: #909399; font-size: 14px;">
                {{ securitySettings.unusualLoginProtection ? '已开启' : '未开启' }}
              </span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>通知设置</span>
          </div>
          <el-form label-width="200px">
            <el-form-item label="交易执行通知">
              <el-switch v-model="notificationSettings.tradeExecution"></el-switch>
            </el-form-item>
            <el-form-item label="价格提醒通知">
              <el-switch v-model="notificationSettings.priceAlert"></el-switch>
            </el-form-item>
            <el-form-item label="系统公告通知">
              <el-switch v-model="notificationSettings.systemAnnouncement"></el-switch>
            </el-form-item>
            <el-form-item label="市场分析报告通知">
              <el-switch v-model="notificationSettings.marketAnalysis"></el-switch>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="订阅管理" name="subscription">
        <div style="margin-bottom: 20px;">
          <h2 style="font-size: 20px; font-weight: 600; margin: 0;">订阅管理</h2>
        </div>
        
        <!-- 当前订阅 -->
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <div slot="header" class="clearfix">
            <span>当前订阅</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div style="text-align: center; padding: 20px; border: 1px solid #EBEEF5; border-radius: 4px;">
                <h3 style="margin: 0 0 10px; font-size: 18px; color: #303133;">专业版</h3>
                <div style="font-size: 24px; font-weight: 600; color: #409EFF; margin-bottom: 10px;">¥299/月</div>
                <el-tag type="success">当前订阅</el-tag>
                <ul style="text-align: left; margin-top: 20px; padding-left: 20px;">
                  <li>实时市场数据</li>
                  <li>高级图表分析</li>
                  <li>AI策略推荐</li>
                  <li>无限策略创建</li>
                  <li>优先客户支持</li>
                </ul>
                <div style="margin-top: 20px; color: #909399; font-size: 14px;">
                  到期时间: 2023-12-15
                </div>
                <el-button type="danger" plain style="margin-top: 20px;">取消订阅</el-button>
              </div>
            </el-col>
          </el-row>
        </el-card>
        
        <!-- 可用订阅计划 -->
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>可用订阅计划</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div style="text-align: center; padding: 20px; border: 1px solid #EBEEF5; border-radius: 4px;">
                <h3 style="margin: 0 0 10px; font-size: 18px; color: #303133;">基础版</h3>
                <div style="font-size: 24px; font-weight: 600; color: #303133; margin-bottom: 20px;">¥99/月</div>
                <ul style="text-align: left; padding-left: 20px;">
                  <li>延迟市场数据</li>
                  <li>基础图表分析</li>
                  <li>最多3个策略</li>
                  <li>标准客户支持</li>
                </ul>
                <el-button type="primary" plain style="margin-top: 20px;">降级到此计划</el-button>
              </div>
            </el-col>
            <el-col :span="8">
              <div style="text-align: center; padding: 20px; border: 1px solid #EBEEF5; border-radius: 4px; background-color: #F5F7FA;">
                <h3 style="margin: 0 0 10px; font-size: 18px; color: #303133;">专业版</h3>
                <div style="font-size: 24px; font-weight: 600; color: #409EFF; margin-bottom: 20px;">¥299/月</div>
                <el-tag type="success">当前订阅</el-tag>
                <ul style="text-align: left; margin-top: 20px; padding-left: 20px;">
                  <li>实时市场数据</li>
                  <li>高级图表分析</li>
                  <li>AI策略推荐</li>
                  <li>无限策略创建</li>
                  <li>优先客户支持</li>
                </ul>
              </div>
            </el-col>
            <el-col :span="8">
              <div style="text-align: center; padding: 20px; border: 1px solid #EBEEF5; border-radius: 4px;">
                <h3 style="margin: 0 0 10px; font-size: 18px; color: #303133;">企业版</h3>
                <div style="font-size: 24px; font-weight: 600; color: #303133; margin-bottom: 20px;">¥999/月</div>
                <ul style="text-align: left; padding-left: 20px;">
                  <li>实时市场数据</li>
                  <li>高级图表分析</li>
                  <li>AI策略推荐</li>
                  <li>无限策略创建</li>
                  <li>专属客户经理</li>
                  <li>API访问</li>
                  <li>多用户管理</li>
                </ul>
                <el-button type="primary" style="margin-top: 20px;">升级到此计划</el-button>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 修改密码对话框 -->
    <el-dialog title="修改密码" :visible.sync="passwordDialogVisible" width="40%">
      <el-form :model="passwordForm" label-width="120px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.currentPassword" type="password"></el-input>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password"></el-input>
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordChange">确认修改</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'UserCenterView',
  data() {
    return {
      activeTab: 'profile',
      tradingStatsTimeframe: 'month',
      passwordDialogVisible: false,
      loginRecords: [
        {
          time: '2023-10-15 14:30:25',
          ip: '192.168.1.1',
          location: '北京',
          device: 'Chrome / Windows',
          status: '成功'
        },
        {
          time: '2023-10-14 09:15:10',
          ip: '192.168.1.1',
          location: '北京',
          device: 'Safari / iOS',
          status: '成功'
        },
        {
          time: '2023-10-12 18:45:32',
          ip: '118.24.63.156',
          location: '上海',
          device: 'Firefox / macOS',
          status: '成功'
        },
        {
          time: '2023-10-10 22:10:45',
          ip: '45.76.192.88',
          location: '美国',
          device: 'Chrome / Windows',
          status: '失败'
        }
      ],
      settingsForm: {
        username: '张三',
        email: 'zhangsan@example.com',
        phone: '13812341234',
        language: 'zh-CN',
        timezone: 'Asia/Shanghai'
      },
      securitySettings: {
        twoFactorAuth: true,
        loginNotification: true,
        unusualLoginProtection: true
      },
      notificationSettings: {
        tradeExecution: true,
        priceAlert: true,
        systemAnnouncement: false,
        marketAnalysis: true
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    editProfile() {
      this.$message({
        message: '进入编辑模式',
        type: 'info'
      });
    },
    saveSettings() {
      this.$message({
        message: '设置已保存',
        type: 'success'
      });
    },
    changePassword() {
      this.passwordDialogVisible = true;
    },
    submitPasswordChange() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        this.$message({
          message: '两次输入的密码不一致',
          type: 'error'
        });
        return;
      }
      
      this.$message({
        message: '密码修改成功',
        type: 'success'
      });
      this.passwordDialogVisible = false;
      
      // 清空表单
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
    },
    saveSecuritySettings() {
      this.$message({
        message: '安全设置已保存',
        type: 'success'
      });
    },
    saveNotificationSettings() {
      this.$message({
        message: '通知设置已保存',
        type: 'success'
      });
    }
  }
}
</script>

<style>
.el-tabs__header {
  margin-bottom: 25px;
}
</style>
