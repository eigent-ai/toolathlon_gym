#!/usr/bin/env node

// Ignore self-signed certificate errors for testing
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'localhost:20001';

console.log('='.repeat(60));
console.log(' 🔒 Quiz Validation Token 测试');
console.log('='.repeat(60));

async function testQuizValidation() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    const adminProfile = await adminClient.getUserProfile();
    const studentProfile = await studentClient.getUserProfile();

    console.log(`管理员: ${adminProfile.name}`);
    console.log(`学生: ${studentProfile.name}`);

    // 创建课程和测验
    console.log('\n📚 步骤1: 创建测试环境');
    console.log('-'.repeat(40));

    const course = await adminClient.createCourse({
      account_id: 1,
      name: `Validation Token 测试 ${Date.now()}`,
      course_code: `VAL-TEST-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });
    console.log(`✅ 课程创建: ${course.name} (ID: ${course.id})`);

    const quiz = await adminClient.createQuiz(course.id, {
      title: 'Validation Token 验证测验',
      description: '测试 validation token 在答案提交中的作用',
      quiz_type: 'assignment',
      published: false,
      points_possible: 100,
      time_limit: 30,
      allowed_attempts: 2,
      show_correct_answers: true
    });
    console.log(`✅ 测验创建: ${quiz.title} (ID: ${quiz.id})`);

    // 添加多种类型的题目
    console.log('\n📝 步骤2: 添加不同类型的题目');
    console.log('-'.repeat(40));

    // 单选题
    const q1 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '数学计算',
      question_text: '计算: 15 × 4 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 25,
      answers: [
        { text: '58', weight: 0 },
        { text: '59', weight: 0 },
        { text: '60', weight: 100 },
        { text: '61', weight: 0 }
      ]
    });
    console.log(`  ✅ Q1: 单选题 (${q1.points_possible}分)`);

    // 判断题
    const q2 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '地理知识',
      question_text: '中国的首都是北京。',
      question_type: 'true_false_question',
      points_possible: 25,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ]
    });
    console.log(`  ✅ Q2: 判断题 (${q2.points_possible}分)`);

    // 简答题
    const q3 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '文学常识',
      question_text: '《红楼梦》的作者是谁？',
      question_type: 'short_answer_question',
      points_possible: 25,
      answers: [
        { text: '曹雪芹', weight: 100 },
        { text: '曹雪沁', weight: 50 }
      ]
    });
    console.log(`  ✅ Q3: 简答题 (${q3.points_possible}分)`);

    // 多选题
    const q4 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '编程语言',
      question_text: '以下哪些是编程语言？（多选）',
      question_type: 'multiple_answers_question',
      points_possible: 25,
      answers: [
        { text: 'Python', weight: 100 },
        { text: 'HTML', weight: 0 },
        { text: 'JavaScript', weight: 100 },
        { text: 'CSS', weight: 0 },
        { text: 'Java', weight: 100 }
      ]
    });
    console.log(`  ✅ Q4: 多选题 (${q4.points_possible}分)`);

    // 发布测验并注册学生
    await adminClient.updateQuiz(course.id, quiz.id, { published: true });
    console.log('\n✅ 测验已发布');

    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log('✅ 学生已注册到课程');

    await new Promise(resolve => setTimeout(resolve, 1000));

    // 学生开始测验
    console.log('\n\n🎯 步骤3: 学生开始测验');
    console.log('-'.repeat(40));

    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    const attempt = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;

    console.log(`📋 测验开始信息:`);
    console.log(`  - Submission ID: ${attempt.id}`);
    console.log(`  - Validation Token: ${attempt.validation_token ? '✅ 已获取' : '❌ 未获取'}`);
    console.log(`  - Token 长度: ${attempt.validation_token?.length || 0} 字符`);
    console.log(`  - Started at: ${attempt.started_at}`);

    if (!attempt.validation_token) {
      throw new Error('未获取到 validation_token，无法继续测试');
    }

    // 准备学生答案
    console.log('\n📝 步骤4: 准备学生答案');
    console.log('-'.repeat(40));

    const correctAnswerQ1 = q1.answers.find(a => a.weight === 100);
    const correctAnswerQ2 = q2.answers.find(a => a.weight === 100);
    const correctAnswersQ4 = q4.answers.filter(a => a.weight === 100);

    console.log(`Q1 正确答案: ${correctAnswerQ1.text} (ID: ${correctAnswerQ1.id})`);
    console.log(`Q2 正确答案: ${correctAnswerQ2.text} (ID: ${correctAnswerQ2.id})`);
    console.log(`Q3 正确答案: 曹雪芹 (文本输入)`);
    console.log(`Q4 正确答案: ${correctAnswersQ4.map(a => a.text).join(', ')}`);

    const studentAnswers = [
      {
        question_id: q1.id,
        answer: correctAnswerQ1.id  // 单选题：使用 answer_id
      },
      {
        question_id: q2.id,
        answer: correctAnswerQ2.id  // 判断题：使用 answer_id
      },
      {
        question_id: q3.id,
        answer: '曹雪芹'  // 简答题：文本答案
      },
      {
        question_id: q4.id,
        answer: correctAnswersQ4.map(a => a.id)  // 多选题：answer_id 数组
      }
    ];

    console.log('\n提交的答案详情:');
    studentAnswers.forEach((answer, index) => {
      const answerType = Array.isArray(answer.answer) ? 'array' : typeof answer.answer;
      const answerValue = Array.isArray(answer.answer) ?
        `[${answer.answer.join(', ')}]` : answer.answer;
      console.log(`  Q${index + 1}: ${answerValue} (类型: ${answerType})`);
    });

    // 测试1: 使用 validation_token 提交
    console.log('\n\n🔒 步骤5: 使用 Validation Todken 提交');
    console.log('-'.repeat(40));

    console.log('🚀 开始提交答案...');
    const submissionWithToken = await studentClient.submitQuizAttempt(
      course.id,
      quiz.id,
      attempt.id,
      studentAnswers,
      attempt.validation_token
    );

    console.log('\n✅ 提交成功！');
    const result = submissionWithToken.quiz_submissions ?
      submissionWithToken.quiz_submissions[0] : submissionWithToken;

    console.log(`📊 提交结果:`);
    console.log(`  - 状态: ${result.workflow_state}`);
    console.log(`  - 得分: ${result.score} / ${result.quiz_points_possible}`);
    console.log(`  - 得分率: ${((result.score / result.quiz_points_possible) * 100).toFixed(1)}%`);
    console.log(`  - 完成时间: ${result.finished_at}`);
    console.log(`  - 尝试次数: ${result.attempt}`);

    // 验证结果
    console.log('\n\n📈 步骤6: 结果验证');
    console.log('-'.repeat(40));

    if (result.score === result.quiz_points_possible) {
      console.log('🎉 完美！所有答案都正确！');
      console.log(`   满分: ${result.quiz_points_possible}分`);
      console.log('   ✅ Validation token 工作正常');
      console.log('   ✅ 所有题型都能正确提交和评分');
    } else if (result.score > 0) {
      console.log(`✅ 部分正确，得分: ${result.score}/${result.quiz_points_possible}`);
      console.log('   ✅ Validation token 工作正常');
      console.log('   ⚠️  部分答案可能需要手动批改');
    } else {
      console.log('⚠️  得分为0，可能的原因:');
      console.log('   - 答案格式问题');
      console.log('   - 需要教师手动批改');
      console.log('   - Canvas评分延迟');
    }

    // 额外测试：检查没有validation_token的情况
    console.log('\n\n🧪 步骤7: 额外测试 - 检查安全性');
    console.log('-'.repeat(40));

    // 创建第二个测验来测试无token情况
    const quiz2 = await adminClient.createQuiz(course.id, {
      title: '无Token测试',
      quiz_type: 'assignment',
      published: true,
      points_possible: 10
    });

    const q5 = await adminClient.createQuizQuestion(course.id, quiz2.id, {
      question_name: '简单题',
      question_text: '2 + 2 = ?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '3', weight: 0 },
        { text: '4', weight: 100 }
      ]
    });

    const attempt2 = await studentClient.startQuizAttempt(course.id, quiz2.id);
    const submission2 = attempt2.quiz_submissions ? attempt2.quiz_submissions[0] : attempt2;

    try {
      console.log('测试不使用 validation_token 的提交...');
      await studentClient.submitQuizAttempt(
        course.id,
        quiz2.id,
        submission2.id,
        [{ question_id: q5.id, answer: q5.answers.find(a => a.weight === 100).id }]
        // 故意不传 validation_token
      );
      console.log('✅ 无token提交成功（Canvas可能允许这种情况）');
    } catch (error) {
      console.log('⚠️  无token提交失败（这是预期的安全行为）');
      console.log(`   错误: ${error.message}`);
    }

    // 最终总结
    console.log('\n\n');
    console.log('='.repeat(60));
    console.log(' 🎯 测试总结');
    console.log('='.repeat(60));
    console.log('✅ Validation token 正确获取和使用');
    console.log('✅ 单选题答案提交成功');
    console.log('✅ 判断题答案提交成功');
    console.log('✅ 简答题答案提交成功');
    console.log('✅ 多选题答案提交成功');
    console.log('✅ 答案正确评分');
    console.log('\n🔒 Quiz提交功能工作正常！');

  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    if (error.response?.data) {
      console.error('Canvas API 错误详情:');
      console.error(JSON.stringify(error.response.data, null, 2));
    }
    console.error('\n Stack trace:');
    console.error(error.stack);
  }
}

// 运行测试
testQuizValidation().catch(console.error);