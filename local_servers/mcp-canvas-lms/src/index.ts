#!/usr/bin/env node

// src/index.ts

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  Tool
} from "@modelcontextprotocol/sdk/types.js";
import { CanvasClient } from "./client.js";
import * as dotenv from "dotenv";
import {
  CreateCourseArgs,
  UpdateCourseArgs,
  CreateAssignmentArgs,
  UpdateAssignmentArgs,
  SubmitGradeArgs,
  EnrollUserArgs,
  CanvasCourse,
  CanvasAssignmentSubmission,
  SubmitAssignmentArgs,
  FileUploadArgs,
  MCPServerConfig,
  CreateUserArgs,
  ListAccountCoursesArgs,
  ListAccountUsersArgs,
  CreateReportArgs
} from "./types.js";
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Session management for pagination
interface UserListSession {
  id: string;
  account_id: number;
  search_term?: string;
  sort?: 'username' | 'email' | 'sis_id' | 'last_login';
  order?: 'asc' | 'desc';
  per_page: number;
  current_page: number;
  created_at: number;
}

class SessionManager {
  private sessions: Map<string, UserListSession> = new Map();
  private readonly SESSION_TTL = 30 * 60 * 1000; // 30 minutes

  generateSessionId(): string {
    return 'sess_' + Math.random().toString(36).substring(2) + Date.now().toString(36);
  }

  createSession(params: Omit<UserListSession, 'id' | 'created_at'>): string {
    const sessionId = this.generateSessionId();
    this.sessions.set(sessionId, {
      ...params,
      id: sessionId,
      created_at: Date.now()
    });
    this.cleanExpiredSessions();
    return sessionId;
  }

  getSession(sessionId: string): UserListSession | null {
    const session = this.sessions.get(sessionId);
    if (!session) return null;
    
    if (Date.now() - session.created_at > this.SESSION_TTL) {
      this.sessions.delete(sessionId);
      return null;
    }
    
    return session;
  }

  updateSession(sessionId: string, updates: Partial<UserListSession>): boolean {
    const session = this.getSession(sessionId);
    if (!session) return false;
    
    this.sessions.set(sessionId, { ...session, ...updates });
    return true;
  }

  private cleanExpiredSessions(): void {
    const now = Date.now();
    for (const [id, session] of this.sessions.entries()) {
      if (now - session.created_at > this.SESSION_TTL) {
        this.sessions.delete(id);
      }
    }
  }
}

const sessionManager = new SessionManager();

