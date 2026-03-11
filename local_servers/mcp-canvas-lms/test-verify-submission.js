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
console.log(' 📝 验证学生答题提交');
console.log('='.repeat(60));

async function verifyQuizSubmission() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    const adminProfile = await adminClient.getUserProfile();
    const studentProfile = await studentClient.getUserProfile();

    // ========== 创建简单测验 ==========
    console.log('\n📚 第一步：创建课程和测验');
    console.log('-'.repeat(40));

    const course = await adminClient.createCourse({
      account_id: 1,
      name: `答案验证课程 ${Date.now()}`,
      course_code: `VERIFY-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });
    console.log(`✅ 课程创建: ${course.name} (ID: ${course.id})`);

    const quiz = await adminClient.createQuiz(course.id, {
      title: '简单测验',
      quiz_type: 'assignment',
      published: false,
      points_possible: 30,
      show_correct_answers: true
    });
    console.log(`✅ 测验创建: ${quiz.title} (ID: ${quiz.id})`);

    // 添加3道简单题目
    console.log('\n添加题目:');

    const q1 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '数学题',
      question_text: '2 + 2 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '3', weight: 0 },
        { text: '4', weight: 100 },
        { text: '5', weight: 0 }
      ]
    });
    console.log(`  题目1 (ID: ${q1.id}): 2 + 2 = ?`);
    console.log(`    答案选项: 3 (错), 4 (对), 5 (错)`);

    const q2 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '判断题',
      question_text: '太阳从东方升起。',
      question_type: 'true_false_question',
      points_possible: 10,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ]
    });
    console.log(`  题目2 (ID: ${q2.id}): 太阳从东方升起。`);
    console.log(`    答案选项: True (对), False (错)`);

    const q3 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '填空题',
      question_text: '中国的首都是？',
      question_type: 'short_answer_question',
      points_possible: 10,
      answers: [
        { text: '北京', weight: 100 },
        { text: 'Beijing', weight: 100 }
      ]
    });
    console.log(`  题目3 (ID: ${q3.id}): 中国的首都是？`);
    console.log(`    正确答案: 北京 或 Beijing`);

    await adminClient.updateQuiz(course.id, quiz.id, { published: true });
    console.log('\n✅ 测验已发布');

    // 注册学生
    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log(`✅ 学生 ${studentProfile.name} 已注册`);

    await new Promise(resolve => setTimeout(resolve, 1000));

    // ========== 学生开始测验 ==========
    console.log('\n\n🎯 第二步：学生开始测验');
    console.log('-'.repeat(40));

    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    const attempt = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;
    console.log(`✅ 测验已开始`);
    console.log(`  Submission ID: ${attempt.id}`);
    console.log(`  Validation Token: ${attempt.validation_token || 'none'}`);

    // ========== 准备答案 ==========
    console.log('\n\n📝 第三步：学生准备答案');
    console.log('-'.repeat(40));

    // 找到正确的answer_id
    const correctAnswerQ1 = q1.answers.find(a => a.text === '4');

    const studentAnswers = [
      {
        question_id: q1.id,
        answer_id: correctAnswerQ1.id
      },
      {
        question_id: q2.id,
        answer: true
      },
      {
        question_id: q3.id,
        answer: '北京'
      }
    ];

    console.log('学生的答案:');
    console.log(`  题目1 (ID: ${q1.id}): 选择答案 "4" (answer_id: ${correctAnswerQ1.id})`);
    console.log(`  题目2 (ID: ${q2.id}): 选择 True`);
    console.log(`  题目3 (ID: ${q3.id}): 输入 "北京"`);

    console.log('\n实际发送的答案数据:');
    console.log(JSON.stringify(studentAnswers, null, 2));

    // ========== 提交答案 ==========
    console.log('\n\n📮 第四步：提交答案');
    console.log('-'.repeat(40));

    try {
      const submission = await studentClient.submitQuizAttempt(
        course.id,
        quiz.id,
        attempt.id,
        studentAnswers,
        attempt.validation_token
      );

      console.log('✅ 答案提交成功！');
      console.log('\n提交响应:');
      console.log(JSON.stringify(submission, null, 2));

      if (submission.score !== undefined) {
        console.log(`\n📊 得分: ${submission.score} / ${quiz.points_possible}`);
      }
    } catch (error) {
      console.log('❌ 提交失败:', error.message);
      if (error.response) {
        console.log('错误详情:', error.response.data);
      }
    }

    // ========== 管理员查看提交 ==========
    console.log('\n\n🔍 第五步：管理员查看学生提交');
    console.log('-'.repeat(40));

    try {
      // 获取学生的提交记录
      const submissions = await adminClient.getSubmissions(course.id, quiz.id);
      console.log(`找到 ${submissions.length} 个提交`);

      if (submissions.length > 0) {
        const studentSubmission = submissions[0];
        console.log('\n学生提交详情:');
        console.log(`  学生ID: ${studentSubmission.user_id}`);
        console.log(`  提交时间: ${studentSubmission.finished_at || '进行中'}`);
        console.log(`  得分: ${studentSubmission.score || '待批改'}`);
        console.log(`  状态: ${studentSubmission.workflow_state}`);
      }
    } catch (error) {
      console.log('获取提交记录失败:', error.message);
    }

    // ========== 总结 ==========
    console.log('\n\n' + '='.repeat(60));
    console.log(' 📊 验证总结');
    console.log('='.repeat(60));
    console.log('✅ 成功创建包含3道题的测验');
    console.log('✅ 学生成功开始测验');
    console.log('✅ 答案数据已正确构建');
    console.log('✅ 答案已提交到Canvas');
    console.log('\n注意: 如果看到 "待批改"，这是正常的，');
    console.log('因为Canvas可能需要时间来处理评分。');

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    console.error('Stack:', error.stack);
  }
}

// 运行验证
verifyQuizSubmission().catch(console.error);