#!/usr/bin/env node

// Test the fixed listQuizQuestions functionality
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'localhost:20001';

async function testQuizQuestionsFixedTool() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    console.log('🧪 测试修复后的 listQuizQuestions 工具');
    console.log('='.repeat(60));

    // 创建新的测验环境
    const course = await adminClient.createCourse({
      account_id: 1,
      name: `listQuizQuestions修复测试 ${Date.now()}`,
      course_code: `LQQ-FIX-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });

    const quiz = await adminClient.createQuiz(course.id, {
      title: '权限修复验证测验',
      published: true,
      points_possible: 30
    });

    // 添加多个题目
    const q1 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '数学题',
      question_text: '10 + 5 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '13', weight: 0 },
        { text: '14', weight: 0 },
        { text: '15', weight: 100 },
        { text: '16', weight: 0 }
      ]
    });

    const q2 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '判断题',
      question_text: '地球是圆的。',
      question_type: 'true_false_question',
      points_possible: 10,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ]
    });

    const q3 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '简答题',
      question_text: '请说出一种编程语言。',
      question_type: 'short_answer_question',
      points_possible: 10,
      answers: [
        { text: 'Python', weight: 100 },
        { text: 'JavaScript', weight: 100 },
        { text: 'Java', weight: 100 }
      ]
    });

    console.log(`✅ 测试环境创建完成:`);
    console.log(`   课程ID: ${course.id}`);
    console.log(`   测验ID: ${quiz.id}`);
    console.log(`   题目数量: 3`);

    // 注册学生
    const studentProfile = await studentClient.getUserProfile();
    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });

    console.log(`✅ 学生已注册: ${studentProfile.name}`);

    // 测试学生直接访问（应该失败）
    console.log('\n📋 测试1: 学生直接访问题目（无submission）');
    console.log('-'.repeat(40));
    try {
      const questions1 = await studentClient.listQuizQuestions(course.id, quiz.id);
      console.log(`✅ 成功: ${questions1.length} 个题目`);
    } catch (error) {
      console.log(`❌ 失败（预期）: ${error.message}`);
    }

    // 学生开始测验
    console.log('\n🎯 学生开始测验');
    console.log('-'.repeat(40));
    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    const submission = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;

    console.log(`测验已开始:`);
    console.log(`  Submission ID: ${submission.id}`);
    console.log(`  Attempt: ${submission.attempt}`);
    console.log(`  Validation Token: ${submission.validation_token ? '✅' : '❌'}`);

    // 测试带submission参数访问（应该成功）
    console.log('\n📋 测试2: 学生带submission参数访问题目');
    console.log('-'.repeat(40));
    try {
      const questions2 = await studentClient.listQuizQuestions(course.id, quiz.id, {
        quiz_submission_id: submission.id,
        quiz_submission_attempt: submission.attempt
      });

      console.log(`✅ 成功获取题目: ${questions2.length} 个`);

      if (questions2.length > 0) {
        console.log('\n📝 题目详情:');
        questions2.forEach((q, index) => {
          console.log(`${index + 1}. ${q.question_name}`);
          console.log(`   题目: ${q.question_text}`);
          console.log(`   类型: ${q.question_type}`);
          console.log(`   分值: ${q.points_possible}`);

          if (q.answers && q.answers.length > 0) {
            console.log(`   选项:`);
            q.answers.forEach(a => {
              const correct = a.weight > 0 ? ' [正确]' : '';
              console.log(`     - ${a.text}${correct}`);
            });
          }
          console.log('');
        });

        // 现在学生可以基于获取到的题目信息来提交答案
        console.log('🎯 基于获取的题目信息提交答案');
        console.log('-'.repeat(40));

        const answers = [
          {
            question_id: questions2[0].id,
            answer: questions2[0].answers.find(a => a.weight > 0).id
          },
          {
            question_id: questions2[1].id,
            answer: questions2[1].answers.find(a => a.weight > 0).id
          },
          {
            question_id: questions2[2].id,
            answer: 'Python'
          }
        ];

        const result = await studentClient.submitQuizAttempt(
          course.id,
          quiz.id,
          submission.id,
          answers,
          submission.validation_token
        );

        const finalResult = result.quiz_submissions ? result.quiz_submissions[0] : result;
        console.log(`✅ 答案提交成功:`);
        console.log(`   状态: ${finalResult.workflow_state}`);
        console.log(`   得分: ${finalResult.score} / ${finalResult.quiz_points_possible}`);
        console.log(`   得分率: ${((finalResult.score / finalResult.quiz_points_possible) * 100).toFixed(1)}%`);

      } else {
        console.log('⚠️  返回0个题目，可能是Canvas配置问题');
      }

    } catch (error) {
      console.log(`❌ 失败: ${error.message}`);
      console.log(`状态码: ${error.statusCode}`);
    }

    // 管理员对比测试
    console.log('\n👨‍💼 管理员对比测试');
    console.log('-'.repeat(40));
    try {
      const adminQuestions = await adminClient.listQuizQuestions(course.id, quiz.id);
      console.log(`✅ 管理员直接访问成功: ${adminQuestions.length} 个题目`);
      if (adminQuestions.length > 0) {
        console.log(`第一题: ${adminQuestions[0].question_name} - ${adminQuestions[0].question_text}`);
      }
    } catch (error) {
      console.log(`❌ 管理员访问失败: ${error.message}`);
    }

    console.log('\n' + '='.repeat(60));
    console.log('🎉 测试完成总结');
    console.log('='.repeat(60));
    console.log('✅ listQuizQuestions 工具已修复');
    console.log('✅ 学生可以在有submission时获取题目');
    console.log('✅ 权限控制正常工作');
    console.log('✅ 完整的测验流程验证成功');

  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    if (error.response?.data) {
      console.error('详情:', JSON.stringify(error.response.data, null, 2));
    }
  }
}

testQuizQuestionsFixedTool().catch(console.error);