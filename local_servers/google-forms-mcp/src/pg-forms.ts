import pg from 'pg';
const { Pool } = pg;

export interface PgFormsConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
}

const defaultConfig: PgFormsConfig = {
  host: process.env.PG_HOST || 'localhost',
  port: parseInt(process.env.PG_PORT || '5432'),
  database: process.env.PG_DATABASE || 'toolathlon',
  user: process.env.PG_USER || 'postgres',
  password: process.env.PG_PASSWORD || 'postgres',
};

const pool = new Pool(defaultConfig);

/**
 * Create a new form in the gform.forms table.
 * Returns data shaped like the Google Forms API create response.
 */
export async function createForm(title: string, description?: string) {
  const result = await pool.query(
    `INSERT INTO gform.forms (title, document_title, description)
     VALUES ($1, $2, $3)
     RETURNING id, title, description, responder_uri`,
    [title, title, description || null]
  );
  const row = result.rows[0];
  const formId = row.id;
  const responderUri = row.responder_uri || `https://docs.google.com/forms/d/${formId}/viewform`;
  return { formId, title, description: description || '', responderUri };
}

/**
 * Add a text question to a form.
 * Inserts into gform.questions with question_type = 'textQuestion'.
 */
export async function addTextQuestion(formId: string, questionTitle: string, required: boolean = false) {
  const posResult = await pool.query(
    `SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM gform.questions WHERE form_id = $1`,
    [formId]
  );
  const nextPos = posResult.rows[0].next_pos;
  await pool.query(
    `INSERT INTO gform.questions (form_id, title, question_type, required, config, position)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [formId, questionTitle, 'textQuestion', required, '{}', nextPos]
  );
  return { success: true, message: 'Text question added successfully', questionTitle, required };
}

/**
 * Add a multiple choice question to a form.
 * Inserts into gform.questions with question_type = 'choiceQuestion'.
 * The options are stored in the config JSONB column.
 */
export async function addMultipleChoiceQuestion(
  formId: string,
  questionTitle: string,
  options: string[],
  required: boolean = false
) {
  const config = {
    type: 'RADIO',
    options: options.map((option: string) => ({ value: option })),
  };
  const posResult = await pool.query(
    `SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM gform.questions WHERE form_id = $1`,
    [formId]
  );
  const nextPos = posResult.rows[0].next_pos;
  await pool.query(
    `INSERT INTO gform.questions (form_id, title, question_type, required, config, position)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [formId, questionTitle, 'choiceQuestion', required, JSON.stringify(config), nextPos]
  );
  return { success: true, message: 'Multiple choice question added successfully', questionTitle, options, required };
}

/**
 * Get form details including all questions.
 * Returns data shaped like the Google Forms API get response:
 *   { formId, info: { title, documentTitle, description }, items: [...], responderUri, revisionId }
 */
export async function getForm(formId: string) {
  const formResult = await pool.query(
    `SELECT id, title, document_title, description, responder_uri, revision_id
     FROM gform.forms WHERE id = $1`,
    [formId]
  );
  if (formResult.rows.length === 0) {
    throw new Error(`Form not found: ${formId}`);
  }
  const form = formResult.rows[0];

  const questionsResult = await pool.query(
    `SELECT id, item_id, title, description, question_type, required, config
     FROM gform.questions WHERE form_id = $1 ORDER BY position ASC`,
    [formId]
  );

  const items = questionsResult.rows.map((q: any) => {
    const questionData: any = {
      questionId: q.id,
      required: q.required,
    };
    if (q.question_type === 'textQuestion') {
      questionData.textQuestion = {};
    } else if (q.question_type === 'choiceQuestion') {
      questionData.choiceQuestion = q.config;
    }
    return {
      itemId: q.item_id,
      title: q.title,
      questionItem: {
        question: questionData,
      },
    };
  });

  return {
    formId: form.id,
    info: {
      title: form.title,
      documentTitle: form.document_title,
      description: form.description || '',
    },
    items,
    responderUri: form.responder_uri || `https://docs.google.com/forms/d/${form.id}/viewform`,
    revisionId: form.revision_id,
  };
}

/**
 * Get all responses for a form.
 * Returns data shaped like the Google Forms API responses.list response:
 *   { responses: [...], nextPageToken: null }
 */
export async function getFormResponses(formId: string) {
  const result = await pool.query(
    `SELECT id AS "responseId", respondent_email AS "respondentEmail",
            create_time AS "createTime", last_submitted_time AS "lastSubmittedTime",
            answers
     FROM gform.responses WHERE form_id = $1
     ORDER BY create_time ASC`,
    [formId]
  );
  return {
    responses: result.rows,
    nextPageToken: null,
  };
}

/**
 * Close the connection pool. Call on shutdown.
 */
export async function closePool() {
  await pool.end();
}
