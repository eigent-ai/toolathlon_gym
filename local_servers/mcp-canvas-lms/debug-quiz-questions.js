#!/usr/bin/env node

// 深度调试：为什么学生看不到quiz questions
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'localhost:20001';

async function debugQuizQuestionAccess() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    console.log('🔍 深度调试：学生为什么看不到quiz questions');
    console.log('='.repeat(80));

    // 创建一个"宽松"的测验设置
    const course = await adminClient.createCourse({
      account_id: 1,
      name: `调试测验权限 ${Date.now()}`,
      course_code: `DEBUG-QUIZ-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });

    // 创建测验时使用更宽松的设置
    const quiz = await adminClient.createQuiz(course.id, {
      title: '调试权限测验',
      description: '用于调试学生权限问题',
      quiz_type: 'practice_quiz',  // 改为练习测验
      published: true,
      points_possible: 10,
      time_limit: null,  // 无时间限制
      allowed_attempts: -1,  // 无限制次数
      show_correct_answers: true,
      show_correct_answers_at: null,  // 立即显示
      one_question_at_a_time: false,  // 显示所有题目
      cant_go_back: false,
      shuffle_answers: false,
      hide_results: null  // 不隐藏结果
    });

    console.log(`✅ 创建测验: ${quiz.title} (ID: ${quiz.id})`);
    console.log(`   类型: ${quiz.quiz_type}`);
    console.log(`   显示正确答案: ${quiz.show_correct_answers}`);

    // 添加题目
    const question = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '调试题目',
      question_text: '这是一道用于调试的题目：2 + 3 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '4', weight: 0 },
        { text: '5', weight: 100 },
        { text: '6', weight: 0 }
      ]
    });

    console.log(`✅ 添加题目: ${question.question_name}`);

    // 注册学生
    const studentProfile = await studentClient.getUserProfile();
    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log(`✅ 学生已注册: ${studentProfile.name}`);

    // 详细检查submission流程
    console.log('\\n🎯 详细submission流程调试');
    console.log('-'.repeat(60));

    // 1. 开始测验
    console.log('\\n1️⃣ 开始测验');
    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    console.log('StartQuizAttempt 响应:');
    console.log(JSON.stringify(attemptResponse, null, 2));

    const submission = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;

    console.log('\\n📋 Submission 详情:');
    console.log(`  ID: ${submission.id}`);
    console.log(`  User ID: ${submission.user_id}`);
    console.log(`  Quiz ID: ${submission.quiz_id}`);
    console.log(`  Attempt: ${submission.attempt}`);
    console.log(`  状态: ${submission.workflow_state}`);
    console.log(`  开始时间: ${submission.started_at}`);
    console.log(`  结束时间: ${submission.finished_at}`);

    // 2. 获取submission的完整信息
    console.log('\\n2️⃣ 获取submission完整信息');
    try {
      const fullSubmission = await studentClient.client.get(`/courses/${course.id}/quizzes/${quiz.id}/submissions/${submission.id}`);
      console.log('完整submission信息:');
      console.log(JSON.stringify(fullSubmission.data, null, 2));
    } catch (error) {
      console.log(`获取完整submission失败: ${error.message}`);
    }

    // 3. 尝试不同的questions API调用
    console.log('\\n3️⃣ 尝试不同的API调用方式');

    // 方式A: 学生直接调用 courses API
    console.log('\\n📡 方式A: 学生 courses API（无参数）');
    try {
      const resp = await studentClient.client.get(`/courses/${course.id}/quizzes/${quiz.id}/questions`);
      console.log(`✅ 成功: ${resp.data.length} 个题目`);
      console.log('数据:', JSON.stringify(resp.data, null, 2));
    } catch (error) {
      console.log(`❌ 失败: ${error.response?.status} - ${error.message}`);
    }

    // 方式B: 学生调用 courses API 带参数
    console.log('\\n📡 方式B: 学生 courses API（带submission参数）');
    try {
      const url = `/courses/${course.id}/quizzes/${quiz.id}/questions?quiz_submission_id=${submission.id}&quiz_submission_attempt=${submission.attempt}`;
      const resp = await studentClient.client.get(url);
      console.log(`✅ 成功: ${resp.data.length} 个题目`);
      if (resp.data.length > 0) {
        console.log('题目内容:', JSON.stringify(resp.data, null, 2));
      }
    } catch (error) {
      console.log(`❌ 失败: ${error.response?.status} - ${error.message}`);
    }

    // 方式C: 学生调用 quiz_submissions API
    console.log('\\n📡 方式C: 学生 quiz_submissions API');
    try {
      const resp = await studentClient.client.get(`/quiz_submissions/${submission.id}/questions`);
      console.log(`✅ 成功: HTTP ${resp.status}`);
      console.log('完整响应:');
      console.log(JSON.stringify(resp.data, null, 2));

      // 检查是否有其他字段包含题目信息
      console.log('\\n🔍 分析响应结构:');
      console.log(`类型: ${typeof resp.data}`);
      console.log(`键: ${Object.keys(resp.data)}`);

      if (resp.data.quiz_submission_questions) {
        console.log(`quiz_submission_questions 长度: ${resp.data.quiz_submission_questions.length}`);
      }
    } catch (error) {
      console.log(`❌ 失败: ${error.response?.status} - ${error.message}`);
    }

    // 4. 对比：管理员获取同样的信息
    console.log('\\n4️⃣ 对比：管理员获取题目');
    try {
      const adminQuestions = await adminClient.client.get(`/courses/${course.id}/quizzes/${quiz.id}/questions`);
      console.log(`✅ 管理员成功: ${adminQuestions.data.length} 个题目`);
      if (adminQuestions.data.length > 0) {
        console.log('管理员看到的题目:');
        adminQuestions.data.forEach((q, i) => {
          console.log(`  ${i+1}. ${q.question_name}: ${q.question_text}`);
        });
      }
    } catch (error) {
      console.log(`❌ 管理员也失败: ${error.message}`);
    }

    // 5. 尝试管理员调用 quiz_submissions API
    console.log('\\n5️⃣ 管理员调用 quiz_submissions API');
    try {
      const adminSubResp = await adminClient.client.get(`/quiz_submissions/${submission.id}/questions`);
      console.log(`✅ 管理员 submission API 成功`);
      console.log('数据:', JSON.stringify(adminSubResp.data, null, 2));
    } catch (error) {
      console.log(`❌ 管理员 submission API 失败: ${error.message}`);
    }

    // 6. 检查测验的具体设置
    console.log('\\n6️⃣ 检查测验设置');
    const quizDetails = await adminClient.getQuiz(course.id, quiz.id);
    console.log('测验设置详情:');
    const relevantSettings = {
      quiz_type: quizDetails.quiz_type,
      published: quizDetails.published,
      one_question_at_a_time: quizDetails.one_question_at_a_time,
      cant_go_back: quizDetails.cant_go_back,
      show_correct_answers: quizDetails.show_correct_answers,
      show_correct_answers_at: quizDetails.show_correct_answers_at,
      hide_results: quizDetails.hide_results,
      question_count: quizDetails.question_count,
      allowed_attempts: quizDetails.allowed_attempts
    };
    console.log(JSON.stringify(relevantSettings, null, 2));

    // 7. 提交一个答案看看会不会改变
    console.log('\\n7️⃣ 提交答案后再试');
    try {
      await studentClient.submitQuizAttempt(
        course.id,
        quiz.id,
        submission.id,
        [{
          question_id: question.id,
          answer: question.answers.find(a => a.weight > 0).id
        }],
        submission.validation_token
      );
      console.log('✅ 答案已提交');

      // 再次尝试获取题目
      const afterSubmitResp = await studentClient.client.get(`/quiz_submissions/${submission.id}/questions`);
      console.log('提交后的 quiz_submissions 响应:');
      console.log(JSON.stringify(afterSubmitResp.data, null, 2));

    } catch (error) {
      console.log(`提交答案失败: ${error.message}`);
    }

    console.log('\\n' + '='.repeat(80));
    console.log('🎯 调试结论');
    console.log('='.repeat(80));
    console.log('如果所有方式都返回空，那么可能是:');
    console.log('1. Canvas实例的安全策略过于严格');
    console.log('2. 需要特定的API token权限范围');
    console.log('3. 测验类型或设置影响了API访问');
    console.log('4. Canvas版本差异');

  } catch (error) {
    console.error('\\n❌ 调试过程出错:', error.message);
    if (error.response?.data) {
      console.error('详情:', JSON.stringify(error.response.data, null, 2));
    }
  }
}

debugQuizQuestionAccess().catch(console.error);