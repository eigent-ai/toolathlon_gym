#!/usr/bin/env node

// Ignore self-signed certificate errors for testing
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';
import fs from 'fs';
import path from 'path';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'https://localhost:20001';

async function testWithStudent() {
  console.log('\n========== TESTING WITH STUDENT ACCOUNT ==========\n');
  const client = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    // 1. 获取用户信息和课程列表
    console.log('1. Getting user profile...');
    const profile = await client.getUserProfile();
    console.log(`   User: ${profile.name} (ID: ${profile.id})`);

    console.log('\n2. Listing courses...');
    const courses = await client.listCourses();
    console.log(`   Found ${courses.length} courses`);

    if (courses.length === 0) {
      console.log('   No courses found for student. Please enroll in a course first.');
      return null;
    }

    const course = courses[0];
    console.log(`   Using course: ${course.name} (ID: ${course.id})`);

    // 2. 查看课程中的测验
    console.log('\n3. Listing quizzes in course...');
    const quizzes = await client.listQuizzes(course.id);
    console.log(`   Found ${quizzes.length} quizzes`);

    if (quizzes.length > 0) {
      const quiz = quizzes[0];
      console.log(`   First quiz: ${quiz.title} (ID: ${quiz.id})`);

      // 3. 查看测验题目
      console.log('\n4. Listing quiz questions...');
      const questions = await client.listQuizQuestions(course.id, quiz.id);
      console.log(`   Found ${questions.length} questions`);

      if (questions.length > 0) {
        console.log(`   First question: ${questions[0].question_name}`);
      }

      // 4. 开始测验尝试
      console.log('\n5. Starting quiz attempt...');
      try {
        const attempt = await client.startQuizAttempt(course.id, quiz.id);
        console.log(`   Started quiz attempt (Submission ID: ${attempt.id})`);

        // 5. 准备答案并提交
        if (questions.length > 0 && attempt.id) {
          console.log('\n6. Preparing and submitting answers...');
          const answers = questions.map(q => ({
            question_id: q.id,
            answer: q.question_type === 'true_false_question' ? true :
                   q.question_type === 'multiple_choice_question' && q.answers ? q.answers[0]?.id :
                   'Test answer'
          }));

          const submission = await client.submitQuizAttempt(course.id, quiz.id, attempt.id, answers);
          console.log(`   Quiz submitted! Score: ${submission.score || 'Pending'}`);
        }
      } catch (error) {
        console.log(`   Could not start quiz: ${error.message}`);
      }
    }

    // 5. 查看作业
    console.log('\n7. Listing assignments...');
    const assignments = await client.listAssignments(course.id);
    console.log(`   Found ${assignments.length} assignments`);

    if (assignments.length > 0) {
      const assignment = assignments.find(a =>
        a.submission_types?.includes('online_upload') ||
        a.submission_types?.includes('online_text_entry')
      );

      if (assignment) {
        console.log(`   Found assignment accepting uploads: ${assignment.name} (ID: ${assignment.id})`);

        // 6. 创建测试文件并上传
        console.log('\n8. Creating and uploading test file...');
        const testFilePath = path.join(process.cwd(), 'test-submission.txt');
        fs.writeFileSync(testFilePath, `Test submission for assignment: ${assignment.name}\nSubmitted at: ${new Date().toISOString()}\nStudent: ${profile.name}`);

        try {
          const uploadedFile = await client.uploadFileFromPath(testFilePath, course.id);
          console.log(`   File uploaded: ${uploadedFile.display_name} (ID: ${uploadedFile.id})`);

          // 7. 提交作业
          console.log('\n9. Submitting assignment with file...');
          const submission = await client.submitAssignment({
            course_id: course.id,
            assignment_id: assignment.id,
            submission_type: 'online_upload',
            file_ids: [uploadedFile.id]
          });
          console.log(`   Assignment submitted! Workflow state: ${submission.workflow_state}`);
        } catch (error) {
          console.log(`   Could not submit assignment: ${error.message}`);
        } finally {
          // 清理测试文件
          fs.unlinkSync(testFilePath);
        }
      }
    }

    return course.id;
  } catch (error) {
    console.error('Student test error:', error.message);
    return null;
  }
}

