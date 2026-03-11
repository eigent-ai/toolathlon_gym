#!/usr/bin/env node

// Ignore self-signed certificate errors for testing
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'localhost:20001';

console.log('='.repeat(60));
console.log(' 🔍 验证答案是否真正提交');
console.log('='.repeat(60));

async function testRealSubmission() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    const adminProfile = await adminClient.getUserProfile();
    const studentProfile = await studentClient.getUserProfile();

    // 创建课程和测验
    console.log('\n📚 创建测试环境');
    console.log('-'.repeat(40));

    const course = await adminClient.createCourse({
      account_id: 1,
      name: `答案提交测试 ${Date.now()}`,
      course_code: `SUBMIT-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });
    console.log(`课程: ${course.name}`);

    const quiz = await adminClient.createQuiz(course.id, {
      title: '三道题测验',
      quiz_type: 'assignment',
      published: false,
      points_possible: 30,
      show_correct_answers: true,
      show_correct_answers_at: new Date().toISOString()
    });
    console.log(`测验: ${quiz.title}`);

    // 添加题目
    const q1 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '加法题',
      question_text: '3 + 5 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '7', weight: 0 },
        { text: '8', weight: 100 },
        { text: '9', weight: 0 }
      ]
    });
    console.log(`\n题目1 (ID ${q1.id}): 3 + 5 = ?`);
    q1.answers.forEach(a => console.log(`  - ${a.text} (ID: ${a.id}, 权重: ${a.weight})`));

    const q2 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '地理题',
      question_text: '日本的首都是东京。',
      question_type: 'true_false_question',
      points_possible: 10,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ]
    });
    console.log(`\n题目2 (ID ${q2.id}): 日本的首都是东京。`);
    console.log(`  - True (正确) / False (错误)`);

    // 获取True选项的ID
    const trueAnswer = q2.answers.find(a => a.text === 'True');
    console.log(`  True选项的ID: ${trueAnswer.id}`);

    const q3 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '填空题',
      question_text: '一年有多少个月？',
      question_type: 'short_answer_question',
      points_possible: 10,
      answers: [
        { text: '12', weight: 100 },
        { text: '十二', weight: 100 }
      ]
    });
    console.log(`\n题目3 (ID ${q3.id}): 一年有多少个月？`);
    console.log(`  - 正确答案: 12 或 十二`);

    await adminClient.updateQuiz(course.id, quiz.id, { published: true });
    console.log('\n✅ 测验已发布');

    // 注册学生
    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log(`✅ 学生已注册`);

    await new Promise(resolve => setTimeout(resolve, 1000));

    // 学生开始测验
    console.log('\n\n🎯 学生开始测验');
    console.log('-'.repeat(40));

    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    const attempt = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;
    console.log(`Submission ID: ${attempt.id}`);
    console.log(`Validation Token: ${attempt.validation_token}`);

    // 准备正确答案
    const correctAnswer = q1.answers.find(a => a.weight === 100);
    console.log(`\n正确答案的ID: ${correctAnswer.id} (文本: ${correctAnswer.text})`);
    console.log(`答案ID的类型: ${typeof correctAnswer.id}`);

    const studentAnswers = [
      {
        question_id: q1.id,
        answer: correctAnswer.id  // 单选题：使用answer_id
      },
      {
        question_id: q2.id,
        answer: trueAnswer.id  // 判断题：也使用answer_id而不是true
      },
      {
        question_id: q3.id,
        answer: '12'  // 简答题：文本答案
      }
    ];

    console.log('\n📝 提交的答案:');
    studentAnswers.forEach(a => {
      console.log(`  问题 ${a.question_id}: ${a.answer} (类型: ${typeof a.answer})`);
    });

    // 提交答案
    console.log('\n📮 提交中...');
    const submission = await studentClient.submitQuizAttempt(
      course.id,
      quiz.id,
      attempt.id,
      studentAnswers,
      attempt.validation_token
    );

    console.log('\n✅ 提交响应:');
    const result = submission.quiz_submissions ? submission.quiz_submissions[0] : submission;
    console.log(`  状态: ${result.workflow_state}`);
    console.log(`  得分: ${result.score} / ${result.quiz_points_possible}`);
    console.log(`  完成时间: ${result.finished_at}`);

    // 验证得分
    if (result.score > 0) {
      console.log('\n🎉 成功！答案确实被提交并计分了！');
      console.log(`   得分率: ${(result.score / result.quiz_points_possible * 100).toFixed(1)}%`);
    } else {
      console.log('\n⚠️ 得分为0，可能的原因:');
      console.log('  1. 答案格式仍有问题');
      console.log('  2. Canvas需要时间处理评分');
      console.log('  3. 需要教师手动批改');
    }

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    if (error.response?.data) {
      console.error('详情:', JSON.stringify(error.response.data, null, 2));
    }
  }
}

testRealSubmission().catch(console.error);