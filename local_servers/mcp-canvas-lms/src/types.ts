// src/types.ts

/**
 * Branded types for better type safety with IDs
 */
export type CourseId = number & { readonly brand: unique symbol };
export type AssignmentId = number & { readonly brand: unique symbol };
export type UserId = number & { readonly brand: unique symbol };
export type EnrollmentId = number & { readonly brand: unique symbol };

/**
 * Error types
 */
export class CanvasAPIError extends Error {
  constructor(
    message: string,
    public readonly statusCode?: number,
    public readonly response?: unknown
  ) {
    super(message);
    this.name = 'CanvasAPIError';
  }
}

export class CanvasValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CanvasValidationError';
  }
}

/**
 * API Response types
 */
export interface PaginatedResponse<T> {
  readonly data: ReadonlyArray<T>;
  readonly hasMore: boolean;
  readonly nextPage?: string;
}

export interface CanvasUser {
  readonly id: UserId;
  readonly name: string;
  readonly sortable_name: string;
  readonly short_name: string;
  readonly sis_user_id: string | null;
  readonly email: string;
  readonly avatar_url: string;
  readonly login_id?: string;
}

export interface CanvasUserProfile {
  id: number;
  name: string;
  sortable_name: string;
  short_name: string;
  sis_user_id: string | null;
  login_id: string;
  avatar_url: string;
  primary_email: string;
  locale: string;
  bio: string | null;
  title?: string;
  time_zone?: string;
  calendar?: any;
}

export interface CanvasCourse {
  readonly id: CourseId;
  readonly name: string;
  readonly course_code: string;
  readonly workflow_state: CanvasCourseState;
  readonly account_id: number;
  readonly start_at: string | null;
  readonly end_at: string | null;
  readonly enrollments?: ReadonlyArray<CanvasEnrollment>;
  readonly total_students?: number;
  readonly syllabus_body?: string;
  readonly term?: CanvasTerm;
  readonly course_progress?: CanvasCourseProgress;
}

export interface CanvasTerm {
  id: number;
  name: string;
  start_at: string | null;
  end_at: string | null;
}

export interface CanvasCourseProgress {
  requirement_count: number;
  requirement_completed_count: number;
  next_requirement_url: string | null;
  completed_at: string | null;
}

export type CanvasCourseState = 
  | 'unpublished'
  | 'available'
  | 'completed'
  | 'deleted';

export interface CanvasAssignment {
  readonly id: AssignmentId;
  readonly course_id: CourseId;
  readonly name: string;
  readonly description: string;
  readonly due_at: string | null;
  readonly lock_at: string | null;
  readonly unlock_at: string | null;
  readonly points_possible: number;
  readonly position: number;
  readonly submission_types: ReadonlyArray<CanvasSubmissionType>;
  readonly assignment_group_id: number;
  readonly assignment_group?: CanvasAssignmentGroup;
  readonly rubric?: CanvasRubric[];
  readonly rubric_settings?: CanvasRubricSettings;
  readonly allowed_extensions?: string[];
  readonly submission?: CanvasSubmission;
  readonly html_url: string;
  readonly published: boolean;
  readonly grading_type: CanvasGradingType;
}

export type CanvasGradingType = 'pass_fail' | 'percent' | 'letter_grade' | 'gpa_scale' | 'points';

export interface CanvasAssignmentGroup {
  id: number;
  name: string;
  position: number;
  weight: number;
  assignments?: CanvasAssignment[];
  group_weight: number;
}

export type CanvasSubmissionType =
  | 'none'
  | 'online_text_entry'
  | 'online_url'
  | 'online_upload'
  | 'media_recording'
  | 'student_annotation';

export interface CanvasSubmission {
  readonly id: number;
  readonly assignment_id: AssignmentId;
  readonly user_id: UserId;
  readonly submitted_at: string | null;
  readonly score: number | null;
  readonly grade: string | null;
  readonly attempt: number;
  readonly workflow_state: CanvasSubmissionState;
  readonly body?: string;
  readonly url?: string;
  readonly attachments?: CanvasFile[];
  readonly submission_comments?: CanvasSubmissionComment[];
  readonly rubric_assessment?: CanvasRubricAssessment;
  readonly late: boolean;
  readonly missing: boolean;
}

export interface CanvasSubmissionComment {
  id: number;
  comment: string;
  created_at: string;
  author_id: number;
  author_name: string;
  attachments?: CanvasFile[];
}

