// src/client.ts

import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  CanvasCourse, 
  CanvasAssignment,
  CanvasSubmission,
  CanvasUser,
  CanvasEnrollment,
  CreateCourseArgs,
  UpdateCourseArgs,
  CreateAssignmentArgs,
  UpdateAssignmentArgs,
  SubmitGradeArgs,
  EnrollUserArgs,
  CanvasAPIError,
  CanvasDiscussionTopic,
  CanvasModule,
  CanvasModuleItem,
  CanvasQuiz,
  CanvasAnnouncement,
  CanvasUserProfile,
  CanvasScope,
  CanvasAssignmentSubmission,
  CanvasPage,
  CanvasCalendarEvent,
  CanvasRubric,
  CanvasAssignmentGroup,
  CanvasConversation,
  CanvasNotification,
  CanvasFile,
  CanvasSyllabus,
  CanvasDashboard,
  SubmitAssignmentArgs,
  FileUploadArgs,
  CanvasAccount,
  CreateUserArgs,
  CanvasAccountReport,
  CreateReportArgs,
  ListAccountCoursesArgs,
  ListAccountUsersArgs,
  CanvasQuizQuestion,
  QuizSubmission,
  QuizSubmissionAnswer
} from './types.js';

export class CanvasClient {
  private client: AxiosInstance;
  private baseURL: string;
  private token: string;
  private maxRetries: number = 3;
  private retryDelay: number = 1000;

