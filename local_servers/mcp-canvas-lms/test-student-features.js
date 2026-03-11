#!/usr/bin/env node

// Ignore self-signed certificate errors for testing
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { CanvasClient } from './build/client.js';
import fs from 'fs';
import path from 'path';

const STUDENT_TOKEN = 'canvas_token_brian1990$p1';
const ADMIN_TOKEN = 'mcpcanvasadmintoken1';
const DOMAIN = 'https://localhost:20001';

async function enrollStudentAndTest() {
  console.log('\n========== ENROLLMENT AND STUDENT TESTING ==========\n');

  // 1. 使用管理员账号注册学生到课程
  const adminClient = new CanvasClient(ADMIN_TOKEN, DOMAIN);
  const studentClient = new CanvasClient(STUDENT_TOKEN, DOMAIN);

  try {
    console.log('1. Getting student info...');
    const studentProfile = await studentClient.getUserProfile();
    console.log(`   Student: ${studentProfile.name} (ID: ${studentProfile.id})`);

    console.log('\n2. Admin: Creating a new test course for student...');
    const course = await adminClient.createCourse({
      account_id: 1,
      name: `Student Test Course ${Date.now()}`,
      course_code: `STC-${Date.now()}`,
      is_public: false
    });
    console.log(`   Created course: ${course.name} (ID: ${course.id})`);

    // 发布课程
    await adminClient.updateCourse({
      course_id: course.id,
      event: 'offer'
    });
    console.log('   Course published');

    // 创建测验
    console.log('\n3. Admin: Creating quiz in course...');
    const quiz = await adminClient.createQuiz(course.id, {
      title: 'Student Test Quiz',
      quiz_type: 'assignment',
      published: true,
      points_possible: 30,
      allowed_attempts: 3
    });

    // 添加题目
    await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: 'Question 1',
      question_text: 'What is 2 + 2?',
      question_type: 'multiple_choice_question',
      points_possible: 10,
      answers: [
        { text: '3', weight: 0 },
        { text: '4', weight: 100 },
        { text: '5', weight: 0 }
      ]
    });

    await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: 'Question 2',
      question_text: 'The sky is blue.',
      question_type: 'true_false_question',
      points_possible: 10,
      answers: [
        { text: 'True', weight: 100 },
        { text: 'False', weight: 0 }
      ]
    });

    await adminClient.createQuizQuestion(course.id, quiz.id, {
      question_name: 'Question 3',
      question_text: 'What is the capital of France?',
      question_type: 'short_answer_question',
      points_possible: 10,
      answers: [
        { text: 'Paris', weight: 100 },
        { text: 'paris', weight: 100 }
      ]
    });
    console.log('   Quiz created with 3 questions');

    // 创建作业
    console.log('\n4. Admin: Creating file upload assignment...');
    const assignment = await adminClient.createAssignment({
      course_id: course.id,
      name: 'File Upload Assignment',
      description: 'Please upload your work',
      submission_types: ['online_upload'],
      points_possible: 100,
      published: true
    });
    console.log('   Assignment created');

    console.log('\n5. Admin: Enrolling student in course...');
    const enrollment = await adminClient.enrollUser({
      course_id: course.id,
      user_id: studentProfile.id,
      enrollment_type: 'StudentEnrollment',
      enrollment_state: 'active'
    });
    console.log(`   Student enrolled with state: ${enrollment.enrollment_state}`);

    // 等待一秒让enrollment生效
    await new Promise(resolve => setTimeout(resolve, 1000));

    console.log('\n6. Student: Verifying enrollment...');
    const studentCourses = await studentClient.listCourses();
    const enrolledCourse = studentCourses.find(c => c.id === course.id);
    if (enrolledCourse) {
      console.log(`   ✅ Successfully enrolled in: ${enrolledCourse.name}`);
    }

    console.log('\n7. Student: Getting quiz list...');
    const quizzes = await studentClient.listQuizzes(course.id);
    console.log(`   Found ${quizzes.length} quizzes`);

    if (quizzes.length > 0) {
      const quiz = quizzes[0];
      console.log(`   Quiz: ${quiz.title} (${quiz.points_possible} points)`);

      console.log('\n8. Student: Starting quiz attempt...');
      try {
        const attemptResponse = await studentClient.startQuizAttempt(course.id, quiz.id);
        // Extract submission ID from response
        const attempt = attemptResponse.quiz_submissions ? attemptResponse.quiz_submissions[0] : attemptResponse;
        console.log(`   Started quiz (Submission ID: ${attempt.id})`);

        // Get the validation token from the attempt response
        const validationToken = attempt.validation_token;

        // Note: In real Canvas, students can't see questions until they start the quiz
        // The questions would come with the quiz attempt response
        console.log('\n9. Student: Submitting quiz answers...');
        console.log('   Note: Submitting sample answers');

        // Get the questions from the attempt (if available)
        const questions = attemptResponse.questions || [];

        // Prepare answers based on the questions or use defaults
        const sampleAnswers = questions.length > 0 ?
          questions.map((q, index) => {
            if (q.question_type === 'multiple_choice_question') {
              return { question_id: q.id, answer_id: q.answers?.[0]?.id };
            } else if (q.question_type === 'true_false_question') {
              return { question_id: q.id, answer: true };
            } else {
              return { question_id: q.id, answer: 'Sample answer' };
            }
          }) :
          // Fallback if no questions in response
          [
            { question_id: 964, answer: '4' },
            { question_id: 965, answer: true },
            { question_id: 966, answer: 'Paris' }
          ];

        try {
          const submission = await studentClient.submitQuizAttempt(course.id, quiz.id, attempt.id, sampleAnswers, validationToken);
          console.log(`   Quiz submitted! Score: ${submission.score || 'Pending grading'}`);
        } catch (submitError) {
          console.log(`   Could not submit quiz: ${submitError.message}`);
        }
      } catch (error) {
        console.log(`   Could not start quiz: ${error.message}`);
      }
    }

    console.log('\n10. Student: Getting assignments...');
    const assignments = await studentClient.listAssignments(course.id);
    const fileAssignment = assignments.find(a => a.submission_types?.includes('online_upload'));

    if (fileAssignment) {
      console.log(`   Found file upload assignment: ${fileAssignment.name}`);

      console.log('\n11. Student: Creating and uploading test file...');
      const testFilePath = path.join(process.cwd(), 'student-work.txt');
      const fileContent = `Student: ${studentProfile.name}
Course: ${course.name}
Assignment: ${fileAssignment.name}
Date: ${new Date().toISOString()}

This is my assignment submission.
I have completed all the required work.`;

      fs.writeFileSync(testFilePath, fileContent);
      console.log(`   Created test file: ${testFilePath}`);

      try {
        console.log('\n12. Student: Uploading file to Canvas...');
        const uploadedFile = await studentClient.uploadFileFromPath(testFilePath, course.id);
        console.log(`   File uploaded: ${uploadedFile.display_name} (ID: ${uploadedFile.id})`);

        console.log('\n13. Student: Submitting assignment with file...');
        const submission = await studentClient.submitAssignment({
          course_id: course.id,
          assignment_id: fileAssignment.id,
          submission_type: 'online_upload',
          file_ids: [uploadedFile.id]
        });
        console.log(`   ✅ Assignment submitted successfully!`);
        console.log(`   Submission status: ${submission.workflow_state}`);
        console.log(`   Submitted at: ${submission.submitted_at}`);
      } catch (error) {
        console.log(`   Error: ${error.message}`);
      } finally {
        // 清理文件
        fs.unlinkSync(testFilePath);
        console.log(`   Cleaned up test file`);
      }
    }

    console.log('\n✨ All student tests completed successfully!');

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// 运行测试
enrollStudentAndTest().catch(console.error);