export interface CanvasRubricAssessment {
  [criterionId: string]: {
    points: number;
    rating_id?: string;
    comments?: string;
  };
}

export type CanvasSubmissionState =
  | 'submitted'
  | 'unsubmitted'
  | 'graded'
  | 'pending_review';

export interface CanvasEnrollment {
  readonly id: EnrollmentId;
  readonly user_id: UserId;
  readonly course_id: CourseId;
  readonly type: CanvasEnrollmentType;
  readonly role: string;
  readonly enrollment_state: CanvasEnrollmentState;
  readonly grades?: CanvasGrades;
  readonly user?: CanvasUser;
  readonly observed_users?: CanvasUser[];
}

export type CanvasEnrollmentType =
  | 'StudentEnrollment'
  | 'TeacherEnrollment'
  | 'TaEnrollment'
  | 'DesignerEnrollment'
  | 'ObserverEnrollment';

export type CanvasEnrollmentState =
  | 'active'
  | 'invited'
  | 'inactive'
  | 'completed'
  | 'rejected';

export interface CanvasGrades {
  readonly current_score: number | null;
  readonly final_score: number | null;
  readonly current_grade: string | null;
  readonly final_grade: string | null;
  readonly override_score?: number | null;
  readonly override_grade?: string | null;
}

export interface CanvasDiscussionTopic {
  id: number;
  title: string;
  message: string;
  html_url: string;
  posted_at: string;
  assignment_id: number | null;
  assignment?: CanvasAssignment;
  discussion_type: string;
  require_initial_post: boolean;
  user_has_posted: boolean;
  discussion_subentry_count: number;
  read_state: 'read' | 'unread';
  unread_count: number;
}

export interface CanvasModule {
  id: number;
  name: string;
  position: number;
  unlock_at: string | null;
  require_sequential_progress: boolean;
  prerequisite_module_ids: number[];
  state: CanvasModuleState;
  completed_at: string | null;
  items_count: number;
  items_url: string;
  items?: CanvasModuleItem[];
}

export type CanvasModuleState = 'locked' | 'unlocked' | 'started' | 'completed';

export interface CanvasModuleItem {
  id: number;
  title: string;
  type: CanvasModuleItemType;
  module_id: number;
  position: number;
  indent: number;
  html_url: string;
  url?: string;
  page_url?: string;
  external_url?: string;
  content_id?: number;
  content_details?: CanvasModuleItemContentDetails;
  completion_requirement?: CanvasModuleItemCompletionRequirement;
  published: boolean;
}

export type CanvasModuleItemType = 
  | 'File'
  | 'Page'
  | 'Discussion'
  | 'Assignment'
  | 'Quiz'
  | 'SubHeader'
  | 'ExternalUrl'
  | 'ExternalTool';

export interface CanvasModuleItemContentDetails {
  points_possible?: number;
  due_at?: string;
  unlock_at?: string;
  lock_at?: string;
}

export interface CanvasModuleItemCompletionRequirement {
  type: 'must_view' | 'must_submit' | 'must_contribute' | 'min_score';
  min_score?: number;
  completed: boolean;
}

export interface CanvasQuiz {
  id: number;
  title: string;
  html_url: string;
  quiz_type: CanvasQuizType;
  assignment_id?: number;
  time_limit: number | null;
  published: boolean;
  description: string | null;
  due_at: string | null;
  lock_at: string | null;
  unlock_at: string | null;
  points_possible: number;
  question_count: number;
  allowed_attempts: number;
  scoring_policy: 'keep_highest' | 'keep_latest';
  show_correct_answers: boolean;
  show_correct_answers_at: string | null;
  hide_correct_answers_at: string | null;
  shuffle_answers: boolean;
  has_access_code: boolean;
  ip_filter?: string;
  locked_for_user: boolean;
  lock_explanation?: string;
}

export type CanvasQuizType = 'practice_quiz' | 'assignment' | 'graded_survey' | 'survey';

export interface CanvasQuizQuestion {
  id?: number;
  quiz_id?: number;
  position?: number;
  question_name: string;
  question_type: QuizQuestionType;
  question_text: string;
  points_possible: number;
  correct_comments?: string;
  incorrect_comments?: string;
  neutral_comments?: string;
  answers?: QuizAnswer[];
  variables?: any;
  formulas?: any;
  answer_tolerance?: number;
  formula_decimal_places?: number;
  matches?: any[];
  matching_answer_incorrect_matches?: string;
}

