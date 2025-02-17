# keygen-demo
### 前提
1. 安装python
2. 在阿里云-计算巢部署KeyGen服务端

### 代码流程
命令行进入app文件夹，执行：
#### 1. 获取KeygenPolicyId和KeygenToken:
    python app.py [--username USERNAME] [--password PASSWORD] [--product_name PRODUCT_NAME] [--policy_name POLICY_NAME]
    
参数说明：

    --username：计算巢创建Keygen平台的用户名。
    --password：对应的密码。
    --product_name：你的产品的名称。 
    --policy_name：你想要创建或使用的策略名称。

将返回结果KeygenPolicyId和KeygenToken写入env.properties文件中
#### 2. 执行License生命周期代码:
    python keygen.py