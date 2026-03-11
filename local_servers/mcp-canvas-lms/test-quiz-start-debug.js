#!/usr/bin/env node

import { CanvasClient } from './build/client.js';
import * as dotenv from 'dotenv';
import axios from 'axios';
import https from 'https';

// Load environment variables
dotenv.config();

// 忽略自签名证书
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const API_TOKEN = process.env.CANVAS_API_TOKEN;
const DOMAIN = process.env.CANVAS_DOMAIN;

if (!API_TOKEN || !DOMAIN) {
  console.error('❌ 缺少必要的环境变量: CANVAS_API_TOKEN 和 CANVAS_DOMAIN');
  process.exit(1);
}

console.log('='.repeat(80));
console.log(' Canvas Quiz Start 500 错误诊断');
console.log('='.repeat(80));
console.log(`域名: ${DOMAIN}`);
console.log(`Token: ${API_TOKEN.substring(0, 10)}...`);
console.log('');

async function diagnoseQuizStart() {
  // 创建客户端
  const client = new CanvasClient(API_TOKEN, DOMAIN);

  // 使用你的具体测试数据
  const courseId = 28;
  const quizId = 12;

  console.log(`📚 课程ID: ${courseId}`);
  console.log(`📝 测验ID: ${quizId}`);
  console.log('');

  try {
    // 第一步：先获取测验详情
    console.log('1️⃣ 获取测验详细信息...');
    const quizDetails = await client.client.get(`/courses/${courseId}/quizzes/${quizId}`);
    console.log('✅ 成功获取测验详情:');
    console.log(`   标题: ${quizDetails.data.title}`);
    console.log(`   类型: ${quizDetails.data.quiz_type}`);
    console.log(`   发布状态: ${quizDetails.data.published ? '已发布' : '未发布'}`);
    console.log(`   锁定状态: ${quizDetails.data.locked_for_user ? '已锁定' : '未锁定'}`);
    console.log(`   需要访问码: ${quizDetails.data.access_code ? '是' : '否'}`);
    console.log(`   需要锁定浏览器: ${quizDetails.data.require_lockdown_browser ? '是' : '否'}`);
    console.log(`   可用时间: ${quizDetails.data.due_at || '无限制'}`);
    console.log(`   开放时间: ${quizDetails.data.unlock_at || '立即开放'}`);
    console.log(`   关闭时间: ${quizDetails.data.lock_at || '无限制'}`);
    console.log('');

    // 第二步：检查现有的提交
    console.log('2️⃣ 检查现有的测验提交...');
    try {
      const existingSubmissions = await client.client.get(
        `/courses/${courseId}/quizzes/${quizId}/submissions`,
        {
          params: {
            include: ['submission', 'quiz', 'user']
          }
        }
      );
      console.log(`✅ 找到 ${existingSubmissions.data.quiz_submissions?.length || 0} 个现有提交`);

      if (existingSubmissions.data.quiz_submissions?.length > 0) {
        const latestSubmission = existingSubmissions.data.quiz_submissions[0];
        console.log('   最新提交:');
        console.log(`     ID: ${latestSubmission.id}`);
        console.log(`     尝试次数: ${latestSubmission.attempt}`);
        console.log(`     状态: ${latestSubmission.workflow_state}`);
        console.log(`     开始时间: ${latestSubmission.started_at}`);
        console.log(`     完成时间: ${latestSubmission.finished_at || '进行中'}`);

        // 如果有正在进行的提交，可能是问题所在
        if (latestSubmission.workflow_state === 'untaken' ||
            latestSubmission.workflow_state === 'pending_review') {
          console.log('   ⚠️  警告: 存在未完成的测验提交，这可能导致创建新提交失败');
        }
      }
    } catch (error) {
      console.log(`❌ 获取现有提交失败: ${error.message}`);
    }
    console.log('');

    // 第三步：尝试使用不同的方法开始测验
    console.log('3️⃣ 尝试开始新的测验尝试...');
    console.log('');

    // 方法A: 直接POST（原始方法）
    console.log('方法A: 直接POST请求（无参数）');
    try {
      const response = await client.client.post(
        `/courses/${courseId}/quizzes/${quizId}/submissions`
      );
      console.log('✅ 成功创建测验提交（方法A）');
      console.log('   响应:', JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.log(`❌ 方法A失败: ${error.message}`);
      if (error.response) {
        console.log(`   状态码: ${error.response.status}`);
        console.log(`   错误响应:`, error.response.data);
        if (error.response.data?.errors) {
          error.response.data.errors.forEach((err, i) => {
            console.log(`   错误${i+1}: ${err.message}`);
          });
        }
      }
    }
    console.log('');

    // 方法B: 带参数的POST请求
    console.log('方法B: POST请求（带access_code参数）');
    try {
      const response = await client.client.post(
        `/courses/${courseId}/quizzes/${quizId}/submissions`,
        {
          access_code: ''  // 空字符串表示没有访问码
        }
      );
      console.log('✅ 成功创建测验提交（方法B）');
      console.log('   响应:', JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.log(`❌ 方法B失败: ${error.message}`);
      if (error.response?.data?.errors) {
        error.response.data.errors.forEach((err, i) => {
          console.log(`   错误${i+1}: ${err.message}`);
        });
      }
    }
    console.log('');

    // 方法C: 带完整参数的POST请求
    console.log('方法C: POST请求（带完整参数）');
    try {
      const response = await client.client.post(
        `/courses/${courseId}/quizzes/${quizId}/submissions`,
        {
          quiz_submissions: [{
            access_code: null,
            preview: false
          }]
        }
      );
      console.log('✅ 成功创建测验提交（方法C）');
      console.log('   响应:', JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.log(`❌ 方法C失败: ${error.message}`);
      if (error.response?.data?.errors) {
        error.response.data.errors.forEach((err, i) => {
          console.log(`   错误${i+1}: ${err.message}`);
        });
      }
    }
    console.log('');

    // 第四步：直接使用axios测试，绕过client封装
    console.log('4️⃣ 使用原始axios请求测试...');
    const axiosClient = axios.create({
      baseURL: `https://${DOMAIN}/api/v1`,
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });

    try {
      const response = await axiosClient.post(
        `/courses/${courseId}/quizzes/${quizId}/submissions`
      );
      console.log('✅ 原始axios请求成功');
      console.log('   响应:', JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.log(`❌ 原始axios请求失败: ${error.message}`);
      if (error.response) {
        console.log(`   状态码: ${error.response.status}`);
        console.log(`   错误响应:`, JSON.stringify(error.response.data, null, 2));
      }
    }

  } catch (error) {
    console.error('❌ 诊断过程中出错:', error.message);
    if (error.stack) {
      console.error('堆栈:', error.stack);
    }
  }
}

// 运行诊断
diagnoseQuizStart().catch(console.error);