export type QuizQuestionType =
  | 'multiple_choice_question'
  | 'true_false_question'
  | 'short_answer_question'
  | 'fill_in_multiple_blanks_question'
  | 'multiple_answers_question'
  | 'multiple_dropdowns_question'
  | 'matching_question'
  | 'numerical_question'
  | 'calculated_question'
  | 'essay_question'
  | 'file_upload_question'
  | 'text_only_question';

export interface QuizAnswer {
  id?: number;
  text?: string;
  html?: string;
  comments?: string;
  weight?: number;
  blank_id?: string;
  answer_text?: string;
  answer_match_left?: string;
  answer_match_right?: string;
  numerical_answer_type?: string;
  exact?: number;
  margin?: number;
  approximate?: number;
  precision?: number;
  start?: number;
  end?: number;
}

export interface QuizSubmissionAnswer {
  question_id: number;
  answer?: string | number | boolean | string[] | number[];
  answer_id?: number;
  match?: Array<{ answer_id: number; match_id: number }>;
}

export interface QuizSubmission {
  id?: number;
  quiz_id: number;
  user_id?: number;
  submission_id?: number;
  started_at?: string;
  finished_at?: string;
  end_at?: string;
  attempt: number;
  extra_attempts?: number;
  extra_time?: number;
  manually_unlocked?: boolean;
  time_spent?: number;
  score?: number;
  score_before_regrade?: number;
  kept_score?: number;
  fudge_points?: number;
  has_seen_results?: boolean;
  workflow_state?: 'untaken' | 'pending_review' | 'complete' | 'settings_only' | 'preview';
  validation_token?: string;
}

export interface CanvasAnnouncement {
  id: number;
  title: string;
  message: string;
  posted_at: string;
  html_url: string;
  user_has_posted: boolean;
  discussion_subentry_count: number;
}

export interface CanvasScope {
  resource: string;
  resource_name: string;
  controller: string;
  action: string;
  verb: string;
  scope: string;
}

export interface CanvasAssignmentSubmission {
  id: number;
  submission_type: string;
  body?: string;
  url?: string;
  submitted_at: string | null;
  assignment_id: number;
  user_id: number;
  workflow_state: string;
  file_ids?: number[];
  attachments?: CanvasFile[];
}

// New interfaces for student-focused features

export interface CanvasPage {
  page_id: number;
  url: string;
  title: string;
  body: string;
  created_at: string;
  updated_at: string;
  published: boolean;
  front_page: boolean;
  locked_for_user: boolean;
  lock_explanation?: string;
  editing_roles: string;
  html_url: string;
}

export interface CanvasCalendarEvent {
  id: number;
  title: string;
  start_at: string;
  end_at: string;
  description: string;
  location_name?: string;
  location_address?: string;
  context_type: 'Course' | 'User' | 'Group';
  context_id: number;
  workflow_state: 'active' | 'deleted';
  hidden: boolean;
  url?: string;
  html_url: string;
  all_day: boolean;
  assignment?: CanvasAssignment;
}

export interface CanvasRubric {
  id: number;
  title: string;
  context_id: number;
  context_type: string;
  points_possible: number;
  reusable: boolean;
  public: boolean;
  read_only: boolean;
  free_form_criterion_comments: boolean;
  criteria: CanvasRubricCriterion[];
}

export interface CanvasRubricCriterion {
  id: string;
  description: string;
  long_description: string;
  points: number;
  criterion_use_range: boolean;
  ratings: CanvasRubricRating[];
}

export interface CanvasRubricRating {
  id: string;
  description: string;
  long_description: string;
  points: number;
}

export interface CanvasRubricSettings {
  points_possible: number;
  free_form_criterion_comments: boolean;
  hide_score_total?: boolean;
  hide_points?: boolean;
}

export interface CanvasConversation {
  id: number;
  subject: string;
  workflow_state: 'read' | 'unread' | 'archived';
  last_message: string;
  last_message_at: string;
  last_authored_message: string;
  last_authored_message_at: string;
  message_count: number;
  subscribed: boolean;
  private: boolean;
  starred: boolean;
  properties: string[];
  audience: number[];
  audience_contexts: {
    [key: string]: string[];
  };
  avatar_url: string;
  participants: CanvasConversationParticipant[];
  messages?: CanvasConversationMessage[];
}

export interface CanvasConversationParticipant {
  id: number;
  name: string;
  full_name: string;
  avatar_url: string;
}