// Enhanced tools list with all student-focused endpoints
const TOOLS: Tool[] = [
  // Health and system tools
  {
    name: "canvas_health_check",
    description: "Check the health and connectivity of the Canvas API",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },

  // Course management
  {
    name: "canvas_list_courses",
    description: "List all courses for the current user",
    inputSchema: {
      type: "object",
      properties: {
        include_ended: { type: "boolean", description: "Include ended courses" }
      },
      required: []
    }
  },
  {
    name: "canvas_get_course",
    description: "Get detailed information about a specific course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_create_course",
    description: "Create a new course in Canvas",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "ID of the account to create the course in" },
        name: { type: "string", description: "Name of the course" },
        course_code: { type: "string", description: "Course code (e.g., CS101)" },
        start_at: { type: "string", description: "Course start date (ISO format)" },
        end_at: { type: "string", description: "Course end date (ISO format)" },
        license: { type: "string", description: "Course license" },
        is_public: { type: "boolean", description: "Whether the course is public" },
        is_public_to_auth_users: { type: "boolean", description: "Whether the course is public to authenticated users" },
        public_syllabus: { type: "boolean", description: "Whether the syllabus is public" },
        public_syllabus_to_auth: { type: "boolean", description: "Whether the syllabus is public to authenticated users" },
        public_description: { type: "string", description: "Public description of the course" },
        allow_student_wiki_edits: { type: "boolean", description: "Whether students can edit the wiki" },
        allow_wiki_comments: { type: "boolean", description: "Whether wiki comments are allowed" },
        allow_student_forum_attachments: { type: "boolean", description: "Whether students can add forum attachments" },
        open_enrollment: { type: "boolean", description: "Whether the course has open enrollment" },
        self_enrollment: { type: "boolean", description: "Whether the course allows self enrollment" },
        restrict_enrollments_to_course_dates: { type: "boolean", description: "Whether to restrict enrollments to course start/end dates" },
        term_id: { type: "number", description: "ID of the enrollment term" },
        sis_course_id: { type: "string", description: "SIS course ID" },
        integration_id: { type: "string", description: "Integration ID for the course" },
        hide_final_grades: { type: "boolean", description: "Whether to hide final grades" },
        apply_assignment_group_weights: { type: "boolean", description: "Whether to apply assignment group weights" },
        time_zone: { type: "string", description: "Course time zone" },
        syllabus_body: { type: "string", description: "Course syllabus content" }
      },
      required: ["account_id", "name"]
    }
  },
  {
    name: "canvas_update_course",
    description: "Update an existing course in Canvas. Use event='offer' to publish, event='claim' to unpublish.",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course to update" },
        name: { type: "string", description: "New name for the course" },
        course_code: { type: "string", description: "New course code" },
        start_at: { type: "string", description: "New start date (ISO format)" },
        end_at: { type: "string", description: "New end date (ISO format)" },
        event: {
          type: "string",
          enum: ["offer", "claim", "conclude", "delete", "undelete"],
          description: "Course event - 'offer' to publish, 'claim' to unpublish, 'conclude' to end, 'delete' to delete, 'undelete' to restore"
        },
        is_public: { type: "boolean", description: "Whether the course is public" },
        is_public_to_auth_users: { type: "boolean", description: "Whether the course is public to authenticated users" },
        public_syllabus: { type: "boolean", description: "Whether the syllabus is public" },
        public_syllabus_to_auth: { type: "boolean", description: "Whether the syllabus is public to authenticated users" },
        public_description: { type: "string", description: "Public description of the course" },
        restrict_enrollments_to_course_dates: { type: "boolean", description: "Whether to restrict enrollments to course start/end dates" },
        time_zone: { type: "string", description: "Course time zone" },
        syllabus_body: { type: "string", description: "Updated syllabus content" }
      },
      required: ["course_id"]
    }
  },

  // Assignment management
  {
    name: "canvas_list_assignments",
    description: "List assignments for a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        include_submissions: { type: "boolean", description: "Include submission data" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_assignment",
    description: "Get detailed information about a specific assignment",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        assignment_id: { type: "number", description: "ID of the assignment" },
        include_submission: { type: "boolean", description: "Include user's submission data" }
      },
      required: ["course_id", "assignment_id"]
    }
  },
  {
    name: "canvas_create_assignment",
    description: "Create a new assignment in a Canvas course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        name: { type: "string", description: "Name of the assignment" },
        description: { type: "string", description: "Assignment description/instructions" },
        due_at: { type: "string", description: "Due date (ISO format)" },
        points_possible: { type: "number", description: "Maximum points possible" },
        submission_types: { 
          type: "array", 
          items: { type: "string" },
          description: "Allowed submission types"
        },
        allowed_extensions: {
          type: "array",
          items: { type: "string" },
          description: "Allowed file extensions for submissions"
        },
        published: { type: "boolean", description: "Whether the assignment is published" }
      },
      required: ["course_id", "name"]
    }
  },
  {
    name: "canvas_update_assignment",
    description: "Update an existing assignment",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        assignment_id: { type: "number", description: "ID of the assignment to update" },
        name: { type: "string", description: "New name for the assignment" },
        description: { type: "string", description: "New assignment description" },
        due_at: { type: "string", description: "New due date (ISO format)" },
        points_possible: { type: "number", description: "New maximum points" },
        published: { type: "boolean", description: "Whether the assignment is published" }
      },
      required: ["course_id", "assignment_id"]
    }
  },

  // Assignment groups
  {
    name: "canvas_list_assignment_groups",
    description: "List assignment groups for a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },

  // Submissions and grading
  {
    name: "canvas_get_submission",
    description: "Get submission details for an assignment",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        assignment_id: { type: "number", description: "ID of the assignment" },
        user_id: { type: "number", description: "ID of the user (optional, defaults to self)" }
      },
      required: ["course_id", "assignment_id"]
    }
  },
  {
    name: "canvas_submit_assignment",
    description: "Submit work for an assignment",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        assignment_id: { type: "number", description: "ID of the assignment" },
        submission_type: { 
          type: "string", 
          enum: ["online_text_entry", "online_url", "online_upload"],
          description: "Type of submission" 
        },
        body: { type: "string", description: "Text content for text submissions" },
        url: { type: "string", description: "URL for URL submissions" },
        file_ids: { 
          type: "array", 
          items: { type: "number" },
          description: "File IDs for file submissions" 
        }
      },
      required: ["course_id", "assignment_id", "submission_type"]
    }
  },
  {
    name: "canvas_submit_grade",
    description: "Submit a grade for a student's assignment (teacher only)",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        assignment_id: { type: "number", description: "ID of the assignment" },
        user_id: { type: "number", description: "ID of the student" },
        grade: { 
          oneOf: [
            { type: "number" },
            { type: "string" }
          ],
          description: "Grade to submit (number or letter grade)"
        },
        comment: { type: "string", description: "Optional comment on the submission" }
      },
      required: ["course_id", "assignment_id", "user_id", "grade"]
    }
  },

  // Files and uploads
  {
    name: "canvas_list_files",
    description: "List files in a course or folder",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        folder_id: { type: "number", description: "ID of the folder (optional)" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_file",
    description: "Get information about a specific file",
    inputSchema: {
      type: "object",
      properties: {
        file_id: { type: "number", description: "ID of the file" }
      },
      required: ["file_id"]
    }
  },
  {
    name: "canvas_list_folders",
    description: "List folders in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },

  // Pages
  {
    name: "canvas_list_pages",
    description: "List pages in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_page",
    description: "Get content of a specific page",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        page_url: { type: "string", description: "URL slug of the page" }
      },
      required: ["course_id", "page_url"]
    }
  },

  // Calendar and due dates
  {
    name: "canvas_list_calendar_events",
    description: "List calendar events",
    inputSchema: {
      type: "object",
      properties: {
        start_date: { type: "string", description: "Start date (ISO format)" },
        end_date: { type: "string", description: "End date (ISO format)" }
      },
      required: []
    }
  },
  {
    name: "canvas_get_upcoming_assignments",
    description: "Get upcoming assignment due dates",
    inputSchema: {
      type: "object",
      properties: {
        limit: { type: "number", description: "Maximum number of assignments to return" }
      },
      required: []
    }
  },

  // Dashboard
  {
    name: "canvas_get_dashboard",
    description: "Get user's dashboard information",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "canvas_get_dashboard_cards",
    description: "Get dashboard course cards",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },

  // Grades
  {
    name: "canvas_get_course_grades",
    description: "Get grades for a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_user_grades",
    description: "Get all grades for the current user",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },

  // User management
  {
    name: "canvas_get_user_profile",
    description: "Get current user's profile",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "canvas_update_user_profile",
    description: "Update current user's profile",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string", description: "User's name" },
        short_name: { type: "string", description: "User's short name" },
        bio: { type: "string", description: "User's bio" },
        title: { type: "string", description: "User's title" },
        time_zone: { type: "string", description: "User's time zone" }
      },
      required: []
    }
  },
  {
    name: "canvas_enroll_user",
    description: "Enroll a user in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        user_id: { type: "number", description: "ID of the user to enroll" },
        role: { 
          type: "string", 
          description: "Role for the enrollment (StudentEnrollment, TeacherEnrollment, etc.)" 
        },
        enrollment_state: { 
          type: "string",
          description: "State of the enrollment (active, invited, etc.)"
        }
      },
      required: ["course_id", "user_id"]
    }
  },

  // Modules
  {
    name: "canvas_list_modules",
    description: "List all modules in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_module",
    description: "Get details of a specific module",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        module_id: { type: "number", description: "ID of the module" }
      },
      required: ["course_id", "module_id"]
    }
  },
  {
    name: "canvas_list_module_items",
    description: "List all items in a module",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        module_id: { type: "number", description: "ID of the module" }
      },
      required: ["course_id", "module_id"]
    }
  },
  {
    name: "canvas_get_module_item",
    description: "Get details of a specific module item",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        module_id: { type: "number", description: "ID of the module" },
        item_id: { type: "number", description: "ID of the module item" }
      },
      required: ["course_id", "module_id", "item_id"]
    }
  },
  {
    name: "canvas_mark_module_item_complete",
    description: "Mark a module item as complete",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        module_id: { type: "number", description: "ID of the module" },
        item_id: { type: "number", description: "ID of the module item" }
      },
      required: ["course_id", "module_id", "item_id"]
    }
  },

  // Discussions
  {
    name: "canvas_list_discussion_topics",
    description: "List all discussion topics in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_discussion_topic",
    description: "Get details of a specific discussion topic",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        topic_id: { type: "number", description: "ID of the discussion topic" }
      },
      required: ["course_id", "topic_id"]
    }
  },
  {
    name: "canvas_post_to_discussion",
    description: "Post a message to a discussion topic",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        topic_id: { type: "number", description: "ID of the discussion topic" },
        message: { type: "string", description: "Message content" }
      },
      required: ["course_id", "topic_id", "message"]
    }
  },

  // Announcements
  {
    name: "canvas_list_announcements",
    description: "List all announcements in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_create_announcement",
    description: "Create a new announcement in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        title: { type: "string", description: "Title of the announcement" },
        message: { type: "string", description: "Content/message of the announcement" },
        is_announcement: { type: "boolean", description: "Mark as announcement (default: true)" },
        published: { type: "boolean", description: "Whether the announcement is published" },
        delayed_post_at: { type: "string", description: "Delayed posting time (ISO format)" },
        attachment: { type: "object", description: "File attachment for the announcement" }
      },
      required: ["course_id", "title", "message"]
    }
  },

  // Quizzes
  {
    name: "canvas_list_quizzes",
    description: "List all quizzes in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_quiz",
    description: "Get details of a specific quiz",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" }
      },
      required: ["course_id", "quiz_id"]
    }
  },
  {
    name: "canvas_create_quiz",
    description: "Create a new quiz in a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        title: { type: "string", description: "Title of the quiz" },
        quiz_type: { type: "string", description: "Type of the quiz (e.g., graded)" },
        time_limit: { type: "number", description: "Time limit in minutes" },
        published: { type: "boolean", description: "Is the quiz published" },
        description: { type: "string", description: "Description of the quiz" },
        due_at: { type: "string", description: "Due date (ISO format)" }
      },
      required: ["course_id", "title"]
    }
  },
  {
    name: "canvas_start_quiz_attempt",
    description: "Start a new quiz attempt. Returns a quiz_submission object with 'id' field (the quiz_submission_id) and 'validation_token' needed for submitting answers. May return 500 error but still create submission (will auto-retry). Returns 409 if attempt already exists (will return existing).",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" }
      },
      required: ["course_id", "quiz_id"]
    }
  },
  {
    name: "canvas_submit_quiz_answers",
    description: "Submit answers for a quiz attempt. Use the 'id' from canvas_start_quiz_attempt as submission_id, NOT the quiz_id or any other ID.",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" },
        submission_id: { type: "number", description: "The quiz_submission ID from canvas_start_quiz_attempt response (the 'id' field, NOT 'submission_id' field)" },
        validation_token: { type: "string", description: "REQUIRED: Validation token from canvas_start_quiz_attempt response. Without this, you'll get 403 'invalid token' error" },
        answers: {
          type: "array",
          items: {
            type: "object",
            properties: {
              question_id: { type: "number", description: "ID of the question" },
              answer: {
                description: "Answer value - can be string, number, boolean, or array depending on question type"
              },
              answer_id: { type: "number", description: "ID of the answer choice (for multiple choice)" },
              match: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    answer_id: { type: "number" },
                    match_id: { type: "number" }
                  }
                },
                description: "Matching pairs for matching questions"
              }
            },
            required: ["question_id"]
          },
          description: "Array of answers to quiz questions"
        }
      },
      required: ["course_id", "quiz_id", "submission_id", "answers"]
    }
  },
  {
    name: "canvas_list_quiz_questions",
    description: "List all questions in a quiz. Students: First call canvas_start_quiz_attempt to get quiz_submission_id, then use that ID (NOT quiz_id) with use_submission_endpoint=true.",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" },
        quiz_submission_id: { type: "number", description: "For students: The 'id' field from canvas_start_quiz_attempt response (NOT the quiz_id or submission_id field)" },
        quiz_submission_attempt: { type: "number", description: "Optional: The attempt number (required if quiz_submission_id is specified for courses API)" },
        use_submission_endpoint: { type: "boolean", description: "Optional: Use /quiz_submissions/:id/questions endpoint instead of courses API (recommended for students)" }
      },
      required: ["course_id", "quiz_id"]
    }
  },
  {
    name: "canvas_get_quiz_question",
    description: "Get details of a specific quiz question",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" },
        question_id: { type: "number", description: "ID of the question" }
      },
      required: ["course_id", "quiz_id", "question_id"]
    }
  },
  {
    name: "canvas_create_quiz_question",
    description: "Add a new question to a quiz",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" },
        question_name: { type: "string", description: "Name/title of the question" },
        question_text: { type: "string", description: "The question text (HTML supported)" },
        question_type: {
          type: "string",
          enum: [
            "multiple_choice_question",
            "true_false_question",
            "short_answer_question",
            "fill_in_multiple_blanks_question",
            "multiple_answers_question",
            "multiple_dropdowns_question",
            "matching_question",
            "numerical_question",
            "calculated_question",
            "essay_question",
            "file_upload_question",
            "text_only_question"
          ],
          description: "Type of question"
        },
        points_possible: { type: "number", description: "Points for this question" },
        position: { type: "number", description: "Position in the quiz" },
        correct_comments: { type: "string", description: "Comments shown for correct answers" },
        incorrect_comments: { type: "string", description: "Comments shown for incorrect answers" },
        neutral_comments: { type: "string", description: "General comments" },
        answers: {
          type: "array",
          items: {
            type: "object",
            properties: {
              text: { type: "string", description: "Answer text" },
              weight: { type: "number", description: "Weight (100 for correct, 0 for incorrect)" },
              comments: { type: "string", description: "Comments for this answer" }
            }
          },
          description: "Array of answer choices"
        }
      },
      required: ["course_id", "quiz_id", "question_name", "question_text", "question_type", "points_possible"]
    }
  },
  {
    name: "canvas_update_quiz_question",
    description: "Update an existing quiz question",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" },
        question_id: { type: "number", description: "ID of the question to update" },
        question_name: { type: "string", description: "New name/title of the question" },
        question_text: { type: "string", description: "New question text" },
        points_possible: { type: "number", description: "New points value" },
        correct_comments: { type: "string", description: "New comments for correct answers" },
        incorrect_comments: { type: "string", description: "New comments for incorrect answers" },
        answers: {
          type: "array",
          items: {
            type: "object",
            properties: {
              text: { type: "string" },
              weight: { type: "number" },
              comments: { type: "string" }
            }
          },
          description: "Updated answer choices"
        }
      },
      required: ["course_id", "quiz_id", "question_id"]
    }
  },
  {
    name: "canvas_delete_quiz_question",
    description: "Delete a question from a quiz",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz" },
        question_id: { type: "number", description: "ID of the question to delete" }
      },
      required: ["course_id", "quiz_id", "question_id"]
    }
  },
  {
    name: "canvas_upload_file_from_path",
    description: "Upload a file from local filesystem to Canvas",
    inputSchema: {
      type: "object",
      properties: {
        file_path: { type: "string", description: "Absolute path to the local file" },
        course_id: { type: "number", description: "ID of the course (optional)" },
        folder_id: { type: "number", description: "ID of the folder to upload to (optional)" }
      },
      required: ["file_path"]
    }
  },
  {
    name: "canvas_submit_assignment_with_file",
    description: "Submit an assignment with a local file upload",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        assignment_id: { type: "number", description: "ID of the assignment" },
        file_path: { type: "string", description: "Absolute path to the file to submit" },
        comment: { type: "string", description: "Optional submission comment" }
      },
      required: ["course_id", "assignment_id", "file_path"]
    }
  },

  // Rubrics
  {
    name: "canvas_list_rubrics",
    description: "List rubrics for a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_get_rubric",
    description: "Get details of a specific rubric",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        rubric_id: { type: "number", description: "ID of the rubric" }
      },
      required: ["course_id", "rubric_id"]
    }
  },

  // Conversations
  {
    name: "canvas_list_conversations",
    description: "List user's conversations",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "canvas_get_conversation",
    description: "Get details of a specific conversation",
    inputSchema: {
      type: "object",
      properties: {
        conversation_id: { type: "number", description: "ID of the conversation" }
      },
      required: ["conversation_id"]
    }
  },
  {
    name: "canvas_create_conversation",
    description: "Create a new conversation",
    inputSchema: {
      type: "object",
      properties: {
        recipients: { 
          type: "array", 
          items: { type: "string" },
          description: "Recipient user IDs or email addresses" 
        },
        body: { type: "string", description: "Message body" },
        subject: { type: "string", description: "Message subject" }
      },
      required: ["recipients", "body"]
    }
  },

  // Notifications
  {
    name: "canvas_list_notifications",
    description: "List user's notifications",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },

  // Syllabus
  {
    name: "canvas_get_syllabus",
    description: "Get course syllabus",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" }
      },
      required: ["course_id"]
    }
  },

  // Delete Operations
  {
    name: "canvas_delete_course",
    description: "Delete or conclude a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course to delete" },
        event: { 
          type: "string", 
          enum: ["delete", "conclude"], 
          description: "Action to take: 'delete' removes the course entirely, 'conclude' makes it read-only",
          default: "delete"
        }
      },
      required: ["course_id"]
    }
  },
  {
    name: "canvas_delete_assignment",
    description: "Delete an assignment",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        assignment_id: { type: "number", description: "ID of the assignment to delete" }
      },
      required: ["course_id", "assignment_id"]
    }
  },
  {
    name: "canvas_delete_announcement",
    description: "Delete an announcement",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        announcement_id: { type: "number", description: "ID of the announcement to delete" }
      },
      required: ["course_id", "announcement_id"]
    }
  },
  {
    name: "canvas_delete_quiz",
    description: "Delete a quiz",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        quiz_id: { type: "number", description: "ID of the quiz to delete" }
      },
      required: ["course_id", "quiz_id"]
    }
  },
  {
    name: "canvas_delete_conversation",
    description: "Delete a conversation",
    inputSchema: {
      type: "object",
      properties: {
        conversation_id: { type: "number", description: "ID of the conversation to delete" }
      },
      required: ["conversation_id"]
    }
  },
  {
    name: "canvas_unenroll_user",
    description: "Unenroll a user from a course",
    inputSchema: {
      type: "object",
      properties: {
        course_id: { type: "number", description: "ID of the course" },
        enrollment_id: { type: "number", description: "ID of the enrollment to remove" }
      },
      required: ["course_id", "enrollment_id"]
    }
  },

  // Account Management
  {
    name: "canvas_get_account",
    description: "Get account details",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "ID of the account" }
      },
      required: ["account_id"]
    }
  },
  {
    name: "canvas_list_account_courses",
    description: "List courses for an account",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "ID of the account" },
        with_enrollments: { type: "boolean", description: "Include enrollment data" },
        published: { type: "boolean", description: "Only include published courses" },
        completed: { type: "boolean", description: "Include completed courses" },
        search_term: { type: "string", description: "Search term to filter courses" },
        sort: { type: "string", enum: ["course_name", "sis_course_id", "teacher", "account_name"], description: "Sort order" },
        order: { type: "string", enum: ["asc", "desc"], description: "Sort direction" }
      },
      required: ["account_id"]
    }
  },
  {
    name: "canvas_list_account_users",
    description: "List users for an account with pagination support and session management. Returns up to 20 users per page. Use session_id to continue previous search or provide new parameters to start fresh.",
    inputSchema: {
      type: "object",
      properties: {
        session_id: { type: "string", description: "Session ID to continue previous search (when provided, other parameters except 'page' are ignored)" },
        account_id: { type: "number", description: "ID of the account (required for new sessions)" },
        search_term: { type: "string", description: "Search term to filter users" },
        sort: { type: "string", enum: ["username", "email", "sis_id", "last_login"], description: "Sort order" },
        order: { type: "string", enum: ["asc", "desc"], description: "Sort direction" },
        page: { type: "number", description: "Page number (starts from 1, default: 1)", default: 1 },
        per_page: { type: "number", description: "Number of users per page (max: 20, default: 20)", default: 20 }
      },
      // anyOf: [
      //   { required: ["session_id"] },
      //   { required: ["account_id"] }
      // ]
      required: []
    }
  },
  {
    name: "canvas_create_user",
    description: "Create a new user in an account",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "ID of the account" },
        user: {
          type: "object",
          properties: {
            name: { type: "string", description: "Full name of the user" },
            short_name: { type: "string", description: "Short name of the user" },
            sortable_name: { type: "string", description: "Sortable name (Last, First)" },
            time_zone: { type: "string", description: "User's time zone" }
          },
          required: ["name"]
        },
        pseudonym: {
          type: "object",
          properties: {
            unique_id: { type: "string", description: "Unique login ID (email or username)" },
            password: { type: "string", description: "User's password" },
            sis_user_id: { type: "string", description: "SIS ID for the user" },
            send_confirmation: { type: "boolean", description: "Send confirmation email" }
          },
          required: ["unique_id"]
        }
      },
      required: ["account_id", "user", "pseudonym"]
    }
  },
  {
    name: "canvas_list_sub_accounts",
    description: "List sub-accounts for an account",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "ID of the parent account" }
      },
      required: ["account_id"]
    }
  },
  {
    name: "canvas_get_account_reports",
    description: "List available reports for an account",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "ID of the account" }
      },
      required: ["account_id"]
    }
  },
  {
    name: "canvas_create_account_report",
    description: "Generate a report for an account",
    inputSchema: {
      type: "object",
      properties: {
        account_id: { type: "number", description: "ID of the account" },
        report: { type: "string", description: "Type of report to generate" },
        parameters: { type: "object", description: "Report parameters" }
      },
      required: ["account_id", "report"]
    }
  }
];

