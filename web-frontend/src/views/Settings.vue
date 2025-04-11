<template>
  <div class="settings-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>系统设置</span>
      </div>
      
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="交易接口" name="gateways">
          <el-button type="primary" icon="el-icon-plus" @click="addGateway" style="margin-bottom: 20px;">添加接口</el-button>
          <el-table :data="gatewaySettings" style="width: 100%">
            <el-table-column prop="name" label="接口名称" width="150"></el-table-column>
            <el-table-column prop="type" label="接口类型" width="100"></el-table-column>
            <el-table-column prop="status" label="连接状态" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.status === 'connected' ? 'success' : 'danger'">
                  {{ scope.row.status === 'connected' ? '已连接' : '未连接' }}
                </el-tag>
              </template>
            </el-table-column>
             <el-table-column label="账户ID/Key" prop="accountId"></el-table-column>
            <el-table-column label="操作" width="200">
              <template slot-scope="scope">
                 <el-button size="mini" @click="editGateway(scope.row)">编辑</el-button>
                 <el-button size="mini" type="danger" @click="deleteGateway(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="数据源" name="dataSources">
           <el-button type="primary" icon="el-icon-plus" @click="addDataSource" style="margin-bottom: 20px;">添加数据源</el-button>
           <el-table :data="dataSourceSettings" style="width: 100%">
             <el-table-column prop="name" label="数据源名称" width="150"></el-table-column>
             <el-table-column prop="type" label="类型" width="150"></el-table-column>
             <el-table-column prop="details" label="配置详情"></el-table-column>
              <el-table-column label="操作" width="200">
              <template slot-scope="scope">
                 <el-button size="mini" @click="editDataSource(scope.row)">编辑</el-button>
                 <el-button size="mini" type="danger" @click="deleteDataSource(scope.row)">删除</el-button>
              </template>
            </el-table-column>
           </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="通知设置" name="notifications">
          <el-form label-width="120px">
            <el-form-item label="微信通知">
              <el-switch v-model="notificationSettings.wechat.enabled"></el-switch>
              <el-input v-if="notificationSettings.wechat.enabled" v-model="notificationSettings.wechat.webhook" placeholder="请输入企业微信Webhook地址" style="margin-left: 20px; width: 300px;"></el-input>
            </el-form-item>
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationSettings.email.enabled"></el-switch>
              <el-input v-if="notificationSettings.email.enabled" v-model="notificationSettings.email.recipient" placeholder="请输入收件人邮箱" style="margin-left: 20px; width: 300px;"></el-input>
            </el-form-item>
             <!-- Add more notification types if needed -->
             <el-form-item>
                 <el-button type="primary" @click="saveNotificationSettings">保存通知设置</el-button>
             </el-form-item>
          </el-form>
        </el-tab-pane>

         <el-tab-pane label="通用设置" name="general">
           <el-form label-width="150px">
              <el-form-item label="界面主题">
                  <el-radio-group v-model="generalSettings.theme">
                      <el-radio label="light">浅色</el-radio>
                      <el-radio label="dark">深色</el-radio>
                  </el-radio-group>
              </el-form-item>
              <el-form-item label="默认下单数量">
                  <el-input-number v-model="generalSettings.defaultOrderVolume" :min="1"></el-input-number>
              </el-form-item>
               <!-- Add other general settings -->
               <el-form-item>
                 <el-button type="primary" @click="saveGeneralSettings">保存通用设置</el-button>
             </el-form-item>
           </el-form>
         </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Dialog for adding/editing gateway -->
    <el-dialog :title="gatewayDialog.title" :visible.sync="gatewayDialog.visible" width="50%">
       <el-form :model="gatewayDialog.form" label-width="120px">
           <el-form-item label="接口名称">
              <el-input v-model="gatewayDialog.form.name"></el-input>
           </el-form-item>
           <el-form-item label="接口类型">
              <el-select v-model="gatewayDialog.form.type">
                <el-option label="老虎证券" value="tiger"></el-option>
                <el-option label="盈透证券" value="ib"></el-option>
                <el-option label="CTP" value="ctp"></el-option>
                <!-- Add more types -->
              </el-select>
           </el-form-item>
           <!-- Add fields for API Key, Secret, Account ID, Server Address etc. based on type -->
           <el-form-item label="Account ID">
               <el-input v-model="gatewayDialog.form.accountId"></el-input>
           </el-form-item>
            <el-form-item label="API Key">
               <el-input v-model="gatewayDialog.form.apiKey" show-password></el-input>
           </el-form-item>
           <el-form-item label="API Secret">
               <el-input v-model="gatewayDialog.form.apiSecret" show-password></el-input>
           </el-form-item>
       </el-form>
        <span slot="footer" class="dialog-footer">
            <el-button @click="gatewayDialog.visible = false">取消</el-button>
            <el-button type="primary" @click="saveGateway">确定</el-button>
        </span>
    </el-dialog>

     <!-- Dialog for adding/editing data source -->
    <el-dialog :title="dataSourceDialog.title" :visible.sync="dataSourceDialog.visible" width="50%">
       <el-form :model="dataSourceDialog.form" label-width="120px">
            <el-form-item label="数据源名称">
              <el-input v-model="dataSourceDialog.form.name"></el-input>
           </el-form-item>
            <el-form-item label="数据源类型">
              <el-select v-model="dataSourceDialog.form.type">
                <el-option label="本地CSV" value="local_csv"></el-option>
                <el-option label="数据库" value="database"></el-option>
                <el-option label="Tushare" value="tushare"></el-option>
                <!-- Add more types -->
              </el-select>
           </el-form-item>
           <!-- Add fields for path, connection string, token etc. based on type -->
           <el-form-item label="路径/连接串">
               <el-input v-model="dataSourceDialog.form.connection"></el-input>
           </el-form-item>
            <el-form-item label="Token/密码">
               <el-input v-model="dataSourceDialog.form.token" show-password></el-input>
           </el-form-item>
       </el-form>
        <span slot="footer" class="dialog-footer">
            <el-button @click="dataSourceDialog.visible = false">取消</el-button>
            <el-button type="primary" @click="saveDataSource">确定</el-button>
        </span>
    </el-dialog>

  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      activeTab: 'gateways',
      gatewaySettings: [
        // Placeholder data
        { id: 'gw1', name: '我的老虎账户', type: 'tiger', status: 'connected', accountId: 'U1234567' },
        { id: 'gw2', name: 'CTP模拟', type: 'ctp', status: 'disconnected', accountId: '99999' }
      ],
      dataSourceSettings: [
          // Placeholder data
          { id: 'ds1', name: '本地分钟数据', type: 'local_csv', details: '/data/csv/1min'},
          { id: 'ds2', name: 'Tushare Pro', type: 'tushare', details: 'Token: ****'}
      ],
      notificationSettings: {
        wechat: { enabled: false, webhook: '' },
        email: { enabled: true, recipient: 'user@example.com' }
      },
      generalSettings: {
          theme: 'light',
          defaultOrderVolume: 100,
      },
      gatewayDialog: {
          visible: false,
          title: '',
          form: { id: null, name: '', type: '', accountId: '', apiKey: '', apiSecret: '' }
      },
      dataSourceDialog: {
          visible: false,
          title: '',
          form: { id: null, name: '', type: '', connection: '', token: '' }
      }
    }
  },
  methods: {
    addGateway() {
      this.gatewayDialog.title = '添加交易接口';
      this.gatewayDialog.form = { id: null, name: '', type: '', accountId: '', apiKey: '', apiSecret: '' };
      this.gatewayDialog.visible = true;
    },
    editGateway(row) {
      this.gatewayDialog.title = '编辑交易接口';
      // IMPORTANT: Clone the row data to avoid modifying table data directly
      this.gatewayDialog.form = { ...row, apiKey: '********', apiSecret: '********' }; // Mask secrets
      this.gatewayDialog.visible = true;
    },
    deleteGateway(row) {
       this.$confirm(`确定要删除接口 ${row.name} 吗?`, '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // TODO: Call API to delete gateway
        console.log('Delete gateway:', row);
        this.gatewaySettings = this.gatewaySettings.filter(g => g.id !== row.id); // Remove locally for demo
        this.$message({ type: 'success', message: '删除成功 (模拟)' });
      }).catch(() => {
        this.$message({ type: 'info', message: '已取消删除' });
      });
    },
     saveGateway() {
        // TODO: Call API to save (add or update) gateway
        const isEditing = !!this.gatewayDialog.form.id;
        console.log('Saving gateway:', this.gatewayDialog.form);
        // Simulate save
        if (isEditing) {
            const index = this.gatewaySettings.findIndex(g => g.id === this.gatewayDialog.form.id);
            if (index !== -1) {
                // Update existing item (merge changes, don't overwrite secrets if not provided)
                 Object.assign(this.gatewaySettings[index], { ...this.gatewayDialog.form, apiKey: '********', apiSecret: '********' });
            }
        } else {
            this.gatewaySettings.push({ ...this.gatewayDialog.form, id: `gw${Date.now()}`, status: 'disconnected' }); // Add new
        }
         this.$message.success('保存成功 (模拟)');
         this.gatewayDialog.visible = false;
    },

    addDataSource() {
       this.dataSourceDialog.title = '添加数据源';
       this.dataSourceDialog.form = { id: null, name: '', type: '', connection: '', token: '' };
       this.dataSourceDialog.visible = true;
    },
    editDataSource(row) {
        this.dataSourceDialog.title = '编辑数据源';
        this.dataSourceDialog.form = { ...row, token: '********' }; // Mask secrets
        this.dataSourceDialog.visible = true;
    },
    deleteDataSource(row) {
        this.$confirm(`确定要删除数据源 ${row.name} 吗?`, '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // TODO: Call API to delete data source
        console.log('Delete data source:', row);
        this.dataSourceSettings = this.dataSourceSettings.filter(ds => ds.id !== row.id);
        this.$message({ type: 'success', message: '删除成功 (模拟)' });
      }).catch(() => {
        this.$message({ type: 'info', message: '已取消删除' });
      });
    },
    saveDataSource() {
        // TODO: Call API to save data source
        const isEditing = !!this.dataSourceDialog.form.id;
        console.log('Saving data source:', this.dataSourceDialog.form);
         if (isEditing) {
            const index = this.dataSourceSettings.findIndex(ds => ds.id === this.dataSourceDialog.form.id);
            if (index !== -1) {
                 Object.assign(this.dataSourceSettings[index], { ...this.dataSourceDialog.form, token: '********' });
            }
        } else {
            this.dataSourceSettings.push({ ...this.dataSourceDialog.form, id: `ds${Date.now()}` });
        }
        this.$message.success('保存成功 (模拟)');
        this.dataSourceDialog.visible = false;
    },

    saveNotificationSettings() {
      // TODO: Call API to save notification settings
      console.log('Saving notification settings:', this.notificationSettings);
      this.$message.success('通知设置已保存 (模拟)');
    },
     saveGeneralSettings() {
       // TODO: Call API to save general settings
       console.log('Saving general settings:', this.generalSettings);
       this.$message.success('通用设置已保存 (模拟)');
       // Potentially apply theme change immediately
    }
  },
  created() {
    // TODO: Load settings from backend on creation
  }
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
.el-select, .el-input-number {
    width: 100%;
}
</style> 