export interface CanvasConversationMessage {
  id: number;
  created_at: string;
  body: string;
  author_id: number;
  generated: boolean;
  media_comment?: any;
  forwarded_messages?: CanvasConversationMessage[];
  attachments?: CanvasFile[];
}

export interface CanvasNotification {
  id: number;
  title: string;
  message: string;
  html_url: string;
  type: string;
  read_state: boolean;
  created_at: string;
  updated_at: string;
  context_type: string;
  context_id: number;
}

export interface CanvasFile {
  id: number;
  uuid: string;
  folder_id: number;
  display_name: string;
  filename: string;
  content_type: string;
  url: string;
  size: number;
  created_at: string;
  updated_at: string;
  unlock_at?: string;
  locked: boolean;
  hidden: boolean;
  lock_at?: string;
  hidden_for_user: boolean;
  thumbnail_url?: string;
  modified_at: string;
  mime_class: string;
  media_entry_id?: string;
  locked_for_user: boolean;
  lock_explanation?: string;
  preview_url?: string;
}

export interface CanvasSyllabus {
  course_id: number;
  syllabus_body: string;
}

export interface CanvasDashboard {
  dashboard_cards: CanvasDashboardCard[];
  planner_items: CanvasPlannerItem[];
}

export interface CanvasDashboardCard {
  id: number;
  shortName: string;
  originalName: string;
  courseCode: string;
  assetString: string;
  href: string;
  term?: CanvasTerm;
  subtitle: string;
  enrollmentType: string;
  observee?: string;
  image?: string;
  color: string;
  position?: number;
}

export interface CanvasPlannerItem {
  context_type: string;
  context_name: string;
  planner_date: string;
  submissions: boolean;
  plannable_id: number;
  plannable_type: string;
  plannable: {
    id: number;
    title: string;
    due_at: string;
    points_possible?: number;
  };
  html_url: string;
  completed: boolean;
}

/**
 * Tool input types with strict validation
 */
export interface CreateCourseArgs {
  account_id: number;
  name: string;
  course_code?: string;
  start_at?: string;
  end_at?: string;
  license?: string;
  is_public?: boolean;
  is_public_to_auth_users?: boolean;
  public_syllabus?: boolean;
  public_syllabus_to_auth?: boolean;
  public_description?: string;
  allow_student_wiki_edits?: boolean;
  allow_wiki_comments?: boolean;
  allow_student_forum_attachments?: boolean;
  open_enrollment?: boolean;
  self_enrollment?: boolean;
  restrict_enrollments_to_course_dates?: boolean;
  term_id?: number;
  sis_course_id?: string;
  integration_id?: string;
  hide_final_grades?: boolean;
  apply_assignment_group_weights?: boolean;
  time_zone?: string;
  syllabus_body?: string;
}

export interface UpdateCourseArgs {
  course_id: number;
  name?: string;
  course_code?: string;
  start_at?: string;
  end_at?: string;
  event?: 'offer' | 'claim' | 'conclude' | 'delete' | 'undelete';  // offer=发布, claim=取消发布, conclude=结束, delete=删除
  is_public?: boolean;
  is_public_to_auth_users?: boolean;
  public_syllabus?: boolean;
  public_syllabus_to_auth?: boolean;
  public_description?: string;
  restrict_enrollments_to_course_dates?: boolean;
  time_zone?: string;
  syllabus_body?: string;
}

export interface CreateAssignmentArgs {
  course_id: number;
  name: string;
  description?: string;
  due_at?: string;
  lock_at?: string;
  unlock_at?: string;
  points_possible?: number;
  grading_type?: CanvasGradingType;
  submission_types?: CanvasSubmissionType[];
  allowed_extensions?: string[];
  assignment_group_id?: number;
  position?: number;
  peer_reviews?: boolean;
  automatic_peer_reviews?: boolean;
  notify_of_update?: boolean;
  group_category_id?: number;
  published?: boolean;
  omit_from_final_grade?: boolean;
  hide_in_gradebook?: boolean;
}

export interface UpdateAssignmentArgs {
  course_id: number;
  assignment_id: number;
  name?: string;
  description?: string;
  due_at?: string;
  lock_at?: string;
  unlock_at?: string;
  points_possible?: number;
  grading_type?: CanvasGradingType;
  submission_types?: CanvasSubmissionType[];
  allowed_extensions?: string[];
  assignment_group_id?: number;
  position?: number;
  peer_reviews?: boolean;
  automatic_peer_reviews?: boolean;
  notify_of_update?: boolean;
  published?: boolean;
  omit_from_final_grade?: boolean;
  hide_in_gradebook?: boolean;
}