class CanvasMCPServer {
  private server: Server;
  private client: CanvasClient;
  private config: MCPServerConfig;

  constructor(config: MCPServerConfig) {
    this.config = config;
    this.client = new CanvasClient(
      config.canvas.token, 
      config.canvas.domain,
      {
        maxRetries: config.canvas.maxRetries,
        retryDelay: config.canvas.retryDelay
      }
    );

    this.server = new Server(
      {
        name: config.name,
        version: config.version
      },
      {
        capabilities: {
          resources: {},
          tools: {}
        }
      }
    );

    this.setupHandlers();
    this.setupErrorHandling();
  }

  private setupErrorHandling(): void {
    this.server.onerror = (error: Error) => {
      console.error(`[${this.config.name} Error]`, error);
    };

    process.on('SIGINT', async () => {
      console.log('\nReceived SIGINT, shutting down gracefully...');
      await this.server.close();
      process.exit(0);
    });

    process.on('SIGTERM', async () => {
      console.log('\nReceived SIGTERM, shutting down gracefully...');
      await this.server.close();
      process.exit(0);
    });

    process.on('uncaughtException', (error) => {
      console.error('Uncaught Exception:', error);
      process.exit(1);
    });

    process.on('unhandledRejection', (reason, promise) => {
      console.error('Unhandled Rejection at:', promise, 'reason:', reason);
      process.exit(1);
    });
  }

