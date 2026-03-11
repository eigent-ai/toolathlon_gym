#!/usr/bin/env node

// Ignore self-signed certificate errors for testing
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'https://localhost:20001';

async function verifyEvents() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    // 快速创建测验
    const course = await adminClient.createCourse({
      account_id: 1,
      name: `Event Test ${Date.now()}`,
      course_code: `EVT-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });

    const quiz = await adminClient.createQuiz(course.id, {
      title: '验证测验',
      quiz_type: 'assignment',
      published: false,
      points_possible: 10
    });

    const q1 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '测试题',
      question_text: '1 + 1 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '1', weight: 0 },
        { text: '2', weight: 100 },
        { text: '3', weight: 0 }
      ]
    });

    await adminClient.updateQuiz(course.id, quiz.id, { published: true });

    const studentProfile = await studentClient.getUserProfile();
    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });

    await new Promise(resolve => setTimeout(resolve, 1000));

    // 学生开始测验
    console.log('开始测验...');
    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    const attempt = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;

    // 提交答案
    console.log('提交答案...');
    const correctAnswer = q1.answers.find(a => a.weight === 100);
    await studentClient.submitQuizAttempt(
      course.id,
      quiz.id,
      attempt.id,
      [{ question_id: q1.id, answer: correctAnswer.id }],
      attempt.validation_token
    );

    // 检查提交的events
    console.log('\n检查记录的events...');
    const eventsResponse = await adminClient.client.get(
      `/courses/${course.id}/quizzes/${quiz.id}/submissions/${attempt.id}/events`
    );

    console.log('记录的events:');
    console.log(JSON.stringify(eventsResponse.data, null, 2));

    // 获取最终提交状态
    const finalSubmission = await adminClient.client.get(
      `/courses/${course.id}/quizzes/${quiz.id}/submissions/${attempt.id}`
    );

    console.log('\n最终提交状态:');
    const submission = finalSubmission.data.quiz_submissions ?
      finalSubmission.data.quiz_submissions[0] : finalSubmission.data;
    console.log(`  状态: ${submission.workflow_state}`);
    console.log(`  得分: ${submission.score} / ${submission.quiz_points_possible}`);
    console.log(`  完成时间: ${submission.finished_at}`);

  } catch (error) {
    console.error('错误:', error.message);
  }
}

verifyEvents();