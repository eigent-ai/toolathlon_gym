import pg from 'pg';
const { Pool } = pg;

function makeResponse(data: any, status = 200) {
  return { data, status, statusText: 'OK', headers: {}, config: {} };
}

function stripLeadingSlash(url: string): string {
  return url.replace(/^\/+/, '');
}

interface RouteMatch {
  table: string;
  conditions: string[];
  values: any[];
  isSingle: boolean;
  // for special handling
  special?: string;
}

export class PgCanvasRouter {
  private pool: pg.Pool;

  constructor() {
    this.pool = new Pool({
      host: process.env.PG_HOST || 'localhost',
      port: parseInt(process.env.PG_PORT || '5432', 10),
      database: process.env.PG_DATABASE || 'toolathlon',
      user: process.env.PG_USER || 'postgres',
      password: process.env.PG_PASSWORD || 'postgres',
    });
  }

  async get(url: string, config?: any): Promise<any> {
    const path = stripLeadingSlash(url);
    const params = config?.params || {};

    try {
      const result = await this.routeGet(path, params);
      return makeResponse(result);
    } catch (err: any) {
      console.error(`[PgCanvasRouter] GET ${path} error:`, err.message);
      return makeResponse([], 200);
    }
  }

  async post(url: string, data?: any, config?: any): Promise<any> {
    const path = stripLeadingSlash(url);
    const body = data || {};

    try {
      const result = await this.routePost(path, body);
      return makeResponse(result, 201);
    } catch (err: any) {
      console.error(`[PgCanvasRouter] POST ${path} error:`, err.message);
      return makeResponse({}, 201);
    }
  }

  async put(url: string, data?: any, config?: any): Promise<any> {
    const path = stripLeadingSlash(url);
    const body = data || {};

    try {
      const result = await this.routePut(path, body);
      return makeResponse(result);
    } catch (err: any) {
      console.error(`[PgCanvasRouter] PUT ${path} error:`, err.message);
      return makeResponse({});
    }
  }

  async delete(url: string, config?: any): Promise<any> {
    const path = stripLeadingSlash(url);

    try {
      const result = await this.routeDelete(path, config?.data || {});
      return makeResponse(result);
    } catch (err: any) {
      console.error(`[PgCanvasRouter] DELETE ${path} error:`, err.message);
      return makeResponse({});
    }
  }

  // ---- GET routing ----