  constructor(token: string, domain: string, options?: { maxRetries?: number; retryDelay?: number }) {
    this.token = token;
    this.baseURL = `https://${domain}/api/v1`;
    this.maxRetries = options?.maxRetries ?? 3;
    this.retryDelay = options?.retryDelay ?? 1000;

    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000 // 30 second timeout
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.error(`[Canvas API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[Canvas API] Request error:', error.message || error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for pagination and retry logic
    this.client.interceptors.response.use(
      async (response) => {
        const { headers, data } = response;
        const linkHeader = headers.link;
        const contentType = headers['content-type'] || '';

        // Only handle pagination for JSON responses
        if (Array.isArray(data) && linkHeader && contentType.includes('application/json')) {
          let allData = [...data];
          let nextUrl = this.getNextPageUrl(linkHeader);
          const maxPages = 1000; // Safety limit to prevent infinite loops
          let pageCount = 1;

          while (nextUrl && pageCount < maxPages) {
            console.error(`[Canvas API] Fetching page ${pageCount + 1}...`);
            const nextResponse = await this.client.get(nextUrl);
            allData = [...allData, ...nextResponse.data];
            nextUrl = this.getNextPageUrl(nextResponse.headers.link);
            pageCount++;
          }

          if (pageCount >= maxPages) {
            console.error(`[Canvas API] Warning: Reached maximum page limit (${maxPages}). Some data may be missing.`);
          }

          response.data = allData;
        }

        return response;
      },
      async (error: AxiosError) => {
        const config = error.config as any;
        
        // Retry logic for specific errors
        if (this.shouldRetry(error) && config && config.__retryCount < this.maxRetries) {
          config.__retryCount = config.__retryCount || 0;
          config.__retryCount++;
          
          const delay = this.retryDelay * Math.pow(2, config.__retryCount - 1); // Exponential backoff
          console.error(`[Canvas API] Retrying request (${config.__retryCount}/${this.maxRetries}) after ${delay}ms`);
          
          await this.sleep(delay);
          return this.client.request(config);
        }

        // Transform error with better handling for non-JSON responses
        if (error.response) {
          const { status, data, headers } = error.response;
          const contentType = headers?.['content-type'] || 'unknown';
          console.error(`[Canvas API] Error response: ${status}, Content-Type: ${contentType}, Data type: ${typeof data}`);
          
          let errorMessage: string;
          
          try {
            // Check if data is already a string (HTML error pages, plain text, etc.)
            if (typeof data === 'string') {
              errorMessage = data.length > 200 ? data.substring(0, 200) + '...' : data;
            } else if (data && typeof data === 'object') {
              // Handle structured Canvas API error responses
              if ((data as any)?.message) {
                errorMessage = (data as any).message;
              } else if ((data as any)?.errors && Array.isArray((data as any).errors)) {
                errorMessage = (data as any).errors.map((err: any) => err.message || err).join(', ');
              } else {
                errorMessage = JSON.stringify(data);
              }
            } else {
              errorMessage = String(data);
            }
          } catch (jsonError) {
            // Fallback if JSON operations fail
            errorMessage = String(data);
          }
          
          throw new CanvasAPIError(
            `Canvas API Error (${status}): ${errorMessage}`, 
            status, 
            data
          );
        }
        
        // Handle network errors or other issues
        if (error.request) {
          console.error('[Canvas API] Network error - no response received:', error.message);
          throw new CanvasAPIError(
            `Network error: ${error.message}`,
            0,
            null
          );
        }
        
        console.error('[Canvas API] Unexpected error:', error.message);
        throw error;
      }
    );
  }

  private shouldRetry(error: AxiosError): boolean {
    if (!error.response) return true; // Network errors
    
    const status = error.response.status;
    return status === 429 || status >= 500; // Rate limit or server errors
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getNextPageUrl(linkHeader: string | undefined): string | null {
    if (!linkHeader) return null;
    
    const links = linkHeader.split(',');
    const nextLink = links.find(link => link.includes('rel="next"'));
    if (!nextLink) return null;

    const match = nextLink.match(/<(.+?)>/);
    return match ? match[1] : null;
  }

  // ---------------------
  // HEALTH CHECK
  // ---------------------
  async healthCheck(): Promise<{ status: 'ok' | 'error'; timestamp: string; user?: any }> {
    try {
      const user = await this.getUserProfile();
      return {
        status: 'ok',
        timestamp: new Date().toISOString(),
        user: { id: user.id, name: user.name }
      };
    } catch (error) {
      return {
        status: 'error',
        timestamp: new Date().toISOString()
      };
    }
  }

  // ---------------------
  // COURSES (Enhanced)
  // ---------------------
  async listCourses(includeEnded: boolean = false): Promise<CanvasCourse[]> {
    const params: any = {
      include: ['total_students', 'teachers', 'term', 'course_progress']
    };
    
    if (!includeEnded) {
      params.state = ['available', 'completed'];
    }

    const response = await this.client.get('/courses', { params });
    return response.data;
  }

  async getCourse(courseId: number): Promise<CanvasCourse> {
    const response = await this.client.get(`/courses/${courseId}`, {
      params: {
        include: ['total_students', 'teachers', 'term', 'course_progress', 'sections', 'syllabus_body']
      }
    });
    return response.data;
  }

  async createCourse(args: CreateCourseArgs): Promise<CanvasCourse> {
    const { account_id, ...courseData } = args;
    const response = await this.client.post(`/accounts/${account_id}/courses`, {
      course: courseData
    });
    return response.data;
  }

  async updateCourse(args: UpdateCourseArgs): Promise<CanvasCourse> {
    const { course_id, ...courseData } = args;
    const response = await this.client.put(`/courses/${course_id}`, {
      course: courseData
    });
    return response.data;
  }

  async deleteCourse(courseId: number, event: 'delete' | 'conclude' = 'delete'): Promise<void> {
    await this.client.delete(`/courses/${courseId}`, {
      data: { event }
    });
  }

  // ---------------------
  // ASSIGNMENTS (Enhanced)
  // ---------------------
  async listAssignments(courseId: number, includeSubmissions: boolean = false): Promise<CanvasAssignment[]> {
    const params: any = {
      include: ['assignment_group', 'rubric', 'due_at']
    };
    
    if (includeSubmissions) {
      params.include.push('submission');
    }

    const response = await this.client.get(`/courses/${courseId}/assignments`, { params });
    return response.data;
  }

  async getAssignment(courseId: number, assignmentId: number, includeSubmission: boolean = false): Promise<CanvasAssignment> {
    const params: any = {
      include: ['assignment_group', 'rubric']
    };
    
    if (includeSubmission) {
      params.include.push('submission');
    }

    const response = await this.client.get(`/courses/${courseId}/assignments/${assignmentId}`, { params });
    return response.data;
  }

  async createAssignment(args: CreateAssignmentArgs): Promise<CanvasAssignment> {
    const { course_id, ...assignmentData } = args;
    const response = await this.client.post(`/courses/${course_id}/assignments`, {
      assignment: assignmentData
    });
    return response.data;
  }

  async updateAssignment(args: UpdateAssignmentArgs): Promise<CanvasAssignment> {
    const { course_id, assignment_id, ...assignmentData } = args;
    const response = await this.client.put(
      `/courses/${course_id}/assignments/${assignment_id}`,
      { assignment: assignmentData }
    );
    return response.data;
  }

  async deleteAssignment(courseId: number, assignmentId: number): Promise<void> {
    await this.client.delete(`/courses/${courseId}/assignments/${assignmentId}`);
  }

  // ---------------------
  // ASSIGNMENT GROUPS
  // ---------------------
  async listAssignmentGroups(courseId: number): Promise<CanvasAssignmentGroup[]> {
    const response = await this.client.get(`/courses/${courseId}/assignment_groups`, {
      params: {
        include: ['assignments']
      }
    });
    return response.data;
  }

  async getAssignmentGroup(courseId: number, groupId: number): Promise<CanvasAssignmentGroup> {
    const response = await this.client.get(`/courses/${courseId}/assignment_groups/${groupId}`, {
      params: {
        include: ['assignments']
      }
    });
    return response.data;
  }

  // ---------------------
  // SUBMISSIONS (Enhanced for Students)
  // ---------------------
  async getSubmissions(courseId: number, assignmentId: number): Promise<CanvasSubmission[]> {
    const response = await this.client.get(
      `/courses/${courseId}/assignments/${assignmentId}/submissions`,
      {
        params: {
          include: ['submission_comments', 'rubric_assessment', 'assignment']
        }
      }
    );
    return response.data;
  }

  async getSubmission(courseId: number, assignmentId: number, userId: number | 'self' = 'self'): Promise<CanvasSubmission> {
    const response = await this.client.get(
      `/courses/${courseId}/assignments/${assignmentId}/submissions/${userId}`,
      {
        params: {
          include: ['submission_comments', 'rubric_assessment', 'assignment']
        }
      }
    );
    return response.data;
  }

  async submitGrade(args: SubmitGradeArgs): Promise<CanvasSubmission> {
    const { course_id, assignment_id, user_id, grade, comment } = args;
    const response = await this.client.put(
      `/courses/${course_id}/assignments/${assignment_id}/submissions/${user_id}`, {
      submission: {
        posted_grade: grade,
        comment: comment ? { text_comment: comment } : undefined
      }
    });
    return response.data;
  }

  // Student submission with file support
  async submitAssignment(args: SubmitAssignmentArgs): Promise<CanvasAssignmentSubmission> {
    const { course_id, assignment_id, submission_type, body, url, file_ids } = args;
    
    const submissionData: any = {
      submission_type
    };

    if (body) submissionData.body = body;
    if (url) submissionData.url = url;
    if (file_ids && file_ids.length > 0) submissionData.file_ids = file_ids;

    const response = await this.client.post(
      `/courses/${course_id}/assignments/${assignment_id}/submissions`,
      { submission: submissionData }
    );
    return response.data;
  }

  // ---------------------
  // FILES (Enhanced)
  // ---------------------
  async listFiles(courseId: number, folderId?: number): Promise<CanvasFile[]> {
    const endpoint = folderId 
      ? `/folders/${folderId}/files`
      : `/courses/${courseId}/files`;
    
    const response = await this.client.get(endpoint);
    return response.data;
  }

  async getFile(fileId: number): Promise<CanvasFile> {
    const response = await this.client.get(`/files/${fileId}`);
    return response.data;
  }

  async uploadFile(args: FileUploadArgs): Promise<CanvasFile> {
    const { course_id, folder_id, name, size } = args;
    
    // Step 1: Get upload URL
    const uploadEndpoint = folder_id 
      ? `/folders/${folder_id}/files`
      : `/courses/${course_id}/files`;
      
    const uploadResponse = await this.client.post(uploadEndpoint, {
      name,
      size,
      content_type: args.content_type || 'application/octet-stream'
    });

    // Note: Actual file upload would require multipart form data handling
    // This is a simplified version - in practice, you'd need to handle the 
    // two-step upload process Canvas uses
    return uploadResponse.data;
  }

  async listFolders(courseId: number): Promise<any[]> {
    const response = await this.client.get(`/courses/${courseId}/folders`);
    return response.data;
  }

  // ---------------------
  // PAGES
  // ---------------------
  async listPages(courseId: number): Promise<CanvasPage[]> {
    const response = await this.client.get(`/courses/${courseId}/pages`);
    return response.data;
  }

  async getPage(courseId: number, pageUrl: string): Promise<CanvasPage> {
    const response = await this.client.get(`/courses/${courseId}/pages/${pageUrl}`);
    return response.data;
  }

  // ---------------------
  // CALENDAR EVENTS
  // ---------------------
  async listCalendarEvents(startDate?: string, endDate?: string): Promise<CanvasCalendarEvent[]> {
    const params: any = {
      type: 'event',
      all_events: true
    };
    
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await this.client.get('/calendar_events', { params });
    return response.data;
  }

  async getUpcomingAssignments(limit: number = 10): Promise<CanvasAssignment[]> {
    const response = await this.client.get('/users/self/upcoming_events', {
      params: { limit }
    });
    return response.data.filter((event: any) => event.assignment);
  }

  // ---------------------
  // RUBRICS
  // ---------------------
  async listRubrics(courseId: number): Promise<CanvasRubric[]> {
    const response = await this.client.get(`/courses/${courseId}/rubrics`);
    return response.data;
  }

  async getRubric(courseId: number, rubricId: number): Promise<CanvasRubric> {
    const response = await this.client.get(`/courses/${courseId}/rubrics/${rubricId}`);
    return response.data;
  }

  // ---------------------
  // DASHBOARD
  // ---------------------
  async getDashboard(): Promise<CanvasDashboard> {
    const response = await this.client.get('/users/self/dashboard');
    return response.data;
  }

  async getDashboardCards(): Promise<any[]> {
    const response = await this.client.get('/dashboard/dashboard_cards');
    return response.data;
  }

  // ---------------------
  // SYLLABUS
  // ---------------------
  async getSyllabus(courseId: number): Promise<CanvasSyllabus> {
    const response = await this.client.get(`/courses/${courseId}`, {
      params: {
        include: ['syllabus_body']
      }
    });
    return {
      course_id: courseId,
      syllabus_body: response.data.syllabus_body
    };
  }

  // ---------------------
  // CONVERSATIONS/MESSAGING
  // ---------------------
  async listConversations(): Promise<CanvasConversation[]> {
    const response = await this.client.get('/conversations');
    return response.data;
  }

  async getConversation(conversationId: number): Promise<CanvasConversation> {
    const response = await this.client.get(`/conversations/${conversationId}`);
    return response.data;
  }

  async createConversation(recipients: string[], body: string, subject?: string): Promise<CanvasConversation> {
    const response = await this.client.post('/conversations', {
      recipients,
      body,
      subject
    });
    return response.data;
  }

  async deleteConversation(conversationId: number): Promise<void> {
    await this.client.delete(`/conversations/${conversationId}`);
  }

  // ---------------------
  // NOTIFICATIONS
  // ---------------------
  async listNotifications(): Promise<CanvasNotification[]> {
    const response = await this.client.get('/users/self/activity_stream');
    return response.data;
  }

  // ---------------------
  // USERS AND ENROLLMENTS (Enhanced)
  // ---------------------
  async listUsers(courseId: number): Promise<CanvasUser[]> {
    const response = await this.client.get(`/courses/${courseId}/users`, {
      params: {
        include: ['email', 'enrollments', 'avatar_url']
      }
    });
    return response.data;
  }

  async getEnrollments(courseId: number): Promise<CanvasEnrollment[]> {
    const response = await this.client.get(`/courses/${courseId}/enrollments`);
    return response.data;
  }

  async enrollUser(args: EnrollUserArgs): Promise<CanvasEnrollment> {
    const { course_id, user_id, role = 'StudentEnrollment', enrollment_state = 'active' } = args;
    const response = await this.client.post(`/courses/${course_id}/enrollments`, {
      enrollment: {
        user_id,
        type: role,
        enrollment_state
      }
    });
    return response.data;
  }

  async unenrollUser(courseId: number, enrollmentId: number): Promise<void> {
    await this.client.delete(`/courses/${courseId}/enrollments/${enrollmentId}`);
  }

  // ---------------------
  // GRADES (Enhanced)
  // ---------------------
  async getCourseGrades(courseId: number): Promise<CanvasEnrollment[]> {
    const response = await this.client.get(`/courses/${courseId}/enrollments`, {
      params: {
        include: ['grades', 'observed_users']
      }
    });
    return response.data;
  }

  async getUserGrades(): Promise<any> {
    const response = await this.client.get('/users/self/grades');
    return response.data;
  }

  // ---------------------
  // USER PROFILE (Enhanced)
  // ---------------------
  async getUserProfile(): Promise<CanvasUserProfile> {
    const response = await this.client.get('/users/self/profile');
    return response.data;
  }

  async updateUserProfile(profileData: Partial<CanvasUserProfile>): Promise<CanvasUserProfile> {
    const response = await this.client.put('/users/self', {
      user: profileData
    });
    return response.data;
  }

  // ---------------------
  // STUDENT COURSES (Enhanced)
  // ---------------------
  async listStudentCourses(): Promise<CanvasCourse[]> {
    const response = await this.client.get('/courses', {
      params: {
        include: ['enrollments', 'total_students', 'term', 'course_progress'],
        enrollment_state: 'active'
      }
    });
    return response.data;
  }

  // ---------------------
  // MODULES (Enhanced)
  // ---------------------
  async listModules(courseId: number): Promise<CanvasModule[]> {
    const response = await this.client.get(`/courses/${courseId}/modules`, {
      params: {
        include: ['items']
      }
    });
    return response.data;
  }

  async getModule(courseId: number, moduleId: number): Promise<CanvasModule> {
    const response = await this.client.get(`/courses/${courseId}/modules/${moduleId}`, {
      params: {
        include: ['items']
      }
    });
    return response.data;
  }

  async listModuleItems(courseId: number, moduleId: number): Promise<CanvasModuleItem[]> {
    const response = await this.client.get(`/courses/${courseId}/modules/${moduleId}/items`, {
      params: {
        include: ['content_details']
      }
    });
    return response.data;
  }

  async getModuleItem(courseId: number, moduleId: number, itemId: number): Promise<CanvasModuleItem> {
    const response = await this.client.get(`/courses/${courseId}/modules/${moduleId}/items/${itemId}`, {
      params: {
        include: ['content_details']
      }
    });
    return response.data;
  }

  async markModuleItemComplete(courseId: number, moduleId: number, itemId: number): Promise<void> {
    await this.client.put(`/courses/${courseId}/modules/${moduleId}/items/${itemId}/done`);
  }

  // ---------------------
  // DISCUSSION TOPICS (Enhanced)
  // ---------------------
  async listDiscussionTopics(courseId: number): Promise<CanvasDiscussionTopic[]> {
    const response = await this.client.get(`/courses/${courseId}/discussion_topics`, {
      params: {
        include: ['assignment']
      }
    });
    return response.data;
  }

  async getDiscussionTopic(courseId: number, topicId: number): Promise<CanvasDiscussionTopic> {
    const response = await this.client.get(`/courses/${courseId}/discussion_topics/${topicId}`, {
      params: {
        include: ['assignment']
      }
    });
    return response.data;
  }

  async postToDiscussion(courseId: number, topicId: number, message: string): Promise<any> {
    const response = await this.client.post(`/courses/${courseId}/discussion_topics/${topicId}/entries`, {
      message
    });
    return response.data;
  }

  // ---------------------
  // ANNOUNCEMENTS (Enhanced)
  // ---------------------
  async listAnnouncements(courseId: string): Promise<CanvasAnnouncement[]> {
    const response = await this.client.get(`/courses/${courseId}/discussion_topics`, {
      params: {
        only_announcements: true
      }
    });
    return response.data || [];
  }

  async createAnnouncement(courseId: number, announcementData: {
    title: string;
    message: string;
    is_announcement?: boolean;
    published?: boolean;
    delayed_post_at?: string;
    attachment?: any;
  }): Promise<CanvasAnnouncement> {
    // For announcements, published must be true or omitted (can't be draft)
    const postData: any = {
      title: announcementData.title,
      message: announcementData.message,
      is_announcement: announcementData.is_announcement !== false, // default to true
      delayed_post_at: announcementData.delayed_post_at,
      attachment: announcementData.attachment
    };
    
    // Only add published if it's explicitly true or if no delayed posting
    if (announcementData.published === true || !announcementData.delayed_post_at) {
      postData.published = true;
    }
    
    const response = await this.client.post(`/courses/${courseId}/discussion_topics`, postData);
    return response.data;
  }

  async deleteAnnouncement(courseId: number, announcementId: number): Promise<void> {
    await this.client.delete(`/courses/${courseId}/discussion_topics/${announcementId}`);
  }

  // ---------------------
  // QUIZZES (Enhanced)
  // ---------------------
  async listQuizzes(courseId: string): Promise<CanvasQuiz[]> {
    const response = await this.client.get(`/courses/${courseId}/quizzes`);
    return response.data;
  }

  async getQuiz(courseId: string, quizId: number): Promise<CanvasQuiz> {
    const response = await this.client.get(`/courses/${courseId}/quizzes/${quizId}`);
    return response.data;
  }

  async createQuiz(courseId: number, quizData: Partial<CanvasQuiz>): Promise<CanvasQuiz> {
    const response = await this.client.post(`/courses/${courseId}/quizzes`, {
      quiz: quizData
    });
    return response.data;
  }

  async updateQuiz(courseId: number, quizId: number, quizData: Partial<CanvasQuiz>): Promise<CanvasQuiz> {
    const response = await this.client.put(`/courses/${courseId}/quizzes/${quizId}`, {
      quiz: quizData
    });
    return response.data;
  }

  async deleteQuiz(courseId: number, quizId: number): Promise<void> {
    await this.client.delete(`/courses/${courseId}/quizzes/${quizId}`);
  }

  async startQuizAttempt(courseId: number, quizId: number): Promise<QuizSubmission> {
    try {
      const response = await this.client.post(`/courses/${courseId}/quizzes/${quizId}/submissions`);
      // Canvas returns the full response with quiz_submissions array
      return response.data;
    } catch (error: any) {
      // Canvas sometimes returns 500 but actually creates the submission
      // Also handle 409 (conflict) when attempt already exists
      const statusCode = error.statusCode || error.response?.status;
      if (statusCode === 500 || statusCode === 409) {
        if (statusCode === 500) {
          console.log('[Canvas API] Received 500 error, checking if submission was created anyway...');
        } else {
          console.log('[Canvas API] Quiz attempt already exists (409), fetching existing submission...');
        }

        try {
          // Wait a bit for Canvas to stabilize after 500 error
          if (statusCode === 500) {
            await new Promise(resolve => setTimeout(resolve, 500));
          }

          const getResponse = await this.client.get(`/courses/${courseId}/quizzes/${quizId}/submissions`);

          // Return the first (current) submission
          if (getResponse.data?.quiz_submissions?.length > 0) {
            console.log('[Canvas API] Successfully retrieved submission');
            return getResponse.data.quiz_submissions[0];
          } else if (getResponse.data) {
            console.log('[Canvas API] Successfully retrieved submission data');
            return getResponse.data;
          }
        } catch (getError) {
          // If 500 and we can't get submission, the operation really failed
          console.log('[Canvas API] Could not retrieve submission after error');
          throw error;
        }
      }
      // Re-throw other errors
      throw error;
    }
  }

  async submitQuizAttempt(courseId: number, quizId: number, submissionId: number, answers: QuizSubmissionAnswer[], validationToken?: string): Promise<QuizSubmission> {
    // Submit answers via the Quiz Submission Questions API
    // This is the standard method for submitting quiz answers
    try {
      const answersPayload = {
        attempt: 1,
        validation_token: validationToken || null,
        quiz_questions: answers.map(answer => {
          const questionAnswer: any = {
            id: answer.question_id.toString()  // ID must be a string
          };

          // Set the answer based on the question type
          if (answer.answer_id !== undefined) {
            // For multiple choice and true/false questions, answer should be the integer answer_id
            questionAnswer.answer = answer.answer_id;
          } else if (answer.answer !== undefined) {
            // For short answer, essay, numerical questions - use the actual answer value
            questionAnswer.answer = answer.answer;
          } else if (answer.match !== undefined) {
            // For matching questions
            questionAnswer.answer = answer.match;
          }

          return questionAnswer;
        })
      };

      console.log('Submitting answers:', JSON.stringify(answersPayload, null, 2));

      // Submit to the correct endpoint: /quiz_submissions/:id/questions
      const response = await this.client.post(
        `/quiz_submissions/${submissionId}/questions`,
        answersPayload
      );

      console.log('Answers submitted successfully');
    } catch (error) {
      console.error('Error submitting answers:', (error as any).message);
      if ((error as any).response?.data) {
        console.error('Error details:', (error as any).response.data);
      }
    }

    // Then complete the quiz submission
    const completeResponse = await this.client.post(
      `/courses/${courseId}/quizzes/${quizId}/submissions/${submissionId}/complete`,
      {
        attempt: 1,
        validation_token: validationToken || null
      }
    );

    return completeResponse.data;
  }

  // Quiz Questions
  async listQuizQuestions(
    courseId: number,
    quizId: number,
    options?: {
      quiz_submission_id?: number;
      quiz_submission_attempt?: number;
      use_submission_endpoint?: boolean; // 新选项：直接使用submission端点
    }
  ): Promise<CanvasQuizQuestion[]> {
    // 如果指定使用submission端点，直接调用quiz_submissions API
    if (options?.use_submission_endpoint && options?.quiz_submission_id) {
      const response = await this.client.get(`/quiz_submissions/${options.quiz_submission_id}/questions`);
      return response.data.quiz_submission_questions || [];
    }

    // 否则使用原有的courses API（支持submission参数）
    const params: any = {};
    if (options?.quiz_submission_id) {
      params.quiz_submission_id = options.quiz_submission_id;
    }
    if (options?.quiz_submission_attempt) {
      params.quiz_submission_attempt = options.quiz_submission_attempt;
    }

    const response = await this.client.get(`/courses/${courseId}/quizzes/${quizId}/questions`, {
      params
    });
    return response.data;
  }

  async getQuizQuestion(courseId: number, quizId: number, questionId: number): Promise<CanvasQuizQuestion> {
    const response = await this.client.get(`/courses/${courseId}/quizzes/${quizId}/questions/${questionId}`);
    return response.data;
  }

  async getQuizSubmissionQuestions(submissionId: number): Promise<any> {
    const response = await this.client.get(`/quiz_submissions/${submissionId}/questions`);
    return response.data;
  }

  async createQuizQuestion(courseId: number, quizId: number, questionData: Partial<CanvasQuizQuestion>): Promise<CanvasQuizQuestion> {
    const response = await this.client.post(`/courses/${courseId}/quizzes/${quizId}/questions`, {
      question: questionData
    });
    return response.data;
  }

  async updateQuizQuestion(courseId: number, quizId: number, questionId: number, questionData: Partial<CanvasQuizQuestion>): Promise<CanvasQuizQuestion> {
    const response = await this.client.put(`/courses/${courseId}/quizzes/${quizId}/questions/${questionId}`, {
      question: questionData
    });
    return response.data;
  }

  async deleteQuizQuestion(courseId: number, quizId: number, questionId: number): Promise<void> {
    await this.client.delete(`/courses/${courseId}/quizzes/${quizId}/questions/${questionId}`);
  }

  // Enhanced file upload with local file support
  async uploadFileFromPath(filePath: string, courseId?: number, folderId?: number): Promise<CanvasFile> {
    const fs = await import('fs');
    const path = await import('path');
    const FormData = (await import('form-data')).default;

    const stats = await fs.promises.stat(filePath);
    const fileName = path.default.basename(filePath);

    // Step 1: Get upload URL
    // For students, use user files endpoint instead of course files
    const uploadEndpoint = folderId
      ? `/folders/${folderId}/files`
      : courseId
      ? `/users/self/files`  // Changed to user's own files space
      : '/users/self/files';

    const uploadParams = {
      name: fileName,
      size: stats.size,
      on_duplicate: 'rename'
    };

    const uploadUrlResponse = await this.client.post(uploadEndpoint, uploadParams);
    const { upload_url, upload_params } = uploadUrlResponse.data;

    // Step 2: Upload the file
    const formData = new FormData();
    Object.entries(upload_params).forEach(([key, value]) => {
      formData.append(key, value as string);
    });

    const fileStream = fs.default.createReadStream(filePath);
    formData.append('file', fileStream, fileName);

    const uploadResponse = await axios.post(upload_url, formData, {
      headers: formData.getHeaders(),
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });

    // Step 3: Confirm upload
    if (uploadResponse.data.location) {
      const confirmResponse = await this.client.get(uploadResponse.data.location);
      return confirmResponse.data;
    }

    return uploadResponse.data;
  }

  // ---------------------
  // SCOPES (Enhanced)
  // ---------------------
  async listTokenScopes(accountId: number, groupBy?: string): Promise<CanvasScope[]> {
    const params: Record<string, string> = {};
    if (groupBy) {
      params.group_by = groupBy;
    }

    const response = await this.client.get(`/accounts/${accountId}/scopes`, { params });
    return response.data;
  }

  // ---------------------
  // ACCOUNT MANAGEMENT (New)
  // ---------------------
  async getAccount(accountId: number): Promise<CanvasAccount> {
    const response = await this.client.get(`/accounts/${accountId}`);
    return response.data;
  }

  async listAccountCourses(args: ListAccountCoursesArgs): Promise<CanvasCourse[]> {
    const { account_id, ...params } = args;
    const response = await this.client.get(`/accounts/${account_id}/courses`, { params });
    return response.data;
  }

  async listAccountUsers(args: ListAccountUsersArgs): Promise<{ users: CanvasUser[], pagination?: { current_page: number, total_pages?: number, next_page?: number, prev_page?: number } }> {
    const { account_id, page = 1, per_page = 20, ...params } = args;
    
    // Limit per_page to maximum of 20
    const limitedPerPage = Math.min(per_page, 20);
    
    // Create a new axios instance without interceptors for this specific request
    const { default: newAxios } = await import('axios');
    const simpleClient = newAxios.create({
      baseURL: this.baseURL,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });

    const response = await simpleClient.get(`/accounts/${account_id}/users`, { 
      params: { 
        ...params, 
        page, 
        per_page: limitedPerPage 
      } 
    });

    // Parse pagination info from Link header
    const linkHeader = response.headers.link;
    let pagination: any = {
      current_page: page
    };

    if (linkHeader) {
      const links = linkHeader.split(',').reduce((acc: any, link: string) => {
        const match = link.match(/<(.+?)>;\s*rel="(\w+)"/);
        if (match) {
          const url = new URL(match[1]);
          const pageNum = parseInt(url.searchParams.get('page') || '1');
          acc[match[2]] = pageNum;
        }
        return acc;
      }, {});

      if (links.next) pagination.next_page = links.next;
      if (links.prev) pagination.prev_page = links.prev;
      if (links.last) pagination.total_pages = links.last;
    }

    return {
      users: response.data,
      pagination
    };
  }

  async createUser(args: CreateUserArgs): Promise<CanvasUser> {
    const { account_id, ...userData } = args;
    const response = await this.client.post(`/accounts/${account_id}/users`, userData);
    return response.data;
  }

  async listSubAccounts(accountId: number): Promise<CanvasAccount[]> {
    const response = await this.client.get(`/accounts/${accountId}/sub_accounts`);
    return response.data;
  }

  // ---------------------
  // ACCOUNT REPORTS (New)
  // ---------------------
  async getAccountReports(accountId: number): Promise<any[]> {
    const response = await this.client.get(`/accounts/${accountId}/reports`);
    return response.data;
  }

  async createAccountReport(args: CreateReportArgs): Promise<CanvasAccountReport> {
    const { account_id, report, parameters } = args;
    const response = await this.client.post(`/accounts/${account_id}/reports/${report}`, {
      parameters: parameters || {}
    });
    return response.data;
  }

  async getAccountReport(accountId: number, reportType: string, reportId: number): Promise<CanvasAccountReport> {
    const response = await this.client.get(`/accounts/${accountId}/reports/${reportType}/${reportId}`);
    return response.data;
  }
}