async function testWithAdmin(courseId) {
  console.log('\n========== TESTING WITH ADMIN ACCOUNT ==========\n');
  const client = new CanvasClient(ADMIN_TOKEN, DOMAIN);

  try {
    // 1. 获取管理员信息
    console.log('1. Getting admin profile...');
    const profile = await client.getUserProfile();
    console.log(`   Admin: ${profile.name} (ID: ${profile.id})`);

    // 2. 创建或获取测试课程
    let course;
    if (courseId) {
      console.log(`\n2. Using existing course (ID: ${courseId})...`);
      course = await client.getCourse(courseId);
    } else {
      console.log('\n2. Creating test course...');
      // Use a default account ID or get from sub-accounts
      const accountId = 1; // Default root account

      course = await client.createCourse({
        account_id: accountId,
        name: `Test Course ${Date.now()}`,
        course_code: `TEST-${Date.now()}`
      });
      console.log(`   Created course: ${course.name} (ID: ${course.id})`);

      // 发布课程
      await client.updateCourse({
        course_id: course.id,
        event: 'offer'
      });
      console.log('   Course published');
    }

    // 3. 创建测验
    console.log('\n3. Creating quiz...');
    const quiz = await client.createQuiz(course.id, {
      title: `Test Quiz ${new Date().toLocaleString()}`,
      quiz_type: 'assignment',
      time_limit: 60,
      published: false,
      points_possible: 30
    });
    console.log(`   Created quiz: ${quiz.title} (ID: ${quiz.id})`);

    // 4. 添加测验题目
    console.log('\n4. Adding quiz questions...');

    // 添加单选题
    const mcQuestion = await client.createQuizQuestion(course.id, quiz.id, {
      question_name: 'Multiple Choice Question',
      question_text: 'What is 2 + 2?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '3', weight: 0 },
        { text: '4', weight: 100 },
        { text: '5', weight: 0 },
        { text: '6', weight: 0 }
      ],
      correct_comments: 'Correct! 2 + 2 = 4',
      incorrect_comments: 'Incorrect. Please review basic arithmetic.'
    });
    console.log(`   Added multiple choice question (ID: ${mcQuestion.id})`);

    // 添加判断题
    const tfQuestion = await client.createQuizQuestion(course.id, quiz.id, {
      question_name: 'True/False Question',
      question_text: 'The Earth is flat.',
      question_type: 'true_false_question',
      points_possible: 10,
      answers: [
        { text: 'True', weight: 0 },
        { text: 'False', weight: 100 }
      ]
    });
    console.log(`   Added true/false question (ID: ${tfQuestion.id})`);

    // 添加简答题
    const saQuestion = await client.createQuizQuestion(course.id, quiz.id, {
      question_name: 'Short Answer Question',
      question_text: 'What is the capital of France?',
      question_type: 'short_answer_question',
      points_possible: 10,
      answers: [
        { text: 'Paris', weight: 100 },
        { text: 'paris', weight: 100 }
      ]
    });
    console.log(`   Added short answer question (ID: ${saQuestion.id})`);

    // 5. 列出所有题目
    console.log('\n5. Listing all quiz questions...');
    const allQuestions = await client.listQuizQuestions(course.id, quiz.id);
    console.log(`   Total questions: ${allQuestions.length}`);
    allQuestions.forEach(q => {
      console.log(`   - ${q.question_name} (${q.question_type}, ${q.points_possible} points)`);
    });

    // 6. 更新一个题目
    console.log('\n6. Updating a question...');
    const updatedQuestion = await client.updateQuizQuestion(course.id, quiz.id, mcQuestion.id, {
      question_text: 'What is 2 + 2? (Updated)',
      points_possible: 15
    });
    console.log(`   Updated question points to ${updatedQuestion.points_possible}`);

    // 7. 发布测验
    console.log('\n7. Publishing quiz...');
    const publishedQuiz = await client.updateQuiz(course.id, quiz.id, { published: true });
    console.log(`   Quiz published: ${publishedQuiz.published}`);

    // 8. 创建支持文件上传的作业
    console.log('\n8. Creating assignment that accepts file uploads...');
    const assignment = await client.createAssignment({
      course_id: course.id,
      name: `File Upload Assignment ${new Date().toLocaleString()}`,
      description: 'Please upload your work as a file',
      submission_types: ['online_upload', 'online_text_entry'],
      points_possible: 100,
      published: true
    });
    console.log(`   Created assignment: ${assignment.name} (ID: ${assignment.id})`);

    console.log('\n✅ All admin tests completed successfully!');

  } catch (error) {
    console.error('Admin test error:', error.message);
  }
}

// 运行测试
async function runTests() {
  console.log('Starting Canvas API tests...');
  console.log('Domain:', DOMAIN);

  // 先用学生账号测试
  const courseId = await testWithStudent();

  // 然后用管理员账号测试
  await testWithAdmin(courseId);

  console.log('\n========== ALL TESTS COMPLETED ==========');
}

runTests().catch(console.error);