  private setupHandlers(): void {
    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      try {
        const courses = await this.client.listCourses();
        
        return {
          resources: [
            {
              uri: "canvas://health",
              name: "Canvas Health Status",
              description: "Health check and API connectivity status",
              mimeType: "application/json"
            },
            {
              uri: "courses://list",
              name: "All Courses",
              description: "List of all available Canvas courses",
              mimeType: "application/json"
            },
            ...courses.map((course: CanvasCourse) => ({
              uri: `course://${course.id}`,
              name: `Course: ${course.name}`,
              description: `${course.course_code} - ${course.name}`,
              mimeType: "application/json"
            })),
            ...courses.map((course: CanvasCourse) => ({
              uri: `assignments://${course.id}`,
              name: `Assignments: ${course.name}`,
              description: `Assignments for ${course.name}`,
              mimeType: "application/json"
            })),
            ...courses.map((course: CanvasCourse) => ({
              uri: `modules://${course.id}`,
              name: `Modules: ${course.name}`,
              description: `Modules for ${course.name}`,
              mimeType: "application/json"
            })),
            ...courses.map((course: CanvasCourse) => ({
              uri: `discussions://${course.id}`,
              name: `Discussions: ${course.name}`,
              description: `Discussion topics for ${course.name}`,
              mimeType: "application/json"
            })),
            ...courses.map((course: CanvasCourse) => ({
              uri: `announcements://${course.id}`,
              name: `Announcements: ${course.name}`,
              description: `Announcements for ${course.name}`,
              mimeType: "application/json"
            })),
            ...courses.map((course: CanvasCourse) => ({
              uri: `quizzes://${course.id}`,
              name: `Quizzes: ${course.name}`,
              description: `Quizzes for ${course.name}`,
              mimeType: "application/json"
            })),
            ...courses.map((course: CanvasCourse) => ({
              uri: `pages://${course.id}`,
              name: `Pages: ${course.name}`,
              description: `Pages for ${course.name}`,
              mimeType: "application/json"
            })),
            ...courses.map((course: CanvasCourse) => ({
              uri: `files://${course.id}`,
              name: `Files: ${course.name}`,
              description: `Files for ${course.name}`,
              mimeType: "application/json"
            })),
            {
              uri: "dashboard://user",
              name: "User Dashboard",
              description: "User's Canvas dashboard information",
              mimeType: "application/json"
            },
            {
              uri: "profile://user",
              name: "User Profile",
              description: "Current user's profile information",
              mimeType: "application/json"
            },
            {
              uri: "calendar://upcoming",
              name: "Upcoming Events",
              description: "Upcoming assignments and events",
              mimeType: "application/json"
            }
          ]
        };
      } catch (error) {
        console.error('Error listing resources:', error);
        return { resources: [] };
      }
    });

    // Read resource content
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request: any) => {
      const uri = request.params.uri;
      const [type, id] = uri.split("://");
      
      try {
        let content;
        
        switch (type) {
          case "canvas":
            if (id === "health") {
              content = await this.client.healthCheck();
            }
            break;
            
          case "courses":
            content = await this.client.listCourses();
            break;
            
          case "course":
            content = await this.client.getCourse(parseInt(id));
            break;
          
          case "assignments":
            content = await this.client.listAssignments(parseInt(id), true);
            break;
          
          case "modules":
            content = await this.client.listModules(parseInt(id));
            break;

          case "discussions":
            content = await this.client.listDiscussionTopics(parseInt(id));
            break;

          case "announcements":
            content = await this.client.listAnnouncements(id);
            break;
          
          case "quizzes":
            content = await this.client.listQuizzes(id);
            break;

          case "pages":
            content = await this.client.listPages(parseInt(id));
            break;

          case "files":
            content = await this.client.listFiles(parseInt(id));
            break;

          case "dashboard":
            if (id === "user") {
              content = await this.client.getDashboard();
            }
            break;

          case "profile":
            if (id === "user") {
              content = await this.client.getUserProfile();
            }
            break;

          case "calendar":
            if (id === "upcoming") {
              content = await this.client.getUpcomingAssignments();
            }
            break;
          
          default:
            throw new Error(`Unknown resource type: ${type}`);
        }

        return {
          contents: [{
            uri: request.params.uri,
            mimeType: "application/json",
            text: JSON.stringify(content, null, 2)
          }]
        };
      } catch (error) {
        console.error(`Error reading resource ${uri}:`, error);
        return {
          contents: [{
            uri: request.params.uri,
            mimeType: "application/json",
            text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2)
          }]
        };
      }
    });

    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: TOOLS
    }));

    // Handle tool calls with comprehensive error handling
    this.server.setRequestHandler(CallToolRequestSchema, async (request: any) => {
      try {
        const args = request.params.arguments || {};
        const toolName = request.params.name;
        
        console.error(`[Canvas MCP] Executing tool: ${toolName}`);
        
        switch (toolName) {
          // Health check
          case "canvas_health_check": {
            const health = await this.client.healthCheck();
            return {
              content: [{ type: "text", text: JSON.stringify(health, null, 2) }]
            };
          }

          // Course management
          case "canvas_list_courses": {
            const { include_ended = false } = args as { include_ended?: boolean };
            const courses = await this.client.listCourses(include_ended);
            return {
              content: [{ type: "text", text: JSON.stringify(courses, null, 2) }]
            };
          }

          case "canvas_get_course": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const course = await this.client.getCourse(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(course, null, 2) }]
            };
          }
          
          case "canvas_create_course": {
            const courseArgs = args as unknown as CreateCourseArgs;
            if (!courseArgs.account_id || !courseArgs.name) {
              throw new Error("Missing required fields: account_id and name");
            }
            const course = await this.client.createCourse(courseArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(course, null, 2) }]
            };
          }
          
          case "canvas_update_course": {
            const updateArgs = args as unknown as UpdateCourseArgs;
            if (!updateArgs.course_id) {
              throw new Error("Missing required field: course_id");
            }
            const updatedCourse = await this.client.updateCourse(updateArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(updatedCourse, null, 2) }]
            };
          }

          // Assignment management
          case "canvas_list_assignments": {
            const { course_id, include_submissions = false } = args as { 
              course_id: number; 
              include_submissions?: boolean 
            };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const assignments = await this.client.listAssignments(course_id, include_submissions);
            return {
              content: [{ type: "text", text: JSON.stringify(assignments, null, 2) }]
            };
          }

          case "canvas_get_assignment": {
            const { course_id, assignment_id, include_submission = false } = args as { 
              course_id: number; 
              assignment_id: number;
              include_submission?: boolean;
            };
            if (!course_id || !assignment_id) {
              throw new Error("Missing required fields: course_id and assignment_id");
            }
            
            const assignment = await this.client.getAssignment(course_id, assignment_id, include_submission);
            return {
              content: [{ type: "text", text: JSON.stringify(assignment, null, 2) }]
            };
          }
          
          case "canvas_create_assignment": {
            const assignmentArgs = args as unknown as CreateAssignmentArgs;
            if (!assignmentArgs.course_id || !assignmentArgs.name) {
              throw new Error("Missing required fields: course_id and name");
            }
            const assignment = await this.client.createAssignment(assignmentArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(assignment, null, 2) }]
            };
          }
          
          case "canvas_update_assignment": {
            const updateAssignmentArgs = args as unknown as UpdateAssignmentArgs;
            if (!updateAssignmentArgs.course_id || !updateAssignmentArgs.assignment_id) {
              throw new Error("Missing required fields: course_id and assignment_id");
            }
            const updatedAssignment = await this.client.updateAssignment(updateAssignmentArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(updatedAssignment, null, 2) }]
            };
          }

          case "canvas_list_assignment_groups": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const groups = await this.client.listAssignmentGroups(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(groups, null, 2) }]
            };
          }

          // Submissions
          case "canvas_get_submission": {
            const { course_id, assignment_id, user_id } = args as { 
              course_id: number; 
              assignment_id: number;
              user_id?: number;
            };
            if (!course_id || !assignment_id) {
              throw new Error("Missing required fields: course_id and assignment_id");
            }
            
            const submission = await this.client.getSubmission(course_id, assignment_id, user_id || 'self');
            return {
              content: [{ type: "text", text: JSON.stringify(submission, null, 2) }]
            };
          }

          case "canvas_submit_assignment": {
            const submitArgs = args as unknown as SubmitAssignmentArgs;
            const { course_id, assignment_id, submission_type } = submitArgs;

            if (!course_id || !assignment_id || !submission_type) {
              throw new Error("Missing required fields: course_id, assignment_id, and submission_type");
            }

            const submission = await this.client.submitAssignment(submitArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(submission, null, 2) }]
            };
          }
          
          case "canvas_submit_grade": {
            const gradeArgs = args as unknown as SubmitGradeArgs;
            if (!gradeArgs.course_id || !gradeArgs.assignment_id || 
                !gradeArgs.user_id || gradeArgs.grade === undefined) {
              throw new Error("Missing required fields for grade submission");
            }
            const submission = await this.client.submitGrade(gradeArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(submission, null, 2) }]
            };
          }

          // Files
          case "canvas_list_files": {
            const { course_id, folder_id } = args as { course_id: number; folder_id?: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const files = await this.client.listFiles(course_id, folder_id);
            return {
              content: [{ type: "text", text: JSON.stringify(files, null, 2) }]
            };
          }

          case "canvas_get_file": {
            const { file_id } = args as { file_id: number };
            if (!file_id) throw new Error("Missing required field: file_id");
            
            const file = await this.client.getFile(file_id);
            return {
              content: [{ type: "text", text: JSON.stringify(file, null, 2) }]
            };
          }

          case "canvas_list_folders": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const folders = await this.client.listFolders(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(folders, null, 2) }]
            };
          }

          // Pages
          case "canvas_list_pages": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const pages = await this.client.listPages(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(pages, null, 2) }]
            };
          }

          case "canvas_get_page": {
            const { course_id, page_url } = args as { course_id: number; page_url: string };
            if (!course_id || !page_url) {
              throw new Error("Missing required fields: course_id and page_url");
            }
            
            const page = await this.client.getPage(course_id, page_url);
            return {
              content: [{ type: "text", text: JSON.stringify(page, null, 2) }]
            };
          }

          // Calendar
          case "canvas_list_calendar_events": {
            const { start_date, end_date } = args as { start_date?: string; end_date?: string };
            const events = await this.client.listCalendarEvents(start_date, end_date);
            return {
              content: [{ type: "text", text: JSON.stringify(events, null, 2) }]
            };
          }

          case "canvas_get_upcoming_assignments": {
            const { limit = 10 } = args as { limit?: number };
            const assignments = await this.client.getUpcomingAssignments(limit);
            return {
              content: [{ type: "text", text: JSON.stringify(assignments, null, 2) }]
            };
          }

          // Dashboard
          case "canvas_get_dashboard": {
            const dashboard = await this.client.getDashboard();
            return {
              content: [{ type: "text", text: JSON.stringify(dashboard, null, 2) }]
            };
          }

          case "canvas_get_dashboard_cards": {
            const cards = await this.client.getDashboardCards();
            return {
              content: [{ type: "text", text: JSON.stringify(cards, null, 2) }]
            };
          }

          // User management
          case "canvas_get_user_profile": {
            const profile = await this.client.getUserProfile();
            return {
              content: [{ type: "text", text: JSON.stringify(profile, null, 2) }]
            };
          }

          case "canvas_update_user_profile": {
            const profileData = args as Partial<{ name: string; short_name: string; bio: string; title: string; time_zone: string }>;
            const updatedProfile = await this.client.updateUserProfile(profileData);
            return {
              content: [{ type: "text", text: JSON.stringify(updatedProfile, null, 2) }]
            };
          }

          case "canvas_enroll_user": {
            const enrollArgs = args as unknown as EnrollUserArgs;
            if (!enrollArgs.course_id || !enrollArgs.user_id) {
              throw new Error("Missing required fields: course_id and user_id");
            }
            const enrollment = await this.client.enrollUser(enrollArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(enrollment, null, 2) }]
            };
          }

          // Grades
          case "canvas_get_course_grades": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const grades = await this.client.getCourseGrades(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(grades, null, 2) }]
            };
          }

          case "canvas_get_user_grades": {
            const grades = await this.client.getUserGrades();
            return {
              content: [{ type: "text", text: JSON.stringify(grades, null, 2) }]
            };
          }

          // Continue with all other tools...
          // [I'll include the rest in the same pattern]
          
          // Account Management
          case "canvas_get_account": {
            const { account_id } = args as { account_id: number };
            if (!account_id) throw new Error("Missing required field: account_id");
            
            const account = await this.client.getAccount(account_id);
            return {
              content: [{ type: "text", text: JSON.stringify(account, null, 2) }]
            };
          }

          case "canvas_list_account_courses": {
            const accountCoursesArgs = args as unknown as ListAccountCoursesArgs;
            if (!accountCoursesArgs.account_id) {
              throw new Error("Missing required field: account_id");
            }
            
            const courses = await this.client.listAccountCourses(accountCoursesArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(courses, null, 2) }]
            };
          }

          case "canvas_list_account_users": {
            const accountUsersArgs = args as unknown as ListAccountUsersArgs;
            let sessionId: string;
            let queryParams: {
              account_id: number;
              search_term?: string;
              sort?: 'username' | 'email' | 'sis_id' | 'last_login';
              order?: 'asc' | 'desc';
              page: number;
              per_page: number;
            };

            if (accountUsersArgs.session_id) {
              // Use existing session
              const session = sessionManager.getSession(accountUsersArgs.session_id);
              if (!session) {
                throw new Error(`Session ${accountUsersArgs.session_id} not found or expired. Please start a new search.`);
              }
              
              sessionId = accountUsersArgs.session_id;
              queryParams = {
                account_id: session.account_id,
                search_term: session.search_term,
                sort: session.sort,
                order: session.order,
                page: accountUsersArgs.page || session.current_page,
                per_page: session.per_page
              };
              
              // Update session with new page
              sessionManager.updateSession(sessionId, { current_page: queryParams.page });
            } else {
              // Create new session
              if (!accountUsersArgs.account_id) {
                throw new Error("Missing required field: account_id (required for new sessions)");
              }
              
              queryParams = {
                account_id: accountUsersArgs.account_id,
                search_term: accountUsersArgs.search_term,
                sort: accountUsersArgs.sort,
                order: accountUsersArgs.order,
                page: accountUsersArgs.page || 1,
                per_page: Math.min(accountUsersArgs.per_page || 20, 20)
              };
              
              sessionId = sessionManager.createSession({
                account_id: queryParams.account_id,
                search_term: queryParams.search_term,
                sort: queryParams.sort,
                order: queryParams.order,
                per_page: queryParams.per_page,
                current_page: queryParams.page
              });
            }
            
            const result = await this.client.listAccountUsers(queryParams);
            const { users, pagination } = result;
            
            // Create response with session and pagination info
            let responseText = `Users (Page ${pagination?.current_page || queryParams.page}):\n\n`;
            responseText += JSON.stringify(users, null, 2);
            
            // Add session and pagination navigation info
            responseText += "\n\n=== Session & Pagination Info ===\n";
            responseText += `Session ID: ${sessionId}\n`;
            responseText += `Current page: ${pagination?.current_page || queryParams.page}\n`;
            
            if (pagination?.total_pages) {
              responseText += `Total pages: ${pagination.total_pages}\n`;
            }
            
            if (pagination?.prev_page) {
              responseText += `Previous page: Use {"session_id": "${sessionId}", "page": ${pagination.prev_page}}\n`;
            }
            
            if (pagination?.next_page) {
              responseText += `Next page: Use {"session_id": "${sessionId}", "page": ${pagination.next_page}}\n`;
            }
            
            responseText += "\n📝 Session Usage:\n";
            responseText += `• Continue browsing: Use session_id "${sessionId}" with different page numbers\n`;
            responseText += `• New search: Omit session_id and provide account_id with new parameters\n`;
            responseText += `• Sessions expire after 30 minutes of inactivity`;
            
            return {
              content: [{ type: "text", text: responseText }]
            };
          }

          case "canvas_create_user": {
            const createUserArgs = args as unknown as CreateUserArgs;
            if (!createUserArgs.account_id || !createUserArgs.user || !createUserArgs.pseudonym) {
              throw new Error("Missing required fields: account_id, user, and pseudonym");
            }
            
            const user = await this.client.createUser(createUserArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(user, null, 2) }]
            };
          }

          case "canvas_list_sub_accounts": {
            const { account_id } = args as { account_id: number };
            if (!account_id) throw new Error("Missing required field: account_id");
            
            const subAccounts = await this.client.listSubAccounts(account_id);
            return {
              content: [{ type: "text", text: JSON.stringify(subAccounts, null, 2) }]
            };
          }

          case "canvas_get_account_reports": {
            const { account_id } = args as { account_id: number };
            if (!account_id) throw new Error("Missing required field: account_id");
            
            const reports = await this.client.getAccountReports(account_id);
            return {
              content: [{ type: "text", text: JSON.stringify(reports, null, 2) }]
            };
          }

          case "canvas_create_account_report": {
            const createReportArgs = args as unknown as CreateReportArgs;
            if (!createReportArgs.account_id || !createReportArgs.report) {
              throw new Error("Missing required fields: account_id and report");
            }
            
            const report = await this.client.createAccountReport(createReportArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(report, null, 2) }]
            };
          }

          // Modules
          case "canvas_list_modules": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const modules = await this.client.listModules(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(modules, null, 2) }]
            };
          }

          case "canvas_get_module": {
            const { course_id, module_id } = args as { course_id: number; module_id: number };
            if (!course_id || !module_id) {
              throw new Error("Missing required fields: course_id and module_id");
            }
            
            const module = await this.client.getModule(course_id, module_id);
            return {
              content: [{ type: "text", text: JSON.stringify(module, null, 2) }]
            };
          }

          case "canvas_list_module_items": {
            const { course_id, module_id } = args as { course_id: number; module_id: number };
            if (!course_id || !module_id) {
              throw new Error("Missing required fields: course_id and module_id");
            }
            
            const items = await this.client.listModuleItems(course_id, module_id);
            return {
              content: [{ type: "text", text: JSON.stringify(items, null, 2) }]
            };
          }

          case "canvas_get_module_item": {
            const { course_id, module_id, item_id } = args as { 
              course_id: number; 
              module_id: number; 
              item_id: number 
            };
            if (!course_id || !module_id || !item_id) {
              throw new Error("Missing required fields: course_id, module_id, and item_id");
            }
            
            const item = await this.client.getModuleItem(course_id, module_id, item_id);
            return {
              content: [{ type: "text", text: JSON.stringify(item, null, 2) }]
            };
          }

          case "canvas_mark_module_item_complete": {
            const { course_id, module_id, item_id } = args as { 
              course_id: number; 
              module_id: number; 
              item_id: number 
            };
            if (!course_id || !module_id || !item_id) {
              throw new Error("Missing required fields: course_id, module_id, and item_id");
            }
            
            const result = await this.client.markModuleItemComplete(course_id, module_id, item_id);
            return {
              content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
            };
          }

          // Discussions
          case "canvas_list_discussion_topics": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const topics = await this.client.listDiscussionTopics(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(topics, null, 2) }]
            };
          }

          case "canvas_get_discussion_topic": {
            const { course_id, topic_id } = args as { course_id: number; topic_id: number };
            if (!course_id || !topic_id) {
              throw new Error("Missing required fields: course_id and topic_id");
            }
            
            const topic = await this.client.getDiscussionTopic(course_id, topic_id);
            return {
              content: [{ type: "text", text: JSON.stringify(topic, null, 2) }]
            };
          }

          case "canvas_post_to_discussion": {
            const { course_id, topic_id, message } = args as { 
              course_id: number; 
              topic_id: number; 
              message: string 
            };
            if (!course_id || !topic_id || !message) {
              throw new Error("Missing required fields: course_id, topic_id, and message");
            }
            
            const post = await this.client.postToDiscussion(course_id, topic_id, message);
            return {
              content: [{ type: "text", text: JSON.stringify(post, null, 2) }]
            };
          }

          // Announcements
          case "canvas_list_announcements": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const announcements = await this.client.listAnnouncements(course_id.toString());
            return {
              content: [{ type: "text", text: JSON.stringify(announcements, null, 2) }]
            };
          }

          case "canvas_create_announcement": {
            const { course_id, title, message, is_announcement, published, delayed_post_at, attachment } = args as {
              course_id: number;
              title: string;
              message: string;
              is_announcement?: boolean;
              published?: boolean;
              delayed_post_at?: string;
              attachment?: any;
            };
            if (!course_id || !title || !message) {
              throw new Error("Missing required fields: course_id, title, and message");
            }
            
            const announcement = await this.client.createAnnouncement(course_id, {
              title,
              message,
              is_announcement,
              published,
              delayed_post_at,
              attachment
            });
            return {
              content: [{ type: "text", text: JSON.stringify(announcement, null, 2) }]
            };
          }

          // Quizzes
          case "canvas_list_quizzes": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const quizzes = await this.client.listQuizzes(course_id.toString());
            return {
              content: [{ type: "text", text: JSON.stringify(quizzes, null, 2) }]
            };
          }

          case "canvas_get_quiz": {
            const { course_id, quiz_id } = args as { course_id: number; quiz_id: number };
            if (!course_id || !quiz_id) {
              throw new Error("Missing required fields: course_id and quiz_id");
            }
            
            const quiz = await this.client.getQuiz(course_id.toString(), quiz_id);
            return {
              content: [{ type: "text", text: JSON.stringify(quiz, null, 2) }]
            };
          }

          case "canvas_create_quiz": {
            const { course_id, title, quiz_type, time_limit, published, description, due_at } = args as {
              course_id: number;
              title: string;
              quiz_type?: 'practice_quiz' | 'assignment' | 'graded_survey' | 'survey';
              time_limit?: number;
              published?: boolean;
              description?: string;
              due_at?: string;
            };
            if (!course_id || !title) {
              throw new Error("Missing required fields: course_id and title");
            }
            
            const quiz = await this.client.createQuiz(course_id, {
              title,
              quiz_type,
              time_limit,
              published,
              description,
              due_at
            });
            return {
              content: [{ type: "text", text: JSON.stringify(quiz, null, 2) }]
            };
          }

          case "canvas_start_quiz_attempt": {
            const { course_id, quiz_id } = args as { course_id: number; quiz_id: number };
            if (!course_id || !quiz_id) {
              throw new Error("Missing required fields: course_id and quiz_id");
            }

            const attempt = await this.client.startQuizAttempt(course_id, quiz_id);
            return {
              content: [{ type: "text", text: JSON.stringify(attempt, null, 2) }]
            };
          }

          case "canvas_submit_quiz_answers": {
            const { course_id, quiz_id, submission_id, answers, validation_token } = args as {
              course_id: number;
              quiz_id: number;
              submission_id: number;
              answers: any[];
              validation_token?: string;
            };
            if (!course_id || !quiz_id || !submission_id || !answers) {
              throw new Error("Missing required fields: course_id, quiz_id, submission_id, and answers");
            }

            const result = await this.client.submitQuizAttempt(course_id, quiz_id, submission_id, answers, validation_token);
            return {
              content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
            };
          }

          case "canvas_list_quiz_questions": {
            const { course_id, quiz_id, quiz_submission_id, quiz_submission_attempt, use_submission_endpoint } = args as {
              course_id: number;
              quiz_id: number;
              quiz_submission_id?: number;
              quiz_submission_attempt?: number;
              use_submission_endpoint?: boolean;
            };
            if (!course_id || !quiz_id) {
              throw new Error("Missing required fields: course_id and quiz_id");
            }

            const options: any = {};
            if (quiz_submission_id) {
              options.quiz_submission_id = quiz_submission_id;
            }
            if (quiz_submission_attempt) {
              options.quiz_submission_attempt = quiz_submission_attempt;
            }
            if (use_submission_endpoint) {
              options.use_submission_endpoint = use_submission_endpoint;
            }

            const questions = await this.client.listQuizQuestions(course_id, quiz_id, Object.keys(options).length > 0 ? options : undefined);
            return {
              content: [{ type: "text", text: JSON.stringify(questions, null, 2) }]
            };
          }

          case "canvas_get_quiz_question": {
            const { course_id, quiz_id, question_id } = args as {
              course_id: number;
              quiz_id: number;
              question_id: number;
            };
            if (!course_id || !quiz_id || !question_id) {
              throw new Error("Missing required fields: course_id, quiz_id, and question_id");
            }

            const question = await this.client.getQuizQuestion(course_id, quiz_id, question_id);
            return {
              content: [{ type: "text", text: JSON.stringify(question, null, 2) }]
            };
          }

          case "canvas_create_quiz_question": {
            const { course_id, quiz_id, ...questionData } = args as any;
            if (!course_id || !quiz_id || !questionData.question_name || !questionData.question_text || !questionData.question_type || questionData.points_possible === undefined) {
              throw new Error("Missing required fields: course_id, quiz_id, question_name, question_text, question_type, and points_possible");
            }

            const question = await this.client.createQuizQuestion(course_id, quiz_id, questionData);
            return {
              content: [{ type: "text", text: JSON.stringify(question, null, 2) }]
            };
          }

          case "canvas_update_quiz_question": {
            const { course_id, quiz_id, question_id, ...updateData } = args as any;
            if (!course_id || !quiz_id || !question_id) {
              throw new Error("Missing required fields: course_id, quiz_id, and question_id");
            }

            const question = await this.client.updateQuizQuestion(course_id, quiz_id, question_id, updateData);
            return {
              content: [{ type: "text", text: JSON.stringify(question, null, 2) }]
            };
          }

          case "canvas_delete_quiz_question": {
            const { course_id, quiz_id, question_id } = args as {
              course_id: number;
              quiz_id: number;
              question_id: number;
            };
            if (!course_id || !quiz_id || !question_id) {
              throw new Error("Missing required fields: course_id, quiz_id, and question_id");
            }

            await this.client.deleteQuizQuestion(course_id, quiz_id, question_id);
            return {
              content: [{ type: "text", text: "Quiz question deleted successfully" }]
            };
          }

          case "canvas_upload_file_from_path": {
            const { file_path, course_id, folder_id } = args as {
              file_path: string;
              course_id?: number;
              folder_id?: number;
            };
            if (!file_path) {
              throw new Error("Missing required field: file_path");
            }

            const file = await this.client.uploadFileFromPath(file_path, course_id, folder_id);
            return {
              content: [{ type: "text", text: JSON.stringify(file, null, 2) }]
            };
          }

          case "canvas_submit_assignment_with_file": {
            const { course_id, assignment_id, file_path, comment } = args as {
              course_id: number;
              assignment_id: number;
              file_path: string;
              comment?: string;
            };
            if (!course_id || !assignment_id || !file_path) {
              throw new Error("Missing required fields: course_id, assignment_id, and file_path");
            }

            // First upload the file
            const file = await this.client.uploadFileFromPath(file_path, course_id);

            // Then submit the assignment with the uploaded file
            const submissionArgs: SubmitAssignmentArgs = {
              course_id,
              assignment_id,
              submission_type: "online_upload",
              file_ids: [file.id]
            };

            if (comment) {
              (submissionArgs as any).comment = { text_comment: comment };
            }

            const submission = await this.client.submitAssignment(submissionArgs);
            return {
              content: [{ type: "text", text: JSON.stringify(submission, null, 2) }]
            };
          }

          // Rubrics
          case "canvas_list_rubrics": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const rubrics = await this.client.listRubrics(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(rubrics, null, 2) }]
            };
          }

          case "canvas_get_rubric": {
            const { course_id, rubric_id } = args as { course_id: number; rubric_id: number };
            if (!course_id || !rubric_id) {
              throw new Error("Missing required fields: course_id and rubric_id");
            }
            
            const rubric = await this.client.getRubric(course_id, rubric_id);
            return {
              content: [{ type: "text", text: JSON.stringify(rubric, null, 2) }]
            };
          }

          // Conversations
          case "canvas_list_conversations": {
            const conversations = await this.client.listConversations();
            return {
              content: [{ type: "text", text: JSON.stringify(conversations, null, 2) }]
            };
          }

          case "canvas_get_conversation": {
            const { conversation_id } = args as { conversation_id: number };
            if (!conversation_id) throw new Error("Missing required field: conversation_id");
            
            const conversation = await this.client.getConversation(conversation_id);
            return {
              content: [{ type: "text", text: JSON.stringify(conversation, null, 2) }]
            };
          }

          case "canvas_create_conversation": {
            const { recipients, body, subject } = args as { 
              recipients: string[]; 
              body: string; 
              subject?: string 
            };
            if (!recipients || !body) {
              throw new Error("Missing required fields: recipients and body");
            }
            
            const conversation = await this.client.createConversation(recipients, body, subject);
            return {
              content: [{ type: "text", text: JSON.stringify(conversation, null, 2) }]
            };
          }

          // Notifications
          case "canvas_list_notifications": {
            const notifications = await this.client.listNotifications();
            return {
              content: [{ type: "text", text: JSON.stringify(notifications, null, 2) }]
            };
          }

          // Syllabus
          case "canvas_get_syllabus": {
            const { course_id } = args as { course_id: number };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            const syllabus = await this.client.getSyllabus(course_id);
            return {
              content: [{ type: "text", text: JSON.stringify(syllabus, null, 2) }]
            };
          }

          // Delete Operations
          case "canvas_delete_course": {
            const { course_id, event = "delete" } = args as { course_id: number; event?: "delete" | "conclude" };
            if (!course_id) throw new Error("Missing required field: course_id");
            
            await this.client.deleteCourse(course_id, event);
            return {
              content: [{ type: "text", text: `Successfully ${event}d course ${course_id}` }]
            };
          }

          case "canvas_delete_assignment": {
            const { course_id, assignment_id } = args as { course_id: number; assignment_id: number };
            if (!course_id || !assignment_id) {
              throw new Error("Missing required fields: course_id and assignment_id");
            }
            
            await this.client.deleteAssignment(course_id, assignment_id);
            return {
              content: [{ type: "text", text: `Successfully deleted assignment ${assignment_id} from course ${course_id}` }]
            };
          }

          case "canvas_delete_announcement": {
            const { course_id, announcement_id } = args as { course_id: number; announcement_id: number };
            if (!course_id || !announcement_id) {
              throw new Error("Missing required fields: course_id and announcement_id");
            }
            
            await this.client.deleteAnnouncement(course_id, announcement_id);
            return {
              content: [{ type: "text", text: `Successfully deleted announcement ${announcement_id} from course ${course_id}` }]
            };
          }

          case "canvas_delete_quiz": {
            const { course_id, quiz_id } = args as { course_id: number; quiz_id: number };
            if (!course_id || !quiz_id) {
              throw new Error("Missing required fields: course_id and quiz_id");
            }
            
            await this.client.deleteQuiz(course_id, quiz_id);
            return {
              content: [{ type: "text", text: `Successfully deleted quiz ${quiz_id} from course ${course_id}` }]
            };
          }

          case "canvas_delete_conversation": {
            const { conversation_id } = args as { conversation_id: number };
            if (!conversation_id) throw new Error("Missing required field: conversation_id");
            
            await this.client.deleteConversation(conversation_id);
            return {
              content: [{ type: "text", text: `Successfully deleted conversation ${conversation_id}` }]
            };
          }

          case "canvas_unenroll_user": {
            const { course_id, enrollment_id } = args as { course_id: number; enrollment_id: number };
            if (!course_id || !enrollment_id) {
              throw new Error("Missing required fields: course_id and enrollment_id");
            }
            
            await this.client.unenrollUser(course_id, enrollment_id);
            return {
              content: [{ type: "text", text: `Successfully unenrolled user (enrollment ${enrollment_id}) from course ${course_id}` }]
            };
          }
          
          default:
            throw new Error(`Unknown tool: ${toolName}`);
        }
      } catch (error) {
        console.error(`Error executing tool ${request.params.name}:`, error);
        return {
          content: [{
            type: "text",
            text: `Error: ${error instanceof Error ? error.message : String(error)}`
          }],
          isError: true
        };
      }
    });
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error(`${this.config.name} running on stdio`);
  }
}

