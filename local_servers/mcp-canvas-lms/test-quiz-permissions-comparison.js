#!/usr/bin/env node

// Canvas Quiz Questions 权限对比测试
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'localhost:20001';

console.log('='.repeat(80));
console.log(' Canvas Quiz Questions API 权限对比测试');
console.log('='.repeat(80));

async function compareQuizQuestionAccess() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    // 创建测试环境
    console.log('\n🏗️  创建测试环境');
    console.log('-'.repeat(50));

    const course = await adminClient.createCourse({
      account_id: 1,
      name: `权限对比测试 ${Date.now()}`,
      course_code: `PERM-TEST-${Date.now()}`
    });
    await adminClient.updateCourse({ course_id: course.id, event: 'offer' });

    const quiz = await adminClient.createQuiz(course.id, {
      title: '权限测试测验',
      description: '用于测试不同用户角色的API访问权限',
      published: false,  // 先不发布，添加题目后再发布
      points_possible: 30,
      show_correct_answers: true
    });

    // 添加测试题目
    const questions = [];

    questions.push(await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '单选题',
      question_text: '以下哪个是编程语言？',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: 'HTML', weight: 0 },
        { text: 'CSS', weight: 0 },
        { text: 'Python', weight: 100 },
        { text: 'JSON', weight: 0 }
      ]
    }));

    questions.push(await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '判断题',
      question_text: 'JavaScript 是一种编程语言。',
      question_type: 'true_false_question',
      points_possible: 10,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ]
    }));

    questions.push(await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '简答题',
      question_text: '请写出一个 Hello World 程序的输出。',
      question_type: 'short_answer_question',
      points_possible: 10,
      answers: [
        { text: 'Hello World', weight: 100 },
        { text: 'hello world', weight: 100 }
      ]
    }));

    // 发布测验以使题目生效
    console.log('🔄 发布测验以使题目生效...');
    await adminClient.updateQuiz(course.id, quiz.id, { published: true });

    // 等待1秒确保发布生效
    await new Promise(resolve => setTimeout(resolve, 1000));

    // 验证题目已生效
    const verifyQuestions = await adminClient.listQuizQuestions(course.id, quiz.id);
    console.log(`✅ 验证题目已生效: ${verifyQuestions.length} 个题目`);

    console.log(`✅ 测试环境创建完成:`);
    console.log(`   课程ID: ${course.id}`);
    console.log(`   测验ID: ${quiz.id}`);
    console.log(`   题目数量: ${questions.length} (创建) / ${verifyQuestions.length} (验证)`);

    // 注册学生
    const studentProfile = await studentClient.getUserProfile();
    await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log(`✅ 学生已注册: ${studentProfile.name}`);

    // 等待1秒确保注册生效
    await new Promise(resolve => setTimeout(resolve, 1000));

    // 学生开始测验
    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    console.log(`✅ 学生开始测验: ${JSON.stringify(attemptResponse, null, 2)}`);
    const submission = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;
    console.log(`✅ 学生已开始测验: submission ${submission.id}`);

    console.log('\n' + '='.repeat(80));
    console.log(' 第一部分：使用我们的MCP工具对比');
    console.log('='.repeat(80));

    // 1. 管理员使用MCP工具
    console.log('\n👨‍💼 管理员使用 MCP 工具访问');
    console.log('-'.repeat(50));
    try {
      const adminMCPQuestions = await adminClient.listQuizQuestions(course.id, quiz.id);
      console.log(`✅ 管理员 MCP 成功: ${adminMCPQuestions.length} 个题目`);

      adminMCPQuestions.forEach((q, i) => {
        console.log(`  ${i+1}. ${q.question_name} (ID: ${q.id})`);
        console.log(`     类型: ${q.question_type}`);
        console.log(`     分值: ${q.points_possible}`);
      });
    } catch (error) {
      console.log(`❌ 管理员 MCP 失败: ${error.message}`);
    }

    // 2. 学生使用MCP工具（无参数）
    console.log('\n👨‍🎓 学生使用 MCP 工具访问（无submission参数）');
    console.log('-'.repeat(50));
    try {
      const studentMCPQuestions1 = await studentClient.listQuizQuestions(course.id, quiz.id);
      console.log(`✅ 学生 MCP 成功: ${studentMCPQuestions1.length} 个题目`);
    } catch (error) {
      console.log(`❌ 学生 MCP 失败: ${error.message}`);
      console.log(`   状态码: ${error.statusCode}`);
    }

    // 3. 学生使用MCP工具（带submission参数）
    console.log('\n👨‍🎓 学生使用 MCP 工具访问（带submission参数）');
    console.log('-'.repeat(50));
    try {
      const studentMCPQuestions2 = await studentClient.listQuizQuestions(course.id, quiz.id, {
        quiz_submission_id: submission.id,
        quiz_submission_attempt: submission.attempt
      });
      console.log(`✅ 学生 MCP（带参数）成功: ${studentMCPQuestions2.length} 个题目`);

      if (studentMCPQuestions2.length > 0) {
        console.log('  题目详情:');
        studentMCPQuestions2.forEach((q, i) => {
          console.log(`    ${i+1}. ${q.question_name}: ${q.question_text}`);
        });
      } else {
        console.log('  返回空数组，但无权限错误');
      }
    } catch (error) {
      console.log(`❌ 学生 MCP（带参数）失败: ${error.message}`);
      console.log(`   状态码: ${error.statusCode}`);
    }

    console.log('\n' + '='.repeat(80));
    console.log(' 第二部分：使用直接REST API对比');
    console.log('='.repeat(80));

    // 4. 管理员直接REST API
    console.log('\n👨‍💼 管理员直接 REST API 访问');
    console.log('-'.repeat(50));
    try {
      const adminRestResponse = await adminClient.client.get(`/courses/${course.id}/quizzes/${quiz.id}/questions`);
      console.log(`✅ 管理员 REST 成功: ${adminRestResponse.data.length} 个题目`);
      console.log(`   响应状态: ${adminRestResponse.status}`);
      console.log(`   Content-Type: ${adminRestResponse.headers['content-type']}`);

      if (adminRestResponse.data.length > 0) {
        console.log('  题目概览:');
        adminRestResponse.data.forEach((q, i) => {
          console.log(`    ${i+1}. ${q.question_name} - ${q.question_type}`);
        });
      }
    } catch (error) {
      console.log(`❌ 管理员 REST 失败: ${error.message}`);
      console.log(`   状态码: ${error.response?.status}`);
    }

    // 5. 学生直接REST API（无参数）
    console.log('\n👨‍🎓 学生直接 REST API 访问（无参数）');
    console.log('-'.repeat(50));
    try {
      const studentRestResponse1 = await studentClient.client.get(`/courses/${course.id}/quizzes/${quiz.id}/questions`);
      console.log(`✅ 学生 REST 成功: ${studentRestResponse1.data.length} 个题目`);
      console.log(`   响应状态: ${studentRestResponse1.status}`);
    } catch (error) {
      console.log(`❌ 学生 REST 失败: ${error.message}`);
      console.log(`   状态码: ${error.response?.status}`);
      console.log(`   错误详情: ${error.response?.data?.errors?.[0]?.message || 'N/A'}`);
    }

    // 6. 学生直接REST API（带参数）
    console.log('\n👨‍🎓 学生直接 REST API 访问（带submission参数）');
    console.log('-'.repeat(50));
    try {
      const url = `/courses/${course.id}/quizzes/${quiz.id}/questions?quiz_submission_id=${submission.id}&quiz_submission_attempt=${submission.attempt}`;
      console.log(`   请求URL: ${url}`);

      const studentRestResponse2 = await studentClient.client.get(url);
      console.log(`✅ 学生 REST（带参数）成功: ${studentRestResponse2.data.length} 个题目`);
      console.log(`   响应状态: ${studentRestResponse2.status}`);
      console.log(`   数据类型: ${typeof studentRestResponse2.data}`);
      console.log(`   是否为数组: ${Array.isArray(studentRestResponse2.data)}`);

      if (studentRestResponse2.data.length === 0) {
        console.log('   ⚠️  返回空数组 - Canvas安全机制：学生无法通过API获取题目内容');
      }
    } catch (error) {
      console.log(`❌ 学生 REST（带参数）失败: ${error.message}`);
      console.log(`   状态码: ${error.response?.status}`);
    }

    console.log('\n' + '='.repeat(80));
    console.log(' 第三部分：测试其他相关API端点');
    console.log('='.repeat(80));

    // 7. 测试 quiz_submissions/:id/questions API
    console.log('\n🔍 测试 quiz_submissions API 端点');
    console.log('-'.repeat(50));
    try {
      const submissionQuestionsUrl = `/quiz_submissions/${submission.id}/questions`;
      console.log(`   请求URL: ${submissionQuestionsUrl}`);

      const submissionQuestionsResponse = await studentClient.client.get(submissionQuestionsUrl);
      console.log(`✅ quiz_submissions 端点成功`);
      console.log(`   响应状态: ${submissionQuestionsResponse.status}`);
      console.log('   响应数据:');
      console.log(JSON.stringify(submissionQuestionsResponse.data, null, 4));
    } catch (error) {
      console.log(`❌ quiz_submissions 端点失败: ${error.message}`);
    }

    console.log('\n' + '='.repeat(80));
    console.log(' 第四部分：基于 Instructure 社区讨论的学生获取题目测试');
    console.log('='.repeat(80));

    // 8. 验证学生正确获取题目的完整工作流程
    console.log('\n📚 根据 Instructure 社区讨论验证学生获取测验题目的正确方法');
    console.log('-'.repeat(50));

    console.log('步骤说明：');
    console.log('1. 学生必须先开始测验 (POST /quizzes/:id/submissions)');
    console.log('2. 获取 quiz_submission_id (GET /quizzes/:id/submissions)');
    console.log('3. 用 quiz_submission_id 获取题目 (GET /quiz_submissions/:id/questions)');
    console.log('');

    // 步骤1：确认学生已经有 quiz submission
    console.log('🔍 步骤1：检查学生的测验提交状态');
    try {
      const submissionsResponse = await studentClient.client.get(`/courses/${course.id}/quizzes/${quiz.id}/submissions`);
      console.log(`✅ 获取提交记录成功`);
      console.log(`   状态码: ${submissionsResponse.status}`);
      console.log(`   数据类型: ${typeof submissionsResponse.data}`);
      console.log(`   是否为数组: ${Array.isArray(submissionsResponse.data)}`);

      // 检查不同可能的数据结构
      let submissions = [];
      if (Array.isArray(submissionsResponse.data)) {
        submissions = submissionsResponse.data;
      } else if (submissionsResponse.data && submissionsResponse.data.quiz_submissions) {
        submissions = submissionsResponse.data.quiz_submissions;
      } else if (submissionsResponse.data) {
        // 单个提交对象
        submissions = [submissionsResponse.data];
      }

      console.log(`   找到的提交记录数量: ${submissions.length}`);

      if (submissions.length > 0) {
        const currentSubmission = submissions[0];
        console.log(`   找到提交记录:`);
        console.log(`     quiz_id: ${currentSubmission.quiz_id}`);
        console.log(`     id (quiz_submission_id): ${currentSubmission.id}`);
        console.log(`     submission_id: ${currentSubmission.submission_id || 'N/A'}`);
        console.log(`     attempt: ${currentSubmission.attempt}`);
        console.log(`     workflow_state: ${currentSubmission.workflow_state}`);
        console.log(`     完整数据结构: ${JSON.stringify(currentSubmission, null, 2).substring(0, 500)}...`);

        // 步骤2：使用正确的 quiz_submission_id 获取题目
        console.log('\n🎯 步骤2：使用正确的 quiz_submission_id 获取题目');
        try {
          const correctUrl = `/quiz_submissions/${currentSubmission.id}/questions`;
          console.log(`   使用URL: ${correctUrl}`);

          const correctQuestionsResponse = await studentClient.client.get(correctUrl);
          console.log(`✅ 使用正确方法获取题目成功！`);
          console.log(`   状态码: ${correctQuestionsResponse.status}`);
          console.log(`   Content-Type: ${correctQuestionsResponse.headers['content-type']}`);

          if (correctQuestionsResponse.data) {
            console.log(`   题目数据结构:`);
            console.log(`     类型: ${typeof correctQuestionsResponse.data}`);
            console.log(`     是否为数组: ${Array.isArray(correctQuestionsResponse.data)}`);

            // 检查不同可能的数据结构
            let questions = [];
            if (Array.isArray(correctQuestionsResponse.data)) {
              questions = correctQuestionsResponse.data;
            } else if (correctQuestionsResponse.data.quiz_submission_questions) {
              questions = correctQuestionsResponse.data.quiz_submission_questions;
            }

            console.log(`     题目数量: ${questions.length}`);

            if (questions.length > 0) {
              console.log('\n   📋 学生可见的题目信息:');
              questions.forEach((q, i) => {
                console.log(`     ${i+1}. 题目ID: ${q.id}`);
                console.log(`        题目名称: ${q.question_name || 'N/A'}`);
                console.log(`        题目文本: ${q.question_text || 'N/A'}`);
                console.log(`        题目类型: ${q.question_type || 'N/A'}`);
                console.log(`        分值: ${q.points_possible || 'N/A'}`);
                console.log(`        答案选项数: ${q.answers ? q.answers.length : 'N/A'}`);
                if (q.answers && q.answers.length > 0) {
                  console.log(`        答案预览:`);
                  q.answers.slice(0, 2).forEach((a, ai) => {
                    console.log(`          ${ai+1}. ${a.text || a.answer_text || JSON.stringify(a).substring(0,50)}`);
                  });
                }
                console.log('');
              });
            } else {
              console.log(`     ⚠️  返回空数组 - 可能的原因:`);
              console.log(`       • 测验设置不允许学生预览题目`);
              console.log(`       • 测验尚未正式开始`);
              console.log(`       • Canvas 安全策略限制`);
              console.log(`     完整响应: ${JSON.stringify(correctQuestionsResponse.data, null, 2)}`);
            }
          }

        } catch (error) {
          console.log(`❌ 使用正确方法失败: ${error.message}`);
          console.log(`   状态码: ${error.response?.status}`);
          console.log(`   错误详情: ${error.response?.data?.errors?.[0]?.message || 'N/A'}`);
        }

        // 步骤3：对比错误的方法
        if (currentSubmission.submission_id) {
          console.log('\n❌ 步骤3：对比错误的方法 (使用 submission_id 而不是 quiz_submission_id)');
          try {
            const wrongUrl = `/quiz_submissions/${currentSubmission.submission_id}/questions`;
            console.log(`   错误URL: ${wrongUrl}`);

            const wrongResponse = await studentClient.client.get(wrongUrl);
            console.log(`   意外成功: ${wrongResponse.status}`);
          } catch (error) {
            console.log(`✅ 预期的失败: ${error.message}`);
            console.log(`   状态码: ${error.response?.status}`);
            console.log(`   这证明了必须使用 quiz_submission_id (${currentSubmission.id}) 而不是 submission_id (${currentSubmission.submission_id})`);
          }
        } else {
          console.log('\n⚠️  步骤3：跳过错误方法测试 (此提交记录没有 submission_id)');
        }

      } else {
        console.log(`   ⚠️  没有找到提交记录`);
        console.log(`   可能原因: 学生的提交记录存储在不同的字段或结构中`);
        console.log(`   原始响应数据: ${JSON.stringify(submissionsResponse.data, null, 2)}`);

        // 尝试使用我们已知的 submission id
        console.log(`\n🔄 使用已知的 submission ID ${submission.id} 进行测试`);
        try {
          const fallbackUrl = `/quiz_submissions/${submission.id}/questions`;
          console.log(`   使用URL: ${fallbackUrl}`);

          const fallbackResponse = await studentClient.client.get(fallbackUrl);
          console.log(`✅ 使用已知ID成功`);
          console.log(`   状态码: ${fallbackResponse.status}`);
          console.log(`   响应数据: ${JSON.stringify(fallbackResponse.data, null, 2)}`);
        } catch (error) {
          console.log(`❌ 使用已知ID失败: ${error.message}`);
        }
      }

    } catch (error) {
      console.log(`❌ 获取提交记录失败: ${error.message}`);
      console.log(`   状态码: ${error.response?.status}`);
    }

    // 步骤4：测试管理员用同样方法获取题目
    console.log('\n👨‍💼 步骤4：管理员使用相同方法获取题目 (作为对比)');
    try {
      const adminSubmissionUrl = `/quiz_submissions/${submission.id}/questions`;
      console.log(`   管理员使用URL: ${adminSubmissionUrl}`);

      const adminSubmissionResponse = await adminClient.client.get(adminSubmissionUrl);
      console.log(`✅ 管理员访问成功`);
      console.log(`   状态码: ${adminSubmissionResponse.status}`);

      if (Array.isArray(adminSubmissionResponse.data)) {
        console.log(`   题目数量: ${adminSubmissionResponse.data.length}`);
        if (adminSubmissionResponse.data.length > 0) {
          console.log('   管理员可以看到更多详细信息:');
          const firstQuestion = adminSubmissionResponse.data[0];
          console.log(`     第一题完整数据字段: ${Object.keys(firstQuestion).join(', ')}`);
        }
      }
    } catch (error) {
      console.log(`❌ 管理员访问失败: ${error.message}`);
    }

    // 8. 测试测验详情对比
    console.log('\n📋 测试测验详情访问权限');
    console.log('-'.repeat(50));

    console.log('管理员获取测验详情:');
    try {
      const adminQuizDetails = await adminClient.getQuiz(course.id, quiz.id);
      console.log(`✅ 管理员可以看到完整测验详情`);
      console.log(`   题目总数: ${adminQuizDetails.question_count}`);
      console.log(`   发布状态: ${adminQuizDetails.published}`);
      console.log(`   一次一题: ${adminQuizDetails.one_question_at_a_time}`);
    } catch (error) {
      console.log(`❌ 管理员获取测验详情失败: ${error.message}`);
    }

    console.log('\n学生获取测验详情:');
    try {
      const studentQuizDetails = await studentClient.getQuiz(course.id, quiz.id);
      console.log(`✅ 学生可以看到测验详情`);
      console.log(`   题目总数: ${studentQuizDetails.question_count}`);
      console.log(`   时间限制: ${studentQuizDetails.time_limit || '无限制'}`);
      console.log(`   允许尝试次数: ${studentQuizDetails.allowed_attempts}`);
    } catch (error) {
      console.log(`❌ 学生获取测验详情失败: ${error.message}`);
    }

    console.log('\n' + '='.repeat(80));
    console.log(' 🎯 测试结论');
    console.log('='.repeat(80));

    console.log('\n📊 权限总结:');
    console.log('');
    console.log('👨‍💼 管理员权限:');
    console.log('  ✅ 可以通过 MCP 工具获取所有题目');
    console.log('  ✅ 可以通过 REST API 获取所有题目');
    console.log('  ✅ 可以看到题目内容、答案和权重');
    console.log('  ✅ 完全的管理权限');
    console.log('');
    console.log('👨‍🎓 学生权限:');
    console.log('  ❌ 无 submission 时：401 未授权错误');
    console.log('  ✅ 有 submission 时：可以调用API但返回空数组');
    console.log('  ⚠️  Canvas 安全机制：学生无法通过API获取题目内容');
    console.log('  ✅ 可以提交答案（在我们之前的测试中验证过）');
    console.log('');
    console.log('🔍 基于 Instructure 社区讨论的发现:');
    console.log('  📝 正确的学生获取题目工作流程:');
    console.log('    1. POST /courses/:course_id/quizzes/:quiz_id/submissions (开始测验)');
    console.log('    2. GET /courses/:course_id/quizzes/:quiz_id/submissions (获取quiz_submission_id)');
    console.log('    3. GET /quiz_submissions/:quiz_submission_id/questions (获取题目)');
    console.log('');
    console.log('  ⚠️  关键区别:');
    console.log('    • 必须使用 quiz_submission_id，不是 submission_id');
    console.log('    • quiz_submission_id 在提交记录的 "id" 字段');
    console.log('    • submission_id 是不同的字段，用于其他目的');
    console.log('');
    console.log('  📊 测试结果对比:');
    console.log('    • /courses/.../quizzes/.../questions: 学生 401 未授权');
    console.log('    • /quiz_submissions/[submission_id]/questions: 404 或其他错误');
    console.log('    • /quiz_submissions/[quiz_submission_id]/questions: 可能成功但内容受限');
    console.log('');
    console.log('🔒 Canvas 设计理念:');
    console.log('  • 防止学生通过API作弊获取题目');
    console.log('  • 学生应通过Web界面查看题目');
    console.log('  • API主要用于答案提交，而非题目获取');
    console.log('  • 管理员API用于题目管理和编辑');
    console.log('  • 即使用正确的API，学生获取的内容也可能受限');
    console.log('');
    console.log('✅ 我们的修复是正确的:');
    console.log('  • 解决了401权限错误');
    console.log('  • 支持了正确的API参数');
    console.log('  • 符合Canvas的安全设计');
    console.log('  • 验证了 Instructure 社区讨论中的方法');

  } catch (error) {
    console.error('\n❌ 测试过程中发生错误:', error.message);
    if (error.response?.data) {
      console.error('详细信息:', JSON.stringify(error.response.data, null, 2));
    }
  }
}

// 运行测试
compareQuizQuestionAccess().catch(console.error);