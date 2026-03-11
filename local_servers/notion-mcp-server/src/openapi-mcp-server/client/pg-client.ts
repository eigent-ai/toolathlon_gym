import type { OpenAPIV3, OpenAPIV3_1 } from 'openapi-types'
import pg from 'pg'
import crypto from 'crypto'
import { Headers } from './polyfill-headers.js'

const { Pool } = pg

export type HttpClientConfig = {
  baseUrl: string
  headers?: Record<string, string>
}

export type HttpClientResponse<T = any> = {
  data: T
  status: number
  headers: Headers
}

export class PgHttpClient {
  private pool: InstanceType<typeof Pool>

  constructor(
    _config: HttpClientConfig,
    _openApiSpec: OpenAPIV3.Document | OpenAPIV3_1.Document,
  ) {
    this.pool = new Pool({
      host: process.env.PG_HOST || 'localhost',
      port: parseInt(process.env.PG_PORT || '5432', 10),
      database: process.env.PG_DATABASE || 'toolathlon',
      user: process.env.PG_USER || 'postgres',
      password: process.env.PG_PASSWORD || 'postgres',
    })
  }

  private makeResponse<T>(data: T, status = 200): HttpClientResponse<T> {
    return { data, status, headers: new Headers() }
  }

  private wrapList(results: any[]): any {
    return {
      object: 'list',
      results,
      has_more: false,
      next_cursor: null,
    }
  }

  private formatBlock(row: any): any {
    if (!row) return row
    const { block_data, parent_type, parent_id, position, ...rest } = row
    const blockData = block_data || {}
    return {
      ...rest,
      parent: { type: parent_type, [parent_type]: parent_id },
      has_children: rest.has_children ?? false,
      ...blockData,
      [rest.type]: blockData[rest.type] ?? blockData,
    }
  }

  private nowISO(): string {
    return new Date().toISOString()
  }

  async executeOperation<T = any>(
    operation: OpenAPIV3.OperationObject & { method: string; path: string },
    params: Record<string, any> = {},
  ): Promise<HttpClientResponse<T>> {
    const operationId = operation.operationId
    if (!operationId) {
      throw new Error('Operation ID is required')
    }

    switch (operationId) {
      case 'get-self':
        return this.getSelf()
      case 'get-user':
        return this.getUser(params)
      case 'get-users':
        return this.getUsers()
      case 'retrieve-a-database':
        return this.retrieveDatabase(params)
      case 'create-a-database':
        return this.createDatabase(params)
      case 'update-a-database':
        return this.updateDatabase(params)
      case 'post-database-query':
        return this.queryDatabase(params)
      case 'retrieve-a-page':
        return this.retrievePage(params)
      case 'patch-page':
        return this.patchPage(params)
      case 'post-page':
        return this.createPage(params)
      case 'retrieve-a-page-property':
        return this.retrievePageProperty(params)
      case 'retrieve-a-block':
        return this.retrieveBlock(params)
      case 'update-a-block':
        return this.updateBlock(params)
      case 'delete-a-block':
        return this.deleteBlock(params)
      case 'get-block-children':
        return this.getBlockChildren(params)
      case 'patch-block-children':
        return this.patchBlockChildren(params)
      case 'post-search':
        return this.postSearch(params)
      case 'retrieve-a-comment':
        return this.retrieveComments(params)
      case 'create-a-comment':
        return this.createComment(params)
      default:
        throw new Error(`Unknown operation: ${operationId}`)
    }
  }