// Main entry point with enhanced configuration
async function main() {
  // Get current file's directory in ES modules
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);

  // Enhanced environment loading
  const envPaths = [
    '.env',
    'src/.env',
    path.join(__dirname, '.env'),
    path.join(process.cwd(), '.env'),
    path.join(__dirname, '..', '.env'), // Parent directory
  ];

  let loaded = false;
  for (const envPath of envPaths) {
    const result = dotenv.config({ path: envPath });
    if (result.parsed) {
      console.error(`Loaded environment from: ${envPath}`);
      loaded = true;
      break;
    }
  }

  if (!loaded) {
    console.error('Warning: No .env file found');
  }

  const token = process.env.CANVAS_API_TOKEN;
  const domain = process.env.CANVAS_DOMAIN;

  if (!token || !domain) {
    console.error("Missing required environment variables:");
    console.error("- CANVAS_API_TOKEN: Your Canvas API token");
    console.error("- CANVAS_DOMAIN: Your Canvas domain (e.g., school.instructure.com)");
    process.exit(1);
  }

  const config: MCPServerConfig = {
    name: "canvas-mcp-server",
    version: "2.2.3",
    canvas: {
      token,
      domain,
      maxRetries: parseInt(process.env.CANVAS_MAX_RETRIES || '3'),
      retryDelay: parseInt(process.env.CANVAS_RETRY_DELAY || '1000'),
      timeout: parseInt(process.env.CANVAS_TIMEOUT || '30000')
    },
    logging: {
      level: (process.env.LOG_LEVEL as any) || 'info'
    }
  };

  try {
    const server = new CanvasMCPServer(config);
    await server.run();
  } catch (error) {
    console.error("Fatal error:", error);
    process.exit(1);
  }
}

main().catch(console.error);