export interface SubmitGradeArgs {
  course_id: number;
  assignment_id: number;
  user_id: number;
  grade: number | string;
  comment?: string;
  rubric_assessment?: CanvasRubricAssessment;
}

export interface EnrollUserArgs {
  course_id: number;
  user_id: number;
  role?: string;
  enrollment_state?: string;
  notify?: boolean;
  limit_privileges_to_course_section?: boolean;
}

export interface SubmitAssignmentArgs {
  course_id: number;
  assignment_id: number;
  submission_type: CanvasSubmissionType;
  body?: string;
  url?: string;
  file_ids?: number[];
  media_comment_id?: string;
  media_comment_type?: 'audio' | 'video';
  user_id?: number; // For teachers submitting on behalf of students
}

export interface FileUploadArgs {
  course_id?: number;
  folder_id?: number;
  name: string;
  size: number;
  content_type?: string;
  on_duplicate?: 'rename' | 'overwrite';
}

// Configuration interfaces
export interface CanvasClientConfig {
  token: string;
  domain: string;
  maxRetries?: number;
  retryDelay?: number;
  timeout?: number;
}

export interface MCPServerConfig {
  name: string;
  version: string;
  canvas: CanvasClientConfig;
  logging?: {
    level: 'debug' | 'info' | 'warn' | 'error';
    destination?: string;
  };
  rateLimit?: {
    requests: number;
    window: number; // in milliseconds
  };
}
// Canvas API Error Response
export interface CanvasErrorResponse {
  message?: string;
  errors?: Array<{
    message: string;
    error_code?: string;
  }>;
  error_report_id?: string;
}

// Account-level interfaces
export interface CanvasAccount {
  id: number;
  name: string;
  uuid: string;
  parent_account_id: number | null;
  root_account_id: number | null;
  default_storage_quota_mb: number;
  default_user_storage_quota_mb: number;
  default_group_storage_quota_mb: number;
  default_time_zone: string;
  sis_account_id: string | null;
  integration_id: string | null;
  sis_import_id: number | null;
  lti_guid: string;
  workflow_state: string;
}

export interface CreateUserArgs {
  account_id: number;
  user: {
    name: string;
    short_name?: string;
    sortable_name?: string;
    time_zone?: string;
    locale?: string;
    birthdate?: string;
    terms_of_use?: boolean;
    skip_registration?: boolean;
  };
  pseudonym: {
    unique_id: string;
    password?: string;
    sis_user_id?: string;
    integration_id?: string;
    send_confirmation?: boolean;
    force_validations?: boolean;
    authentication_provider_id?: string;
  };
  communication_channel?: {
    type: 'email' | 'sms';
    address: string;
    skip_confirmation?: boolean;
  };
  force_validations?: boolean;
  enable_sis_reactivation?: boolean;
}

export interface CanvasAccountReport {
  id: number;
  report: string;
  file_url?: string;
  attachment?: CanvasFile;
  status: 'created' | 'running' | 'complete' | 'error';
  created_at: string;
  started_at?: string;
  ended_at?: string;
  parameters: Record<string, any>;
  progress: number;
  current_line?: number;
}

export interface CreateReportArgs {
  account_id: number;
  report: string;
  parameters?: Record<string, any>;
}

export interface ListAccountCoursesArgs {
  account_id: number;
  with_enrollments?: boolean;
  enrollment_type?: string[];
  published?: boolean;
  completed?: boolean;
  blueprint?: boolean;
  blueprint_associated?: boolean;
  by_teachers?: number[];
  by_subaccounts?: number[];
  hide_enrollmentless_courses?: boolean;
  state?: ('created' | 'claimed' | 'available' | 'completed' | 'deleted' | 'all')[];
  enrollment_term_id?: number;
  search_term?: string;
  include?: string[];
  sort?: 'course_name' | 'sis_course_id' | 'teacher' | 'account_name';
  order?: 'asc' | 'desc';
  search_by?: 'course' | 'teacher';
}

export interface ListAccountUsersArgs {
  session_id?: string;
  account_id?: number;
  search_term?: string;
  enrollment_type?: string;
  sort?: 'username' | 'email' | 'sis_id' | 'last_login';
  order?: 'asc' | 'desc';
  include?: string[];
  page?: number;
  per_page?: number;
}