  // 1. get-self
  private async getSelf(): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.users WHERE type = 'bot' LIMIT 1`,
    )
    if (rows.length === 0) {
      const fallback = await this.pool.query(
        `SELECT * FROM notion.users LIMIT 1`,
      )
      return this.makeResponse(fallback.rows[0] || null)
    }
    return this.makeResponse(rows[0])
  }

  // 2. get-user
  private async getUser(params: Record<string, any>): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.users WHERE id = $1`,
      [params.user_id],
    )
    return this.makeResponse(rows[0] || null)
  }

  // 3. get-users
  private async getUsers(): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(`SELECT * FROM notion.users`)
    return this.makeResponse(this.wrapList(rows))
  }

  // 4. retrieve-a-database
  private async retrieveDatabase(params: Record<string, any>): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.databases WHERE id = $1`,
      [params.database_id],
    )
    return this.makeResponse(rows[0] || null)
  }

  // 5. create-a-database
  private async createDatabase(params: Record<string, any>): Promise<HttpClientResponse> {
    const id = crypto.randomUUID()
    const now = this.nowISO()
    const {
      title = [],
      description = [],
      icon = null,
      cover = null,
      properties = {},
      parent = {},
      is_inline = false,
    } = params

    const { rows } = await this.pool.query(
      `INSERT INTO notion.databases
        (id, object, created_time, last_edited_time, title, description, icon, cover, properties, parent, is_inline, archived)
       VALUES ($1, 'database', $2, $3, $4, $5, $6, $7, $8, $9, $10, false)
       RETURNING *`,
      [id, now, now, JSON.stringify(title), JSON.stringify(description), JSON.stringify(icon), JSON.stringify(cover), JSON.stringify(properties), JSON.stringify(parent), is_inline],
    )
    return this.makeResponse(rows[0])
  }

  // 6. update-a-database
  private async updateDatabase(params: Record<string, any>): Promise<HttpClientResponse> {
    const { database_id, ...body } = params
    const setClauses: string[] = []
    const values: any[] = []
    let idx = 1

    const allowedFields = ['title', 'description', 'icon', 'cover', 'properties', 'archived', 'is_inline']
    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        const isJsonField = ['title', 'description', 'icon', 'cover', 'properties'].includes(field)
        setClauses.push(`${field} = $${idx}`)
        values.push(isJsonField ? JSON.stringify(body[field]) : body[field])
        idx++
      }
    }

    setClauses.push(`last_edited_time = $${idx}`)
    values.push(this.nowISO())
    idx++

    values.push(database_id)

    const { rows } = await this.pool.query(
      `UPDATE notion.databases SET ${setClauses.join(', ')} WHERE id = $${idx} RETURNING *`,
      values,
    )
    return this.makeResponse(rows[0] || null)
  }

  // 7. post-database-query
  private async queryDatabase(params: Record<string, any>): Promise<HttpClientResponse> {
    const { database_id, filter, sorts } = params
    let query = `SELECT * FROM notion.pages WHERE parent->>'database_id' = $1`
    const values: any[] = [database_id]
    let idx = 2

    // Apply basic filter support
    if (filter && filter.property && filter.property !== 'and' && filter.property !== 'or') {
      const propName = filter.property
      // Determine the filter type (e.g., rich_text, title, number, checkbox, select, etc.)
      const filterTypes = ['rich_text', 'title', 'number', 'checkbox', 'select', 'multi_select', 'date', 'url', 'email', 'phone_number', 'status']
      for (const ft of filterTypes) {
        if (filter[ft]) {
          const condition = filter[ft]
          if (condition.equals !== undefined) {
            query += ` AND properties->'${propName}'->'${ft}'->>'content' = $${idx}`
            values.push(String(condition.equals))
            idx++
          } else if (condition.contains !== undefined) {
            query += ` AND properties->'${propName}'->'${ft}'->>'content' ILIKE $${idx}`
            values.push(`%${condition.contains}%`)
            idx++
          } else if (condition.starts_with !== undefined) {
            query += ` AND properties->'${propName}'->'${ft}'->>'content' ILIKE $${idx}`
            values.push(`${condition.starts_with}%`)
            idx++
          }
          break
        }
      }
    }

    // Apply sorts
    if (sorts && Array.isArray(sorts) && sorts.length > 0) {
      const orderClauses: string[] = []
      for (const sort of sorts) {
        const dir = sort.direction === 'descending' ? 'DESC' : 'ASC'
        if (sort.property) {
          orderClauses.push(`properties->'${sort.property}' ${dir}`)
        } else if (sort.timestamp) {
          orderClauses.push(`${sort.timestamp} ${dir}`)
        }
      }
      if (orderClauses.length > 0) {
        query += ` ORDER BY ${orderClauses.join(', ')}`
      }
    }

    const { rows } = await this.pool.query(query, values)
    return this.makeResponse(this.wrapList(rows))
  }

  // 8. retrieve-a-page
  private async retrievePage(params: Record<string, any>): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.pages WHERE id = $1`,
      [params.page_id],
    )
    return this.makeResponse(rows[0] || null)
  }

  // 9. patch-page
  private async patchPage(params: Record<string, any>): Promise<HttpClientResponse> {
    const { page_id, ...body } = params
    const setClauses: string[] = []
    const values: any[] = []
    let idx = 1

    const allowedFields = ['properties', 'icon', 'cover', 'archived', 'in_trash']
    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        const isJsonField = ['properties', 'icon', 'cover'].includes(field)
        setClauses.push(`${field} = $${idx}`)
        values.push(isJsonField ? JSON.stringify(body[field]) : body[field])
        idx++
      }
    }

    setClauses.push(`last_edited_time = $${idx}`)
    values.push(this.nowISO())
    idx++

    values.push(page_id)

    const { rows } = await this.pool.query(
      `UPDATE notion.pages SET ${setClauses.join(', ')} WHERE id = $${idx} RETURNING *`,
      values,
    )
    return this.makeResponse(rows[0] || null)
  }

  // 10. post-page (create page)
  private async createPage(params: Record<string, any>): Promise<HttpClientResponse> {
    const id = crypto.randomUUID()
    const now = this.nowISO()
    const {
      parent = {},
      properties = {},
      icon = null,
      cover = null,
      children,
    } = params

    const { rows } = await this.pool.query(
      `INSERT INTO notion.pages
        (id, object, created_time, last_edited_time, parent, properties, icon, cover, archived, in_trash)
       VALUES ($1, 'page', $2, $3, $4, $5, $6, $7, false, false)
       RETURNING *`,
      [id, now, now, JSON.stringify(parent), JSON.stringify(properties), JSON.stringify(icon), JSON.stringify(cover)],
    )

    // If children blocks are provided, insert them
    if (children && Array.isArray(children)) {
      await this.insertBlocks(id, 'page_id', children)
    }

    return this.makeResponse(rows[0])
  }

  // 11. retrieve-a-page-property
  private async retrievePageProperty(params: Record<string, any>): Promise<HttpClientResponse> {
    const { page_id, property_id } = params
    const { rows } = await this.pool.query(
      `SELECT properties FROM notion.pages WHERE id = $1`,
      [page_id],
    )
    if (rows.length === 0) {
      return this.makeResponse(null, 404)
    }
    const properties = rows[0].properties || {}
    // property_id could be the property name or an actual id
    const value = properties[property_id] ?? null
    return this.makeResponse(value)
  }

  // 12. retrieve-a-block
  private async retrieveBlock(params: Record<string, any>): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.blocks WHERE id = $1`,
      [params.block_id],
    )
    if (rows.length === 0) {
      return this.makeResponse(null, 404)
    }
    return this.makeResponse(this.formatBlock(rows[0]))
  }

  // 13. update-a-block
  private async updateBlock(params: Record<string, any>): Promise<HttpClientResponse> {
    const { block_id, ...body } = params
    const setClauses: string[] = []
    const values: any[] = []
    let idx = 1

    // Handle type-specific block data updates
    const metaFields = ['type', 'archived', 'has_children']
    const blockDataUpdates: Record<string, any> = {}

    for (const [key, value] of Object.entries(body)) {
      if (metaFields.includes(key)) {
        if (key === 'archived' || key === 'has_children') {
          setClauses.push(`${key} = $${idx}`)
          values.push(value)
          idx++
        } else if (key === 'type') {
          setClauses.push(`type = $${idx}`)
          values.push(value)
          idx++
        }
      } else {
        // Assume it's block_data content (e.g., paragraph, heading_1, etc.)
        blockDataUpdates[key] = value
      }
    }

    if (Object.keys(blockDataUpdates).length > 0) {
      setClauses.push(`block_data = block_data || $${idx}::jsonb`)
      values.push(JSON.stringify(blockDataUpdates))
      idx++
    }

    setClauses.push(`last_edited_time = $${idx}`)
    values.push(this.nowISO())
    idx++

    values.push(block_id)

    const { rows } = await this.pool.query(
      `UPDATE notion.blocks SET ${setClauses.join(', ')} WHERE id = $${idx} RETURNING *`,
      values,
    )
    if (rows.length === 0) {
      return this.makeResponse(null, 404)
    }
    return this.makeResponse(this.formatBlock(rows[0]))
  }

  // 14. delete-a-block
  private async deleteBlock(params: Record<string, any>): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(
      `UPDATE notion.blocks SET archived = true, in_trash = true, last_edited_time = $1 WHERE id = $2 RETURNING *`,
      [this.nowISO(), params.block_id],
    )
    if (rows.length === 0) {
      return this.makeResponse(null, 404)
    }
    return this.makeResponse(this.formatBlock(rows[0]))
  }

  // 15. get-block-children
  private async getBlockChildren(params: Record<string, any>): Promise<HttpClientResponse> {
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.blocks WHERE parent_id = $1 ORDER BY position ASC`,
      [params.block_id],
    )
    const formatted = rows.map((r: any) => this.formatBlock(r))
    return this.makeResponse(this.wrapList(formatted))
  }

  // 16. patch-block-children
  private async patchBlockChildren(params: Record<string, any>): Promise<HttpClientResponse> {
    const { block_id, children } = params
    if (children && Array.isArray(children)) {
      await this.insertBlocks(block_id, 'block_id', children)
    }

    // Update parent's has_children flag
    await this.pool.query(
      `UPDATE notion.blocks SET has_children = true WHERE id = $1`,
      [block_id],
    )

    // Return the children
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.blocks WHERE parent_id = $1 ORDER BY position ASC`,
      [block_id],
    )
    const formatted = rows.map((r: any) => this.formatBlock(r))
    return this.makeResponse(this.wrapList(formatted))
  }

  // 17. post-search
  private async postSearch(params: Record<string, any>): Promise<HttpClientResponse> {
    const { query, filter, sort } = params
    const results: any[] = []

    const shouldSearchPages = !filter || !filter.value || filter.value === 'page'
    const shouldSearchDatabases = !filter || !filter.value || filter.value === 'database'

    if (shouldSearchPages) {
      let pageQuery = `SELECT * FROM notion.pages WHERE archived = false`
      const pageValues: any[] = []
      let idx = 1

      if (query) {
        pageQuery += ` AND properties::text ILIKE $${idx}`
        pageValues.push(`%${query}%`)
        idx++
      }

      const { rows: pageRows } = await this.pool.query(pageQuery, pageValues)
      results.push(...pageRows)
    }

    if (shouldSearchDatabases) {
      let dbQuery = `SELECT * FROM notion.databases WHERE archived = false`
      const dbValues: any[] = []
      let idx = 1

      if (query) {
        dbQuery += ` AND title::text ILIKE $${idx}`
        dbValues.push(`%${query}%`)
        idx++
      }

      const { rows: dbRows } = await this.pool.query(dbQuery, dbValues)
      results.push(...dbRows)
    }

    // Apply sort if provided
    if (sort && sort.direction) {
      const dir = sort.direction === 'ascending' ? 1 : -1
      const field = sort.timestamp || 'last_edited_time'
      results.sort((a: any, b: any) => {
        const aVal = new Date(a[field] || 0).getTime()
        const bVal = new Date(b[field] || 0).getTime()
        return (aVal - bVal) * dir
      })
    }

    return this.makeResponse(this.wrapList(results))
  }

  // 18. retrieve-a-comment
  private async retrieveComments(params: Record<string, any>): Promise<HttpClientResponse> {
    const blockId = params.block_id
    const { rows } = await this.pool.query(
      `SELECT * FROM notion.comments
       WHERE parent->>'block_id' = $1
          OR parent->>'page_id' = $1
       ORDER BY created_time ASC`,
      [blockId],
    )
    return this.makeResponse(this.wrapList(rows))
  }

  // 19. create-a-comment
  private async createComment(params: Record<string, any>): Promise<HttpClientResponse> {
    const id = crypto.randomUUID()
    const now = this.nowISO()
    const {
      parent = {},
      discussion_id = null,
      rich_text = [],
    } = params

    const { rows } = await this.pool.query(
      `INSERT INTO notion.comments
        (id, object, parent, discussion_id, created_time, last_edited_time, rich_text)
       VALUES ($1, 'comment', $2, $3, $4, $5, $6)
       RETURNING *`,
      [id, JSON.stringify(parent), discussion_id, now, now, JSON.stringify(rich_text)],
    )
    return this.makeResponse(rows[0])
  }

  // Helper: insert child blocks
  private async insertBlocks(
    parentId: string,
    parentType: string,
    children: any[],
  ): Promise<void> {
    // Get current max position for this parent
    const { rows: posRows } = await this.pool.query(
      `SELECT COALESCE(MAX(position), -1) AS max_pos FROM notion.blocks WHERE parent_id = $1`,
      [parentId],
    )
    let position = (posRows[0]?.max_pos ?? -1) + 1

    for (const child of children) {
      const id = crypto.randomUUID()
      const now = this.nowISO()
      const blockType = child.type || 'paragraph'
      const hasChildren = !!(child.children && child.children.length > 0)

      // Extract block data: everything except meta fields
      const { type, children: childChildren, object, ...blockData } = child

      await this.pool.query(
        `INSERT INTO notion.blocks
          (id, object, parent_type, parent_id, created_time, last_edited_time, type, has_children, archived, in_trash, block_data, position)
         VALUES ($1, 'block', $2, $3, $4, $5, $6, $7, false, false, $8, $9)`,
        [id, parentType, parentId, now, now, blockType, hasChildren, JSON.stringify(blockData), position],
      )

      position++

      // Recursively insert nested children
      if (childChildren && Array.isArray(childChildren) && childChildren.length > 0) {
        await this.insertBlocks(id, 'block_id', childChildren)
      }
    }
  }
}
