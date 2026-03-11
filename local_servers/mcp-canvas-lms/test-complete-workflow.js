#!/usr/bin/env node

// Ignore self-signed certificate errors for testing
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';
import fs from 'fs';
import path from 'path';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'localhost:20001';

console.log('='.repeat(60));
console.log(' 完整的Canvas工作流测试');
console.log('='.repeat(60));

async function runCompleteWorkflow() {
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    // ========== 1. 获取用户信息 ==========
    console.log('\n📋 步骤 1: 获取用户信息');
    console.log('-'.repeat(40));

    const adminProfile = await adminClient.getUserProfile();
    console.log(`✅ 管理员: ${adminProfile.name} (ID: ${adminProfile.id})`);

    const studentProfile = await studentClient.getUserProfile();
    console.log(`✅ 学生: ${studentProfile.name} (ID: ${studentProfile.id})`);

    // ========== 2. 创建课程 ==========
    console.log('\n📚 步骤 2: 创建新课程');
    console.log('-'.repeat(40));

    const course = await adminClient.createCourse({
      account_id: 1,
      name: `完整测试课程 ${new Date().toLocaleString('zh-CN')}`,
      course_code: `TEST-${Date.now()}`,
      is_public: false,
      syllabus_body: '这是一个完整的测试课程，包含测验和作业'
    });
    console.log(`✅ 课程创建成功: ${course.name}`);
    console.log(`   课程ID: ${course.id}`);

    // 发布课程
    await adminClient.updateCourse({
      course_id: course.id,
      event: 'offer'
    });
    console.log('✅ 课程已发布');

    // ========== 3. 创建测验并添加题目 ==========
    console.log('\n📝 步骤 3: 创建测验');
    console.log('-'.repeat(40));

    const quiz = await adminClient.createQuiz(course.id, {
      title: '期中测验',
      description: '这是一个包含多种题型的测验',
      quiz_type: 'assignment',
      published: false,
      time_limit: 30,
      allowed_attempts: 2,
      points_possible: 100,
      show_correct_answers: true,
      shuffle_answers: false
    });
    console.log(`✅ 测验创建成功: ${quiz.title} (ID: ${quiz.id})`);

    // 添加各种题型
    console.log('\n📝 步骤 4: 添加测验题目');
    console.log('-'.repeat(40));

    // 题目1: 单选题
    const q1 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '数学计算题',
      question_text: '<p>请计算: 15 + 27 = ?</p>',
      question_type: 'multiple_choice_question',
      points_possible: 20,
      position: 1,
      answers: [
        { text: '40', weight: 0, comments: '再算一遍哦' },
        { text: '42', weight: 100, comments: '正确！' },
        { text: '43', weight: 0, comments: '接近了，但不对' },
        { text: '45', weight: 0, comments: '计算错误' }
      ],
      correct_comments: '很好！15 + 27 = 42',
      incorrect_comments: '请重新计算: 15 + 27'
    });
    console.log(`✅ 题目1添加成功: 单选题 (${q1.points_possible}分)`);

    // 题目2: 判断题
    const q2 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '地理知识',
      question_text: '<p>中国的首都是北京。</p>',
      question_type: 'true_false_question',
      points_possible: 20,
      position: 2,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ],
      correct_comments: '正确！北京是中国的首都。',
      incorrect_comments: '错误。北京是中国的首都。'
    });
    console.log(`✅ 题目2添加成功: 判断题 (${q2.points_possible}分)`);

    // 题目3: 简答题
    const q3 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '世界知识',
      question_text: '<p>世界上最大的洋是哪个？（请输入中文名称）</p>',
      question_type: 'short_answer_question',
      points_possible: 20,
      position: 3,
      answers: [
        { text: '太平洋', weight: 100 },
        { text: '太平', weight: 50 }
      ],
      correct_comments: '正确！太平洋是世界上最大的洋。',
      incorrect_comments: '答案是太平洋。'
    });
    console.log(`✅ 题目3添加成功: 简答题 (${q3.points_possible}分)`);

    // 题目4: 多选题
    const q4 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '编程语言',
      question_text: '<p>以下哪些是编程语言？（多选）</p>',
      question_type: 'multiple_answers_question',
      points_possible: 20,
      position: 4,
      answers: [
        { text: 'Python', weight: 100 },
        { text: 'Java', weight: 100 },
        { text: 'HTML', weight: 0, comments: 'HTML是标记语言，不是编程语言' },
        { text: 'JavaScript', weight: 100 },
        { text: 'CSS', weight: 0, comments: 'CSS是样式表语言' }
      ]
    });
    console.log(`✅ 题目4添加成功: 多选题 (${q4.points_possible}分)`);

    // 题目5: 论述题
    const q5 = await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: '论述题',
      question_text: '<p>请简要描述你对在线教育的看法（至少50字）</p>',
      question_type: 'essay_question',
      points_possible: 20,
      position: 5
    });
    console.log(`✅ 题目5添加成功: 论述题 (${q5.points_possible}分)`);

    // 发布测验
    await adminClient.updateQuiz(course.id, quiz.id, { published: true });
    console.log('✅ 测验已发布');

    // ========== 5. 创建作业 ==========
    console.log('\n📄 步骤 5: 创建作业');
    console.log('-'.repeat(40));

    const assignment = await adminClient.createAssignment({
      course_id: course.id,
      name: '项目报告提交',
      description: '<p>请提交你的项目报告文档。</p><ul><li>格式: PDF或Word文档</li><li>字数: 不少于1000字</li><li>截止日期: 本周末</li></ul>',
      submission_types: ['online_upload', 'online_text_entry'],
      points_possible: 100,
      published: true,
      grading_type: 'points'
    });
    console.log(`✅ 作业创建成功: ${assignment.name}`);
    console.log(`   作业ID: ${assignment.id}`);
    console.log(`   分值: ${assignment.points_possible}分`);

    // ========== 6. 注册学生到课程 ==========
    console.log('\n👥 步骤 6: 注册学生到课程');
    console.log('-'.repeat(40));

    const enrollment = await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log(`✅ 学生注册成功`);
    console.log(`   注册状态: ${enrollment.enrollment_state}`);

    // 等待注册生效
    await new Promise(resolve => setTimeout(resolve, 1000));

    // ========== 7. 学生参加测验 ==========
    console.log('\n🎯 步骤 7: 学生参加测验');
    console.log('-'.repeat(40));

    // 验证学生已注册
    const studentCourses = await studentClient.listCourses();
    const enrolledCourse = studentCourses.find(c => c.id === course.id);
    console.log(`✅ 确认学生已注册到: ${enrolledCourse.name}`);

    // 获取测验列表
    const quizzes = await studentClient.listQuizzes(course.id);
    console.log(`✅ 找到 ${quizzes.length} 个测验`);

    // 开始测验
    console.log('\n开始测验...');
    const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
    const attempt = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;
    const validationToken = attempt.validation_token;
    console.log(`✅ 测验已开始 (Attempt ID: ${attempt.id})`);

    // 准备答案
    console.log('\n提交测验答案...');
    const quizAnswers = [
      { question_id: q1.id, answer_id: q1.answers[1].id }, // 选择"42"
      { question_id: q2.id, answer: true }, // True
      { question_id: q3.id, answer: '太平洋' }, // 太平洋
      { question_id: q4.id, answer: [q4.answers[0].id, q4.answers[1].id, q4.answers[3].id] }, // Python, Java, JavaScript
      { question_id: q5.id, answer: '在线教育为学习提供了极大的灵活性和便利性。学生可以根据自己的时间安排学习，不受地理位置限制。同时，在线教育资源丰富，可以接触到全球优质的教育内容。然而，在线教育也需要学生有较强的自律性和时间管理能力。' }
    ];

    const quizSubmission = await studentClient.submitQuizAttempt(course.id, quiz.id, attempt.id, quizAnswers, validationToken);
    console.log(`✅ 测验提交成功`);
    console.log(`   得分: ${quizSubmission.score || '待批改'}`);
    console.log(`   状态: ${quizSubmission.workflow_state || 'pending_review'}`);

    // ========== 8. 学生提交作业 ==========
    console.log('\n📤 步骤 8: 学生提交作业');
    console.log('-'.repeat(40));

    // 获取作业列表
    const assignments = await studentClient.listAssignments(course.id);
    const fileAssignment = assignments.find(a => a.id === assignment.id);
    console.log(`✅ 找到作业: ${fileAssignment.name}`);

    // 创建作业文件
    const reportPath = path.join(process.cwd(), 'project-report.txt');
    const reportContent = `项目报告
==================

学生姓名: ${studentProfile.name}
课程名称: ${course.name}
提交日期: ${new Date().toLocaleDateString('zh-CN')}

一、项目概述
本项目旨在探讨和实践Canvas LMS系统的API集成方案。通过开发MCP服务器，
实现了与Canvas平台的全面对接，支持课程管理、测验创建、作业提交等核心功能。

二、技术实现
1. 使用TypeScript开发，确保类型安全
2. 实现了50+个Canvas API端点的封装
3. 支持文件上传、测验管理等复杂功能
4. 完整的错误处理和重试机制

三、项目成果
- 成功实现了所有计划功能
- 通过了完整的集成测试
- 代码质量达到生产标准

四、总结与展望
本项目成功展示了Canvas LMS的强大扩展能力，为教育技术的发展提供了新的可能性。

字数: 1000+
`;

    fs.writeFileSync(reportPath, reportContent);
    console.log(`✅ 作业文件已创建: ${reportPath}`);

    // 上传文件
    console.log('\n上传文件到Canvas...');
    const uploadedFile = await studentClient.uploadFileFromPath(reportPath);
    console.log(`✅ 文件上传成功: ${uploadedFile.display_name} (ID: ${uploadedFile.id})`);

    // 提交作业
    console.log('\n提交作业...');
    const submission = await studentClient.submitAssignment({
      course_id: course.id,
      assignment_id: assignment.id,
      submission_type: 'online_upload',
      file_ids: [uploadedFile.id]
    });
    console.log(`✅ 作业提交成功！`);
    console.log(`   提交状态: ${submission.workflow_state}`);
    console.log(`   提交时间: ${new Date(submission.submitted_at).toLocaleString('zh-CN')}`);

    // 清理文件
    fs.unlinkSync(reportPath);
    console.log(`✅ 临时文件已清理`);

    // ========== 完成 ==========
    console.log('\n');
    console.log('='.repeat(60));
    console.log(' 🎉 所有测试完成！');
    console.log('='.repeat(60));
    console.log('\n📊 测试总结:');
    console.log(`  ✅ 课程创建成功: ${course.name}`);
    console.log(`  ✅ 测验创建成功: 包含5道题目，共100分`);
    console.log(`  ✅ 作业创建成功: ${assignment.name}`);
    console.log(`  ✅ 学生完成测验: ${quizSubmission.score || '待批改'}`);
    console.log(`  ✅ 学生提交作业: 文件上传成功`);

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    console.error(error.stack);
  }
}

// 运行完整工作流
runCompleteWorkflow().catch(console.error);