  private async routeGet(path: string, params: any): Promise<any> {
    let m: RegExpMatchArray | null;

    // --- Users ---
    // GET /users/self/profile
    if (path === 'users/self/profile') {
      const res = await this.pool.query('SELECT * FROM canvas.users WHERE id = 1');
      return res.rows[0] || {};
    }
    // GET /users/self/dashboard
    if (path === 'users/self/dashboard') {
      return { links: [], recent_activity: [] };
    }
    // GET /users/self/activity_stream
    if (path === 'users/self/activity_stream') {
      return [];
    }
    // GET /users/self/upcoming_events
    if (path === 'users/self/upcoming_events') {
      const res = await this.pool.query(`
        SELECT a.*, json_build_object('id', a.id, 'name', a.name) as assignment
        FROM canvas.assignments a
        WHERE a.due_at > NOW()
        ORDER BY a.due_at ASC
        LIMIT $1
      `, [params.limit || 10]);
      return res.rows;
    }
    // GET /users/self/grades
    if (path === 'users/self/grades') {
      const res = await this.pool.query(`
        SELECT e.*, c.name as course_name
        FROM canvas.enrollments e
        JOIN canvas.courses c ON c.id = e.course_id
        WHERE e.user_id = 1
      `);
      return res.rows;
    }
    // GET /users/self/courses
    if (path === 'users/self/courses') {
      const res = await this.pool.query(`
        SELECT c.* FROM canvas.courses c
        JOIN canvas.enrollments e ON e.course_id = c.id
        WHERE e.user_id = 1
      `);
      return res.rows;
    }
    // GET /users/self
    if (path === 'users/self') {
      const res = await this.pool.query('SELECT * FROM canvas.users WHERE id = 1');
      return res.rows[0] || {};
    }
    // GET /users/:id/profile
    m = path.match(/^users\/(\d+)\/profile$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.users WHERE id = $1', [m[1]]);
      return res.rows[0] || {};
    }
    // GET /users/:id
    m = path.match(/^users\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.users WHERE id = $1', [m[1]]);
      return res.rows[0] || {};
    }

    // --- Dashboard ---
    if (path === 'dashboard/dashboard_cards') {
      const res = await this.pool.query(`
        SELECT c.id, c.name, c.course_code, c.enrollment_term_id
        FROM canvas.courses c
        JOIN canvas.enrollments e ON e.course_id = c.id
        WHERE e.user_id = 1
      `);
      return res.rows;
    }

    // --- Conversations ---
    if (path === 'conversations') {
      const res = await this.pool.query('SELECT * FROM canvas.conversations ORDER BY last_message_at DESC');
      return res.rows;
    }
    m = path.match(/^conversations\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.conversations WHERE id = $1', [m[1]]);
      return res.rows[0] || {};
    }

    // --- Calendar events ---
    if (path === 'calendar_events') {
      let query = 'SELECT * FROM canvas.calendar_events WHERE 1=1';
      const values: any[] = [];
      let idx = 1;
      if (params.start_date) {
        query += ` AND start_at >= $${idx}`;
        values.push(params.start_date);
        idx++;
      }
      if (params.end_date) {
        query += ` AND end_at <= $${idx}`;
        values.push(params.end_date);
        idx++;
      }
      query += ' ORDER BY start_at';
      const res = await this.pool.query(query, values);
      return res.rows;
    }

    // --- Files ---
    m = path.match(/^files\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.files WHERE id = $1', [m[1]]);
      return res.rows[0] || {};
    }
    m = path.match(/^folders\/(\d+)\/files$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.files WHERE folder_id = $1', [m[1]]);
      return res.rows;
    }

    // --- Quiz submissions questions ---
    m = path.match(/^quiz_submissions\/(\d+)\/questions$/);
    if (m) {
      // Return quiz questions for this submission
      const subRes = await this.pool.query('SELECT quiz_id FROM canvas.quiz_submissions WHERE id = $1', [m[1]]);
      if (subRes.rows.length > 0) {
        const qRes = await this.pool.query('SELECT * FROM canvas.quiz_questions WHERE quiz_id = $1 ORDER BY position', [subRes.rows[0].quiz_id]);
        return { quiz_submission_questions: qRes.rows };
      }
      return { quiz_submission_questions: [] };
    }

    // --- Accounts ---
    if (path === 'accounts') {
      const res = await this.pool.query('SELECT * FROM canvas.accounts');
      return res.rows;
    }
    m = path.match(/^accounts\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.accounts WHERE id = $1', [m[1]]);
      return res.rows[0] || {};
    }
    m = path.match(/^accounts\/(\d+)\/courses$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.courses WHERE account_id = $1', [m[1]]);
      return res.rows;
    }
    m = path.match(/^accounts\/(\d+)\/users$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.users');
      return res.rows;
    }
    m = path.match(/^accounts\/(\d+)\/sub_accounts$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.accounts WHERE parent_account_id = $1', [m[1]]);
      return res.rows;
    }
    m = path.match(/^accounts\/(\d+)\/scopes$/);
    if (m) {
      return [];
    }
    m = path.match(/^accounts\/(\d+)\/reports(?:\/(.+)\/(\d+))?$/);
    if (m) {
      if (m[2] && m[3]) {
        return { id: parseInt(m[3]), report: m[2], status: 'complete', parameters: {} };
      }
      return [];
    }

    // --- Courses (top-level) ---
    if (path === 'courses') {
      let query = 'SELECT * FROM canvas.courses';
      const conditions: string[] = [];
      const values: any[] = [];
      let idx = 1;
      if (params.state) {
        const states = Array.isArray(params.state) ? params.state : [params.state];
        conditions.push(`workflow_state = ANY($${idx})`);
        values.push(states);
        idx++;
      }
      if (params.enrollment_state) {
        // Filter courses where user has active enrollment
        conditions.push(`id IN (SELECT course_id FROM canvas.enrollments WHERE user_id = 1 AND enrollment_state = $${idx})`);
        values.push(params.enrollment_state);
        idx++;
      }
      if (conditions.length > 0) {
        query += ' WHERE ' + conditions.join(' AND ');
      }
      query += ' ORDER BY id';
      const res = await this.pool.query(query, values);
      return res.rows;
    }

    // --- Course-level routes ---
    // Must check more specific patterns first

    // GET /courses/:id/assignments/:aid/submissions/:uid
    m = path.match(/^courses\/(\d+)\/assignments\/(\d+)\/submissions\/(.+)$/);
    if (m) {
      const userId = m[3] === 'self' ? 1 : parseInt(m[3]);
      const res = await this.pool.query(
        'SELECT * FROM canvas.submissions WHERE assignment_id = $1 AND user_id = $2',
        [m[2], userId]
      );
      return res.rows[0] || {};
    }

    // GET /courses/:id/assignments/:aid/submissions
    m = path.match(/^courses\/(\d+)\/assignments\/(\d+)\/submissions$/);
    if (m) {
      const res = await this.pool.query(
        'SELECT * FROM canvas.submissions WHERE assignment_id = $1',
        [m[2]]
      );
      return res.rows;
    }

    // GET /courses/:id/assignments/:aid
    m = path.match(/^courses\/(\d+)\/assignments\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.assignments WHERE id = $1 AND course_id = $2', [m[2], m[1]]);
      return res.rows[0] || {};
    }

    // GET /courses/:id/assignments
    m = path.match(/^courses\/(\d+)\/assignments$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.assignments WHERE course_id = $1 ORDER BY position', [m[1]]);
      return res.rows;
    }

    // GET /courses/:id/assignment_groups/:gid
    m = path.match(/^courses\/(\d+)\/assignment_groups\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.assignment_groups WHERE id = $1 AND course_id = $2', [m[2], m[1]]);
      const group = res.rows[0] || {};
      if (params.include && params.include.includes('assignments')) {
        const aRes = await this.pool.query('SELECT * FROM canvas.assignments WHERE assignment_group_id = $1', [m[2]]);
        group.assignments = aRes.rows;
      }
      return group;
    }

    // GET /courses/:id/assignment_groups
    m = path.match(/^courses\/(\d+)\/assignment_groups$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.assignment_groups WHERE course_id = $1 ORDER BY position', [m[1]]);
      if (params.include && params.include.includes('assignments')) {
        for (const group of res.rows) {
          const aRes = await this.pool.query('SELECT * FROM canvas.assignments WHERE assignment_group_id = $1', [group.id]);
          group.assignments = aRes.rows;
        }
      }
      return res.rows;
    }

    // GET /courses/:id/quizzes/:qid/questions/:questionId
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/questions\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.quiz_questions WHERE id = $1 AND quiz_id = $2', [m[3], m[2]]);
      return res.rows[0] || {};
    }

