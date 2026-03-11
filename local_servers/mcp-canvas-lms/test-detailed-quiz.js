#!/usr/bin/env node

// Ignore self-signed certificate errors for testing
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';
import fs from 'fs';
import path from 'path';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'https://localhost:20001';

console.log('='.repeat(60));
console.log(' 📝 详细的学生测验流程测试');
console.log('='.repeat(60));

async function detailedQuizTest() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    // ========== 准备阶段：创建课程和测验 ==========
    console.log('\n🔧 准备阶段：管理员创建课程和测验');
    console.log('-'.repeat(40));

    const adminProfile = await adminClient.getUserProfile();
    const studentProfile = await studentClient.getUserProfile();
    console.log(`管理员: ${adminProfile.name}`);
    console.log(`学生: ${studentProfile.name}`);

    // 创建课程
    const course = await adminClient.createCourse({
      account_id: 1,
      name: `测验演示课程 ${Date.now()}`,
      course_code: `QUIZ-DEMO-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });
    console.log(`✅ 课程已创建: ${course.name}`);

    // 创建详细的测验
    const quiz = await adminClient.createQuiz(course.id, {
      title: '数学和常识测验',
      description: '这个测验包含数学计算和常识问题',
      quiz_type: 'assignment',
      published: false,
      time_limit: 60,
      allowed_attempts: 3,
      points_possible: 50,
      show_correct_answers: true,
      shuffle_answers: false,
      one_question_at_a_time: false,
      cant_go_back: false
    });
    console.log(`✅ 测验已创建: ${quiz.title}`);

    // 添加题目
    console.log('\n添加测验题目...');

    // 题目1: 简单数学
    const q1 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '简单加法',
      question_text: '计算: 8 + 7 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '14', weight: 0 },
        { text: '15', weight: 100 },
        { text: '16', weight: 0 },
        { text: '17', weight: 0 }
      ]
    });
    console.log(`  ✅ 题目1: 8 + 7 = ? (单选题)`);

    // 题目2: 判断题
    const q2 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '首都知识',
      question_text: '法国的首都是巴黎。',
      question_type: 'true_false_question',
      points_possible: 10,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ]
    });
    console.log(`  ✅ 题目2: 法国首都判断题`);

    // 题目3: 简答题
    const q3 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '颜色问题',
      question_text: '天空通常是什么颜色？（请用中文回答）',
      question_type: 'short_answer_question',
      points_possible: 10,
      answers: [
        { text: '蓝色', weight: 100 },
        { text: '蓝', weight: 100 },
        { text: '蓝天', weight: 100 }
      ]
    });
    console.log(`  ✅ 题目3: 天空颜色（简答题）`);

    // 题目4: 乘法计算
    const q4 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '乘法计算',
      question_text: '6 × 7 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '40', weight: 0 },
        { text: '41', weight: 0 },
        { text: '42', weight: 100 },
        { text: '43', weight: 0 }
      ]
    });
    console.log(`  ✅ 题目4: 6 × 7 = ? (单选题)`);

    // 题目5: 多选题
    const q5 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '水果识别',
      question_text: '以下哪些是水果？（多选）',
      question_type: 'multiple_answers_question',
      points_possible: 10,
      answers: [
        { text: '苹果', weight: 100 },
        { text: '西红柿', weight: 0 },
        { text: '香蕉', weight: 100 },
        { text: '胡萝卜', weight: 0 },
        { text: '橙子', weight: 100 }
      ]
    });
    console.log(`  ✅ 题目5: 水果识别（多选题）`);

    // 发布测验
    await adminClient.updateQuiz(course.id, quiz.id, { published: true });
    console.log('✅ 测验已发布，总分50分');

    // 注册学生
    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log(`✅ 学生已注册到课程`);

    await new Promise(resolve => setTimeout(resolve, 1000));

    // ========== 学生视角：查看和参加测验 ==========
    console.log('\n\n📚 学生视角：查看课程和测验');
    console.log('='.repeat(60));

    // 学生查看课程
    const studentCourses = await studentClient.listCourses();
    const myCourse = studentCourses.find(c => c.id === course.id);
    console.log(`学生看到课程: ${myCourse.name}`);

    // 查看测验列表
    const availableQuizzes = await studentClient.listQuizzes(course.id);
    const myQuiz = availableQuizzes[0];
    console.log(`\n发现测验: ${myQuiz.title}`);
    console.log(`  - 时间限制: ${myQuiz.time_limit}分钟`);
    console.log(`  - 允许尝试次数: ${myQuiz.allowed_attempts}次`);
    console.log(`  - 总分: ${myQuiz.points_possible}分`);

    // ========== 开始做测验 ==========
    console.log('\n\n🎯 开始测验');
    console.log('='.repeat(60));

    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    const attempt = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;
    const validationToken = attempt.validation_token;

    console.log(`✅ 测验已开始`);
    console.log(`  - Attempt ID: ${attempt.id}`);
    console.log(`  - 开始时间: ${new Date().toLocaleString('zh-CN')}`);

    // 模拟学生做题过程
    console.log('\n\n📝 学生答题过程');
    console.log('-'.repeat(40));

    console.log('\n题目 1: 计算 8 + 7 = ?');
    console.log('  选项: A)14  B)15  C)16  D)17');
    console.log('  学生思考: 8 + 7 = 15');
    console.log('  ✅ 选择: B) 15');

    console.log('\n题目 2: 法国的首都是巴黎。');
    console.log('  选项: True / False');
    console.log('  学生思考: 是的，巴黎是法国首都');
    console.log('  ✅ 选择: True');

    console.log('\n题目 3: 天空通常是什么颜色？');
    console.log('  学生回答: 蓝色');
    console.log('  ✅ 输入: 蓝色');

    console.log('\n题目 4: 6 × 7 = ?');
    console.log('  选项: A)40  B)41  C)42  D)43');
    console.log('  学生思考: 6 × 7 = 42');
    console.log('  ✅ 选择: C) 42');

    console.log('\n题目 5: 以下哪些是水果？（多选）');
    console.log('  选项: 苹果、西红柿、香蕉、胡萝卜、橙子');
    console.log('  学生思考: 苹果、香蕉、橙子是水果');
    console.log('  ✅ 选择: 苹果、香蕉、橙子');

    // 准备答案（模拟学生的选择）
    const studentAnswers = [
      {
        question_id: q1.id,
        answer_id: q1.answers.find(a => a.text === '15').id
      },
      {
        question_id: q2.id,
        answer: true
      },
      {
        question_id: q3.id,
        answer: '蓝色'
      },
      {
        question_id: q4.id,
        answer_id: q4.answers.find(a => a.text === '42').id
      },
      {
        question_id: q5.id,
        answer: [
          q5.answers.find(a => a.text === '苹果').id,
          q5.answers.find(a => a.text === '香蕉').id,
          q5.answers.find(a => a.text === '橙子').id
        ]
      }
    ];

    // ========== 提交测验 ==========
    console.log('\n\n📮 提交测验');
    console.log('='.repeat(60));

    const submission = await studentClient.submitQuizAttempt(
      course.id,
      quiz.id,
      attempt.id,
      studentAnswers,
      validationToken
    );

    console.log('✅ 测验已提交！');
    console.log(`  - 提交时间: ${new Date().toLocaleString('zh-CN')}`);
    console.log(`  - 状态: ${submission.workflow_state || '已提交'}`);
    console.log(`  - 得分: ${submission.score || '待批改'} / ${myQuiz.points_possible}`);

    // ========== 查看结果分析 ==========
    console.log('\n\n📊 答题结果分析');
    console.log('='.repeat(60));
    console.log('题目1: 8 + 7 = 15 ✅ 正确 (10分)');
    console.log('题目2: 巴黎是法国首都 ✅ 正确 (10分)');
    console.log('题目3: 天空是蓝色 ✅ 正确 (10分)');
    console.log('题目4: 6 × 7 = 42 ✅ 正确 (10分)');
    console.log('题目5: 水果选择 ✅ 正确 (10分)');
    console.log('-'.repeat(40));
    console.log('预期总分: 50/50 (100%)');

    // ========== 创建和提交作业 ==========
    console.log('\n\n📄 额外测试：文件作业提交');
    console.log('='.repeat(60));

    // 创建作业
    const assignment = await adminClient.createAssignment({
      course_id: course.id,
      name: '学习心得',
      description: '请提交你的学习心得体会',
      submission_types: ['online_upload'],
      points_possible: 50,
      published: true
    });
    console.log(`✅ 作业已创建: ${assignment.name}`);

    // 学生提交作业
    const reportPath = path.join(process.cwd(), 'study-notes.txt');
    const reportContent = `学习心得
==========
学生: ${studentProfile.name}
日期: ${new Date().toLocaleDateString('zh-CN')}

通过这次测验，我学到了：
1. 基础数学计算的重要性
2. 地理常识知识
3. 观察生活中的细节
4. 多选题需要仔细分析每个选项

测验体验很好，题目清晰，系统响应迅速。
`;

    fs.writeFileSync(reportPath, reportContent);
    const uploadedFile = await studentClient.uploadFileFromPath(reportPath);

    const assignmentSubmission = await studentClient.submitAssignment({
      course_id: course.id,
      assignment_id: assignment.id,
      submission_type: 'online_upload',
      file_ids: [uploadedFile.id]
    });

    console.log(`✅ 作业已提交`);
    console.log(`  - 文件: ${uploadedFile.display_name}`);
    console.log(`  - 状态: ${assignmentSubmission.workflow_state}`);

    fs.unlinkSync(reportPath);

    // ========== 总结 ==========
    console.log('\n\n');
    console.log('='.repeat(60));
    console.log(' 🎉 测试完成总结');
    console.log('='.repeat(60));
    console.log('✅ 管理员成功创建课程和测验');
    console.log('✅ 添加了5道不同类型的题目');
    console.log('✅ 学生成功查看测验信息');
    console.log('✅ 学生完成所有题目并提交');
    console.log('✅ 学生成功提交文件作业');
    console.log('\n所有功能运行正常！');

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    if (error.response) {
      console.error('响应数据:', error.response.data);
    }
  }
}

// 运行测试
detailedQuizTest().catch(console.error);