    // GET /courses/:id/quizzes/:qid/questions
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/questions$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.quiz_questions WHERE quiz_id = $1 ORDER BY position', [m[2]]);
      return res.rows;
    }

    // GET /courses/:id/quizzes/:qid/submissions
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/submissions$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.quiz_submissions WHERE quiz_id = $1', [m[2]]);
      return { quiz_submissions: res.rows };
    }

    // GET /courses/:id/quizzes/:qid
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.quizzes WHERE id = $1 AND course_id = $2', [m[2], m[1]]);
      return res.rows[0] || {};
    }

    // GET /courses/:id/quizzes
    m = path.match(/^courses\/(\d+)\/quizzes$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.quizzes WHERE course_id = $1', [m[1]]);
      return res.rows;
    }

    // GET /courses/:id/modules/:mid/items/:itemId
    m = path.match(/^courses\/(\d+)\/modules\/(\d+)\/items\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.module_items WHERE id = $1 AND module_id = $2', [m[3], m[2]]);
      return res.rows[0] || {};
    }

    // GET /courses/:id/modules/:mid/items
    m = path.match(/^courses\/(\d+)\/modules\/(\d+)\/items$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.module_items WHERE module_id = $1 ORDER BY position', [m[2]]);
      return res.rows;
    }

    // GET /courses/:id/modules/:mid
    m = path.match(/^courses\/(\d+)\/modules\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.modules WHERE id = $1 AND course_id = $2', [m[2], m[1]]);
      const mod = res.rows[0] || {};
      if (params.include && params.include.includes('items')) {
        const itemsRes = await this.pool.query('SELECT * FROM canvas.module_items WHERE module_id = $1 ORDER BY position', [m[2]]);
        mod.items = itemsRes.rows;
      }
      return mod;
    }

    // GET /courses/:id/modules
    m = path.match(/^courses\/(\d+)\/modules$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.modules WHERE course_id = $1 ORDER BY position', [m[1]]);
      if (params.include && params.include.includes('items')) {
        for (const mod of res.rows) {
          const itemsRes = await this.pool.query('SELECT * FROM canvas.module_items WHERE module_id = $1 ORDER BY position', [mod.id]);
          mod.items = itemsRes.rows;
        }
      }
      return res.rows;
    }

    // GET /courses/:id/discussion_topics/:tid
    m = path.match(/^courses\/(\d+)\/discussion_topics\/(\d+)$/);
    if (m) {
      // Could be a regular topic or announcement
      const res = await this.pool.query('SELECT * FROM canvas.discussion_topics WHERE id = $1 AND course_id = $2', [m[2], m[1]]);
      if (res.rows.length > 0) return res.rows[0];
      // Try announcements table
      const aRes = await this.pool.query('SELECT * FROM canvas.announcements WHERE id = $1 AND course_id = $2', [m[2], m[1]]);
      return aRes.rows[0] || {};
    }

    // GET /courses/:id/discussion_topics (may be announcements)
    m = path.match(/^courses\/(\d+)\/discussion_topics$/);
    if (m) {
      if (params.only_announcements) {
        const res = await this.pool.query('SELECT * FROM canvas.announcements WHERE course_id = $1', [m[1]]);
        return res.rows;
      }
      const res = await this.pool.query('SELECT * FROM canvas.discussion_topics WHERE course_id = $1', [m[1]]);
      return res.rows;
    }

    // GET /courses/:id/pages/:url
    m = path.match(/^courses\/(\d+)\/pages\/(.+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.pages WHERE course_id = $1 AND url = $2', [m[1], decodeURIComponent(m[2])]);
      return res.rows[0] || {};
    }

    // GET /courses/:id/pages
    m = path.match(/^courses\/(\d+)\/pages$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.pages WHERE course_id = $1', [m[1]]);
      return res.rows;
    }

    // GET /courses/:id/enrollments
    m = path.match(/^courses\/(\d+)\/enrollments$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.enrollments WHERE course_id = $1', [m[1]]);
      return res.rows;
    }

    // GET /courses/:id/users
    m = path.match(/^courses\/(\d+)\/users$/);
    if (m) {
      const res = await this.pool.query(`
        SELECT u.* FROM canvas.users u
        JOIN canvas.enrollments e ON e.user_id = u.id
        WHERE e.course_id = $1
      `, [m[1]]);
      return res.rows;
    }

    // GET /courses/:id/rubrics/:rid
    m = path.match(/^courses\/(\d+)\/rubrics\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.rubrics WHERE id = $1 AND course_id = $2', [m[2], m[1]]);
      return res.rows[0] || {};
    }

    // GET /courses/:id/rubrics
    m = path.match(/^courses\/(\d+)\/rubrics$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.rubrics WHERE course_id = $1', [m[1]]);
      return res.rows;
    }

    // GET /courses/:id/files
    m = path.match(/^courses\/(\d+)\/files$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.files');
      return res.rows;
    }

    // GET /courses/:id/folders
    m = path.match(/^courses\/(\d+)\/folders$/);
    if (m) {
      return [];
    }

    // GET /courses/:id/announcements
    m = path.match(/^courses\/(\d+)\/announcements$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.announcements WHERE course_id = $1', [m[1]]);
      return res.rows;
    }

    // GET /courses/:id (single course - must be AFTER all /courses/:id/* patterns)
    m = path.match(/^courses\/(\d+)$/);
    if (m) {
      const res = await this.pool.query('SELECT * FROM canvas.courses WHERE id = $1', [m[1]]);
      return res.rows[0] || {};
    }

    console.error(`[PgCanvasRouter] Unmatched GET: ${path}`);
    return [];
  }

  // ---- POST routing ----

  private async routePost(path: string, body: any): Promise<any> {
    let m: RegExpMatchArray | null;

    // POST /conversations
    if (path === 'conversations') {
      const row = await this.insertRow('canvas.conversations', {
        subject: body.subject || '',
        last_message: body.body || '',
        last_message_at: new Date().toISOString(),
        message_count: 1,
        participants: JSON.stringify(body.recipients || []),
        messages: JSON.stringify([{ body: body.body, created_at: new Date().toISOString() }]),
        workflow_state: 'read',
      });
      return row;
    }

    // POST /accounts/:id/courses
    m = path.match(/^accounts\/(\d+)\/courses$/);
    if (m) {
      const courseData = body.course || body;
      const row = await this.insertRow('canvas.courses', {
        ...courseData,
        account_id: m[1],
      });
      return row;
    }

    // POST /accounts/:id/users
    m = path.match(/^accounts\/(\d+)\/users$/);
    if (m) {
      const row = await this.insertRow('canvas.users', body);
      return row;
    }

    // POST /accounts/:id/reports/:report
    m = path.match(/^accounts\/(\d+)\/reports\/(.+)$/);
    if (m) {
      return { id: 1, report: m[2], status: 'created', parameters: body.parameters || {} };
    }

    // POST /courses/:id/assignments/:aid/submissions
    m = path.match(/^courses\/(\d+)\/assignments\/(\d+)\/submissions$/);
    if (m) {
      const subData = body.submission || body;
      const row = await this.insertRow('canvas.submissions', {
        assignment_id: m[2],
        user_id: 1,
        submission_type: subData.submission_type,
        body: subData.body || null,
        url: subData.url || null,
        submitted_at: new Date().toISOString(),
        workflow_state: 'submitted',
        attempt: 1,
      });
      return row;
    }

    // POST /courses/:id/enrollments
    m = path.match(/^courses\/(\d+)\/enrollments$/);
    if (m) {
      const enrollData = body.enrollment || body;
      const row = await this.insertRow('canvas.enrollments', {
        course_id: m[1],
        user_id: enrollData.user_id,
        type: enrollData.type || 'StudentEnrollment',
        enrollment_state: enrollData.enrollment_state || 'active',
        role: enrollData.type || 'StudentEnrollment',
      });
      return row;
    }

    // POST /courses/:id/quizzes/:qid/submissions
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/submissions$/);
    if (m) {
      const row = await this.insertRow('canvas.quiz_submissions', {
        quiz_id: m[2],
        user_id: 1,
        started_at: new Date().toISOString(),
        attempt: 1,
        workflow_state: 'untaken',
        validation_token: 'mock_token_' + Date.now(),
      });
      return row;
    }

    // POST /courses/:id/quizzes/:qid/submissions/:sid/complete
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/submissions\/(\d+)\/complete$/);
    if (m) {
      const res = await this.pool.query(
        `UPDATE canvas.quiz_submissions SET workflow_state = 'complete', finished_at = NOW() WHERE id = $1 RETURNING *`,
        [m[3]]
      );
      return res.rows[0] || {};
    }

    // POST /quiz_submissions/:id/questions
    m = path.match(/^quiz_submissions\/(\d+)\/questions$/);
    if (m) {
      // Store answers in submission_data
      await this.pool.query(
        `UPDATE canvas.quiz_submissions SET submission_data = $1 WHERE id = $2`,
        [JSON.stringify(body.quiz_questions || []), m[1]]
      );
      return { quiz_submission_questions: body.quiz_questions || [] };
    }

    // POST /courses/:id/quizzes/:qid/questions
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/questions$/);
    if (m) {
      const qData = body.question || body;
      const row = await this.insertRow('canvas.quiz_questions', {
        quiz_id: m[2],
        ...qData,
      });
      return row;
    }

    // POST /courses/:id/quizzes
    m = path.match(/^courses\/(\d+)\/quizzes$/);
    if (m) {
      const quizData = body.quiz || body;
      const row = await this.insertRow('canvas.quizzes', {
        course_id: m[1],
        ...quizData,
      });
      return row;
    }

    // POST /courses/:id/assignments
    m = path.match(/^courses\/(\d+)\/assignments$/);
    if (m) {
      const assignData = body.assignment || body;
      const row = await this.insertRow('canvas.assignments', {
        course_id: m[1],
        ...assignData,
      });
      return row;
    }

    // POST /courses/:id/discussion_topics/:tid/entries
    m = path.match(/^courses\/(\d+)\/discussion_topics\/(\d+)\/entries$/);
    if (m) {
      return { id: Date.now(), message: body.message, created_at: new Date().toISOString() };
    }

    // POST /courses/:id/discussion_topics (could be announcement)
    m = path.match(/^courses\/(\d+)\/discussion_topics$/);
    if (m) {
      if (body.is_announcement) {
        const row = await this.insertRow('canvas.announcements', {
          course_id: m[1],
          title: body.title,
          message: body.message,
          is_announcement: true,
          posted_at: body.delayed_post_at || new Date().toISOString(),
        });
        return row;
      }
      const row = await this.insertRow('canvas.discussion_topics', {
        course_id: m[1],
        title: body.title,
        message: body.message,
        published: body.published !== false,
      });
      return row;
    }

    // POST /courses/:id/files or /users/self/files or /folders/:id/files
    m = path.match(/^(?:courses\/\d+|users\/self|folders\/\d+)\/files$/);
    if (m) {
      const row = await this.insertRow('canvas.files', {
        display_name: body.name || 'uploaded_file',
        filename: body.name || 'uploaded_file',
        content_type: body.content_type || 'application/octet-stream',
        size: body.size || 0,
        url: `https://mock-canvas.local/files/${Date.now()}`,
      });
      // Return upload URL mock for two-step upload
      return {
        ...row,
        upload_url: `https://mock-canvas.local/upload/${Date.now()}`,
        upload_params: {},
      };
    }

    console.error(`[PgCanvasRouter] Unmatched POST: ${path}`);
    return {};
  }

  // ---- PUT routing ----

  private async routePut(path: string, body: any): Promise<any> {
    let m: RegExpMatchArray | null;

    // PUT /users/self
    if (path === 'users/self') {
      const userData = body.user || body;
      const row = await this.updateRow('canvas.users', 'id', 1, userData);
      return row;
    }

    // PUT /courses/:id/assignments/:aid/submissions/:uid
    m = path.match(/^courses\/(\d+)\/assignments\/(\d+)\/submissions\/(.+)$/);
    if (m) {
      const userId = m[3] === 'self' ? 1 : parseInt(m[3]);
      const subData = body.submission || body;
      const updateData: any = {};
      if (subData.posted_grade !== undefined) {
        updateData.grade = subData.posted_grade;
        updateData.score = parseFloat(subData.posted_grade) || null;
        updateData.graded_at = new Date().toISOString();
        updateData.workflow_state = 'graded';
      }
      // Check if submission exists
      const existing = await this.pool.query(
        'SELECT id FROM canvas.submissions WHERE assignment_id = $1 AND user_id = $2',
        [m[2], userId]
      );
      if (existing.rows.length > 0) {
        const row = await this.updateRow('canvas.submissions', 'id', existing.rows[0].id, updateData);
        return row;
      }
      // Create if not exists
      const row = await this.insertRow('canvas.submissions', {
        assignment_id: m[2],
        user_id: userId,
        ...updateData,
      });
      return row;
    }

    // PUT /courses/:id/assignments/:aid
    m = path.match(/^courses\/(\d+)\/assignments\/(\d+)$/);
    if (m) {
      const assignData = body.assignment || body;
      const row = await this.updateRow('canvas.assignments', 'id', parseInt(m[2]), assignData);
      return row;
    }

    // PUT /courses/:id/quizzes/:qid/questions/:questionId
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/questions\/(\d+)$/);
    if (m) {
      const qData = body.question || body;
      const row = await this.updateRow('canvas.quiz_questions', 'id', parseInt(m[3]), qData);
      return row;
    }

    // PUT /courses/:id/quizzes/:qid
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)$/);
    if (m) {
      const quizData = body.quiz || body;
      const row = await this.updateRow('canvas.quizzes', 'id', parseInt(m[2]), quizData);
      return row;
    }

    // PUT /courses/:id/modules/:mid/items/:itemId/done
    m = path.match(/^courses\/(\d+)\/modules\/(\d+)\/items\/(\d+)\/done$/);
    if (m) {
      return {};
    }

    // PUT /courses/:id
    m = path.match(/^courses\/(\d+)$/);
    if (m) {
      const courseData = body.course || body;
      const row = await this.updateRow('canvas.courses', 'id', parseInt(m[1]), courseData);
      return row;
    }

    console.error(`[PgCanvasRouter] Unmatched PUT: ${path}`);
    return {};
  }

  // ---- DELETE routing ----

  private async routeDelete(path: string, body: any): Promise<any> {
    let m: RegExpMatchArray | null;

    // DELETE /conversations/:id
    m = path.match(/^conversations\/(\d+)$/);
    if (m) {
      await this.pool.query('DELETE FROM canvas.conversations WHERE id = $1', [m[1]]);
      return {};
    }

    // DELETE /courses/:id/enrollments/:eid
    m = path.match(/^courses\/(\d+)\/enrollments\/(\d+)$/);
    if (m) {
      await this.pool.query('DELETE FROM canvas.enrollments WHERE id = $1', [m[2]]);
      return {};
    }

    // DELETE /courses/:id/assignments/:aid
    m = path.match(/^courses\/(\d+)\/assignments\/(\d+)$/);
    if (m) {
      await this.pool.query('DELETE FROM canvas.assignments WHERE id = $1', [m[2]]);
      return {};
    }

    // DELETE /courses/:id/quizzes/:qid/questions/:questionId
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)\/questions\/(\d+)$/);
    if (m) {
      await this.pool.query('DELETE FROM canvas.quiz_questions WHERE id = $1', [m[3]]);
      return {};
    }

    // DELETE /courses/:id/quizzes/:qid
    m = path.match(/^courses\/(\d+)\/quizzes\/(\d+)$/);
    if (m) {
      await this.pool.query('DELETE FROM canvas.quizzes WHERE id = $1', [m[2]]);
      return {};
    }

    // DELETE /courses/:id/discussion_topics/:tid (could be announcement)
    m = path.match(/^courses\/(\d+)\/discussion_topics\/(\d+)$/);
    if (m) {
      await this.pool.query('DELETE FROM canvas.discussion_topics WHERE id = $1', [m[2]]);
      await this.pool.query('DELETE FROM canvas.announcements WHERE id = $1', [m[2]]);
      return {};
    }

    // DELETE /courses/:id
    m = path.match(/^courses\/(\d+)$/);
    if (m) {
      if (body?.event === 'conclude') {
        await this.pool.query(`UPDATE canvas.courses SET workflow_state = 'completed' WHERE id = $1`, [m[1]]);
      } else {
        await this.pool.query('DELETE FROM canvas.courses WHERE id = $1', [m[1]]);
      }
      return {};
    }

    console.error(`[PgCanvasRouter] Unmatched DELETE: ${path}`);
    return {};
  }

  // ---- DB Helpers ----

  private async insertRow(table: string, data: any): Promise<any> {
    const cleanData = { ...data };
    delete cleanData.id; // let SERIAL handle it

    // Handle JSONB fields
    const keys = Object.keys(cleanData);
    if (keys.length === 0) {
      const res = await this.pool.query(`INSERT INTO ${table} DEFAULT VALUES RETURNING *`);
      return res.rows[0];
    }

    const columns = keys.map(k => this.quoteIdent(k)).join(', ');
    const placeholders = keys.map((_, i) => `$${i + 1}`).join(', ');
    const values = keys.map(k => {
      const v = cleanData[k];
      if (v !== null && v !== undefined && typeof v === 'object') return JSON.stringify(v);
      return v;
    });

    const query = `INSERT INTO ${table} (${columns}) VALUES (${placeholders}) RETURNING *`;
    const res = await this.pool.query(query, values);
    return res.rows[0];
  }

  private async updateRow(table: string, idCol: string, idVal: any, data: any): Promise<any> {
    const cleanData = { ...data };
    delete cleanData.id;
    delete cleanData[idCol];

    const keys = Object.keys(cleanData);
    if (keys.length === 0) {
      const res = await this.pool.query(`SELECT * FROM ${table} WHERE ${this.quoteIdent(idCol)} = $1`, [idVal]);
      return res.rows[0] || {};
    }

    const setClauses = keys.map((k, i) => `${this.quoteIdent(k)} = $${i + 1}`);
    const values: any[] = keys.map(k => {
      const v = cleanData[k];
      if (v !== null && v !== undefined && typeof v === 'object') return JSON.stringify(v);
      return v;
    });
    values.push(idVal);

    const query = `UPDATE ${table} SET ${setClauses.join(', ')} WHERE ${this.quoteIdent(idCol)} = $${values.length} RETURNING *`;
    const res = await this.pool.query(query, values);
    return res.rows[0] || {};
  }

  private quoteIdent(name: string): string {
    const reserved = ['order', 'key', 'group', 'type', 'index', 'user'];
    if (reserved.includes(name.toLowerCase())) {
      return `"${name}"`;
    }
    return name;
  }
}
