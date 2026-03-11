import pg from 'pg';
const { Pool } = pg;

const RESOURCE_MAP: Record<string, {table: string, idColumn?: string}> = {
  'orders': {table: 'wc.orders'},
  'products': {table: 'wc.products'},
  'customers': {table: 'wc.customers'},
  'coupons': {table: 'wc.coupons'},
  'taxes': {table: 'wc.tax_rates'},
  'taxes/classes': {table: 'wc.tax_classes', idColumn: 'slug'},
  'products/categories': {table: 'wc.product_categories'},
  'products/tags': {table: 'wc.product_tags'},
  'products/attributes': {table: 'wc.product_attributes'},
  'products/reviews': {table: 'wc.product_reviews'},
  'shipping/zones': {table: 'wc.shipping_zones'},
  'shipping_methods': {table: 'wc.shipping_methods', idColumn: 'id'},
  'payment_gateways': {table: 'wc.payment_gateways', idColumn: 'id'},
  'webhooks': {table: 'wc.webhooks'},
  'settings': {table: 'wc.settings'},
  'system_status': {table: 'wc.system_status'},
};

const NESTED_RESOURCE_MAP: Record<string, {table: string | null, parentKey: string}> = {
  'orders/*/notes': {table: 'wc.order_notes', parentKey: 'order_id'},
  'orders/*/refunds': {table: 'wc.refunds', parentKey: 'order_id'},
  'products/*/variations': {table: 'wc.product_variations', parentKey: 'product_id'},
  'shipping/zones/*/methods': {table: 'wc.shipping_zone_methods', parentKey: 'zone_id'},
  'shipping/zones/*/locations': {table: 'wc.shipping_zone_locations', parentKey: 'zone_id'},
  'customers/*/downloads': {table: null, parentKey: 'customer_id'},
};

function makeResponse(data: any, status = 200) {
  return { data, status, statusText: 'OK', headers: {}, config: {} };
}

function stripLeadingSlash(url: string): string {
  return url.replace(/^\/+/, '');
}

export class PgRestRouter {
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

    // Data endpoints
    if (path === 'data' || path === 'data/continents' || path === 'data/countries' || path === 'data/currencies') {
      return makeResponse(this.getStaticData(path));
    }

    // Reports
    if (path.startsWith('reports')) {
      return this.handleReport(path, params);
    }

    // Settings: /settings, /settings/:group, /settings/:group/:option
    const settingsMatch = path.match(/^settings(?:\/([^/]+))?(?:\/([^/]+))?$/);
    if (settingsMatch) {
      return this.handleSettingsGet(settingsMatch[1], settingsMatch[2]);
    }

    // System status
    if (path === 'system_status') {
      const result = await this.pool.query('SELECT key, data FROM wc.system_status');
      const statusObj: any = {};
      for (const row of result.rows) {
        statusObj[row.key] = row.data;
      }
      return makeResponse(statusObj);
    }
    if (path === 'system_status/tools') {
      const result = await this.pool.query(`SELECT data FROM wc.system_status WHERE key = 'tools'`);
      return makeResponse(result.rows[0]?.data || []);
    }
    const sysToolMatch = path.match(/^system_status\/tools\/(.+)$/);
    if (sysToolMatch) {
      const result = await this.pool.query(`SELECT data FROM wc.system_status WHERE key = 'tools'`);
      const tools = result.rows[0]?.data || [];
      const tool = Array.isArray(tools) ? tools.find((t: any) => t.id === sysToolMatch[1]) : null;
      return makeResponse(tool || { id: sysToolMatch[1], name: sysToolMatch[1] });
    }

    // Data currencies/current
    if (path === 'data/currencies/current') {
      return makeResponse({ code: 'USD', name: 'United States dollar', symbol: '$' });
    }

    // Check nested resources first
    const nestedResult = this.matchNestedResource(path);
    if (nestedResult) {
      const { pattern, parentId, childId } = nestedResult;
      const nested = NESTED_RESOURCE_MAP[pattern];
      if (!nested.table) {
        return makeResponse([]);
      }
      if (childId) {
        const res = await this.pool.query(
          `SELECT * FROM ${nested.table} WHERE id = $1 AND ${nested.parentKey} = $2`,
          [childId, parentId]
        );
        return makeResponse(res.rows[0] || null);
      }
      const { query, values } = this.buildListQuery(nested.table, params, nested.parentKey, parentId);
      const res = await this.pool.query(query, values);
      return makeResponse(res.rows);
    }

    // Top-level resources
    const resourceResult = this.matchResource(path);
    if (resourceResult) {
      const { resourceKey, resourceId } = resourceResult;
      const resource = RESOURCE_MAP[resourceKey];
      const idCol = resource.idColumn || 'id';

      if (resourceId !== undefined) {
        const res = await this.pool.query(
          `SELECT * FROM ${resource.table} WHERE ${this.quoteIdent(idCol)} = $1`,
          [resourceId]
        );
        return makeResponse(res.rows[0] || null);
      }

      const { query, values } = this.buildListQuery(resource.table, params);
      const res = await this.pool.query(query, values);
      return makeResponse(res.rows);
    }

    return makeResponse([]);
  }

  async post(url: string, data?: any, config?: any): Promise<any> {
    const path = stripLeadingSlash(url);
    const body = data || config?.data || {};

    // Batch operations
    const batchMatch = path.match(/^(.+)\/batch$/);
    if (batchMatch) {
      return this.handleBatch(batchMatch[1], body);
    }

    // Nested resource POST
    const nestedResult = this.matchNestedResource(path);
    if (nestedResult) {
      const { pattern, parentId } = nestedResult;
      const nested = NESTED_RESOURCE_MAP[pattern];
      if (!nested.table) return makeResponse({});
      const insertData = { ...body, [nested.parentKey]: parentId };
      const row = await this.insertRow(nested.table, insertData);
      return makeResponse(row, 201);
    }

    // Top-level resource POST
    const resourceResult = this.matchResource(path);
    if (resourceResult && resourceResult.resourceId === undefined) {
      const resource = RESOURCE_MAP[resourceResult.resourceKey];
      const row = await this.insertRow(resource.table, body);
      return makeResponse(row, 201);
    }

    return makeResponse({}, 201);
  }

  async put(url: string, data?: any, config?: any): Promise<any> {
    const path = stripLeadingSlash(url);
    const body = data || config?.data || {};

    // Nested resource PUT
    const nestedResult = this.matchNestedResource(path);
    if (nestedResult) {
      const { pattern, parentId, childId } = nestedResult;
      const nested = NESTED_RESOURCE_MAP[pattern];
      if (!nested.table) return makeResponse({});
      if (childId) {
        const row = await this.updateRow(nested.table, 'id', childId, body, nested.parentKey, parentId);
        return makeResponse(row);
      }
      // PUT without childId (e.g., PUT /shipping/zones/:id/locations replaces all)
      if (Array.isArray(body)) {
        await this.pool.query(`DELETE FROM ${nested.table} WHERE ${nested.parentKey} = $1`, [parentId]);
        const results = [];
        for (const item of body) {
          const row = await this.insertRow(nested.table, { ...item, [nested.parentKey]: parentId });
          results.push(row);
        }
        return makeResponse(results);
      }
      // Single object update by parentKey
      const res = await this.pool.query(
        `UPDATE ${nested.table} SET date_modified = NOW() WHERE ${nested.parentKey} = $1 RETURNING *`,
        [parentId]
      );
      return makeResponse(res.rows);
    }

    // Top-level resource PUT
    const resourceResult = this.matchResource(path);
    if (resourceResult && resourceResult.resourceId !== undefined) {
      const resource = RESOURCE_MAP[resourceResult.resourceKey];
      const idCol = resource.idColumn || 'id';
      const row = await this.updateRow(resource.table, idCol, resourceResult.resourceId, body);
      return makeResponse(row);
    }

    // System status tools: PUT /system_status/tools/:id
    const sysToolMatch = path.match(/^system_status\/tools\/(.+)$/);
    if (sysToolMatch) {
      return makeResponse({ id: sysToolMatch[1], name: sysToolMatch[1], success: true });
    }

    // Settings update: PUT /settings/:group/:option
    const settingsMatch = path.match(/^settings\/([^/]+)\/([^/]+)$/);
    if (settingsMatch) {
      return this.handleSettingsUpdate(settingsMatch[1], settingsMatch[2], body);
    }

    return makeResponse({});
  }

  async delete(url: string, config?: any): Promise<any> {
    const path = stripLeadingSlash(url);

    // Nested resource DELETE
    const nestedResult = this.matchNestedResource(path);
    if (nestedResult && nestedResult.childId) {
      const { pattern, parentId, childId } = nestedResult;
      const nested = NESTED_RESOURCE_MAP[pattern];
      if (!nested.table) return makeResponse({});
      const res = await this.pool.query(
        `DELETE FROM ${nested.table} WHERE id = $1 AND ${nested.parentKey} = $2 RETURNING *`,
        [childId, parentId]
      );
      return makeResponse(res.rows[0] || {});
    }

    // Top-level resource DELETE
    const resourceResult = this.matchResource(path);
    if (resourceResult && resourceResult.resourceId !== undefined) {
      const resource = RESOURCE_MAP[resourceResult.resourceKey];
      const idCol = resource.idColumn || 'id';
      const res = await this.pool.query(
        `DELETE FROM ${resource.table} WHERE ${this.quoteIdent(idCol)} = $1 RETURNING *`,
        [resourceResult.resourceId]
      );
      return makeResponse(res.rows[0] || {});
    }

    return makeResponse({});
  }

  // --- Helpers ---

  private matchResource(path: string): {resourceKey: string, resourceId?: string} | null {
    // Try matching from longest resource keys to shortest
    const sortedKeys = Object.keys(RESOURCE_MAP).sort((a, b) => b.length - a.length);
    for (const key of sortedKeys) {
      // Exact match: /resource
      if (path === key) {
        return { resourceKey: key };
      }
      // With ID: /resource/:id
      const prefix = key + '/';
      if (path.startsWith(prefix)) {
        const rest = path.slice(prefix.length);
        // Make sure there's no further slash (that would be a nested resource)
        if (!rest.includes('/')) {
          return { resourceKey: key, resourceId: rest };
        }
      }
    }
    return null;
  }

  private matchNestedResource(path: string): {pattern: string, parentId: string, childId?: string} | null {
    for (const pattern of Object.keys(NESTED_RESOURCE_MAP)) {
      // Pattern like "orders/*/notes" → regex "^orders/([^/]+)/notes(?:/([^/]+))?$"
      const regexStr = '^' + pattern.replace('*', '([^/]+)') + '(?:/([^/]+))?$';
      const regex = new RegExp(regexStr);
      const match = path.match(regex);
      if (match) {
        return {
          pattern,
          parentId: match[1],
          childId: match[2],
        };
      }
    }
    return null;
  }

  private buildListQuery(table: string, params: any, parentKey?: string, parentId?: string): {query: string, values: any[]} {
    const conditions: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (parentKey && parentId) {
      conditions.push(`${parentKey} = $${paramIndex}`);
      values.push(parentId);
      paramIndex++;
    }

    // Filter by common WooCommerce query params
    const filterFields = ['status', 'customer_id', 'product_id', 'slug', 'code', 'sku', 'email', 'class', 'type'];
    for (const field of filterFields) {
      // Skip undefined and empty-string values so that an unset optional
      // parameter (passed as "") does not produce a spurious WHERE clause.
      if (params[field] !== undefined && params[field] !== null && params[field] !== '') {
        conditions.push(`${this.quoteIdent(field)} = $${paramIndex}`);
        values.push(params[field]);
        paramIndex++;
      }
    }

    // Search
    if (params.search) {
      conditions.push(`(name ILIKE $${paramIndex} OR slug ILIKE $${paramIndex})`);
      values.push(`%${params.search}%`);
      paramIndex++;
    }

    // Date filters
    if (params.after) {
      conditions.push(`date_created >= $${paramIndex}`);
      values.push(params.after);
      paramIndex++;
    }
    if (params.before) {
      conditions.push(`date_created <= $${paramIndex}`);
      values.push(params.before);
      paramIndex++;
    }

    // Category filter (JSONB)
    if (params.category) {
      conditions.push(`categories @> $${paramIndex}::jsonb`);
      values.push(JSON.stringify([{ id: parseInt(params.category) }]));
      paramIndex++;
    }

    // Tag filter (JSONB)
    if (params.tag) {
      conditions.push(`tags @> $${paramIndex}::jsonb`);
      values.push(JSON.stringify([{ id: parseInt(params.tag) }]));
      paramIndex++;
    }

    const whereClause = conditions.length > 0 ? ' WHERE ' + conditions.join(' AND ') : '';

    // Ordering
    const orderBy = params.orderby || 'id';
    const order = params.order === 'asc' ? 'ASC' : 'DESC';
    const orderClause = ` ORDER BY ${this.quoteIdent(orderBy)} ${order}`;

    // Pagination
    const perPage = parseInt(params.per_page) || 10;
    const page = parseInt(params.page) || 1;
    const offset = (page - 1) * perPage;
    const limitClause = ` LIMIT ${perPage} OFFSET ${offset}`;

    const query = `SELECT * FROM ${table}${whereClause}${orderClause}${limitClause}`;
    return { query, values };
  }

  private async insertRow(table: string, data: any): Promise<any> {
    const cleanData = { ...data };
    // Remove id if it's auto-generated (SERIAL)
    if (cleanData.id === undefined || cleanData.id === null) {
      delete cleanData.id;
    }
    // Set timestamps
    if (!cleanData.date_created) {
      cleanData.date_created = new Date().toISOString();
    }
    if (!cleanData.date_modified) {
      cleanData.date_modified = new Date().toISOString();
    }

    const keys = Object.keys(cleanData);
    if (keys.length === 0) {
      const res = await this.pool.query(`INSERT INTO ${table} DEFAULT VALUES RETURNING *`);
      return res.rows[0];
    }

    const columns = keys.map(k => this.quoteIdent(k)).join(', ');
    const placeholders = keys.map((_, i) => `$${i + 1}`).join(', ');
    const values = keys.map(k => {
      const v = cleanData[k];
      if (v !== null && typeof v === 'object') return JSON.stringify(v);
      return v;
    });

    const query = `INSERT INTO ${table} (${columns}) VALUES (${placeholders}) RETURNING *`;
    const res = await this.pool.query(query, values);
    return res.rows[0];
  }

  private async updateRow(table: string, idCol: string, idVal: string, data: any, parentKey?: string, parentId?: string): Promise<any> {
    const cleanData = { ...data };
    delete cleanData.id;
    delete cleanData[idCol];
    cleanData.date_modified = new Date().toISOString();

    const keys = Object.keys(cleanData);
    if (keys.length === 0) {
      const res = await this.pool.query(`SELECT * FROM ${table} WHERE ${this.quoteIdent(idCol)} = $1`, [idVal]);
      return res.rows[0];
    }

    const setClauses = keys.map((k, i) => `${this.quoteIdent(k)} = $${i + 1}`);
    const values: any[] = keys.map(k => {
      const v = cleanData[k];
      if (v !== null && typeof v === 'object') return JSON.stringify(v);
      return v;
    });

    let paramIdx = values.length + 1;
    let whereClause = `${this.quoteIdent(idCol)} = $${paramIdx}`;
    values.push(idVal);
    paramIdx++;

    if (parentKey && parentId) {
      whereClause += ` AND ${parentKey} = $${paramIdx}`;
      values.push(parentId);
    }

    const query = `UPDATE ${table} SET ${setClauses.join(', ')} WHERE ${whereClause} RETURNING *`;
    const res = await this.pool.query(query, values);
    return res.rows[0] || null;
  }

  private async handleBatch(resourcePath: string, body: any): Promise<any> {
    const resourceResult = this.matchResource(resourcePath);
    if (!resourceResult) return makeResponse({ create: [], update: [], delete: [] });

    const resource = RESOURCE_MAP[resourceResult.resourceKey];
    const idCol = resource.idColumn || 'id';
    const result: any = { create: [], update: [], delete: [] };

    if (body.create && Array.isArray(body.create)) {
      for (const item of body.create) {
        const row = await this.insertRow(resource.table, item);
        result.create.push(row);
      }
    }
    if (body.update && Array.isArray(body.update)) {
      for (const item of body.update) {
        const itemId = item[idCol] || item.id;
        if (itemId) {
          const row = await this.updateRow(resource.table, idCol, itemId, item);
          if (row) result.update.push(row);
        }
      }
    }
    if (body.delete && Array.isArray(body.delete)) {
      for (const id of body.delete) {
        const res = await this.pool.query(
          `DELETE FROM ${resource.table} WHERE ${this.quoteIdent(idCol)} = $1 RETURNING *`,
          [id]
        );
        if (res.rows[0]) result.delete.push(res.rows[0]);
      }
    }

    return makeResponse(result);
  }

  private async handleSettingsGet(groupId?: string, optionId?: string): Promise<any> {
    if (!groupId) {
      // List all settings groups
      const res = await this.pool.query('SELECT DISTINCT group_id, group_id AS id, group_id AS label FROM wc.settings ORDER BY group_id');
      return makeResponse(res.rows.map(r => ({ id: r.group_id, label: r.label || r.group_id })));
    }
    if (optionId) {
      // Get specific setting
      const res = await this.pool.query(
        'SELECT * FROM wc.settings WHERE group_id = $1 AND option_id = $2',
        [groupId, optionId]
      );
      return makeResponse(res.rows[0] || null);
    }
    // List settings in group
    const res = await this.pool.query(
      'SELECT * FROM wc.settings WHERE group_id = $1',
      [groupId]
    );
    return makeResponse(res.rows);
  }

  private async handleSettingsUpdate(groupId: string, optionId: string, body: any): Promise<any> {
    const value = body.value !== undefined ? body.value : null;
    const res = await this.pool.query(
      `UPDATE wc.settings SET value = $1 WHERE group_id = $2 AND option_id = $3 RETURNING *`,
      [value, groupId, optionId]
    );
    return makeResponse(res.rows[0] || null);
  }

  private async handleReport(path: string, params: any): Promise<any> {
    const reportPath = path.replace(/^reports\/?/, '');

    if (!reportPath || reportPath === '') {
      return makeResponse([
        { slug: 'sales', description: 'Sales report' },
        { slug: 'top_sellers', description: 'Top sellers report' },
        { slug: 'orders/totals', description: 'Orders totals' },
        { slug: 'products/totals', description: 'Products totals' },
        { slug: 'customers/totals', description: 'Customers totals' },
      ]);
    }

    if (reportPath === 'sales') {
      const res = await this.pool.query(`
        SELECT
          COALESCE(SUM(total), 0) as total_sales,
          COALESCE(SUM(total_tax), 0) as total_tax,
          COALESCE(SUM(shipping_total), 0) as total_shipping,
          COUNT(*) as total_orders
        FROM wc.orders
        WHERE status NOT IN ('cancelled', 'refunded', 'failed', 'trash')
      `);
      return makeResponse([res.rows[0]]);
    }

    if (reportPath === 'top_sellers') {
      const res = await this.pool.query(`
        SELECT id, name, total_sales
        FROM wc.products
        ORDER BY total_sales DESC
        LIMIT 10
      `);
      return makeResponse(res.rows);
    }

    if (reportPath === 'orders/totals') {
      const res = await this.pool.query(`
        SELECT status, COUNT(*) as total
        FROM wc.orders
        GROUP BY status
      `);
      return makeResponse(res.rows);
    }

    if (reportPath === 'products/totals') {
      const res = await this.pool.query(`
        SELECT status, COUNT(*) as total
        FROM wc.products
        GROUP BY status
      `);
      return makeResponse(res.rows);
    }

    if (reportPath === 'customers/totals') {
      const res = await this.pool.query(`SELECT COUNT(*) as total FROM wc.customers`);
      return makeResponse(res.rows);
    }

    return makeResponse([]);
  }

  private getStaticData(path: string): any {
    if (path === 'data') {
      return [
        { slug: 'continents', description: 'List of continents' },
        { slug: 'countries', description: 'List of countries' },
        { slug: 'currencies', description: 'List of currencies' },
      ];
    }
    if (path === 'data/continents') {
      return [
        { code: 'AF', name: 'Africa' },
        { code: 'AN', name: 'Antarctica' },
        { code: 'AS', name: 'Asia' },
        { code: 'EU', name: 'Europe' },
        { code: 'NA', name: 'North America' },
        { code: 'OC', name: 'Oceania' },
        { code: 'SA', name: 'South America' },
      ];
    }
    if (path === 'data/countries') {
      return [
        { code: 'US', name: 'United States' },
        { code: 'GB', name: 'United Kingdom' },
        { code: 'CA', name: 'Canada' },
        { code: 'AU', name: 'Australia' },
        { code: 'DE', name: 'Germany' },
        { code: 'FR', name: 'France' },
        { code: 'JP', name: 'Japan' },
        { code: 'CN', name: 'China' },
      ];
    }
    if (path === 'data/currencies') {
      return [
        { code: 'USD', name: 'United States dollar', symbol: '$' },
        { code: 'EUR', name: 'Euro', symbol: '\u20ac' },
        { code: 'GBP', name: 'Pound sterling', symbol: '\u00a3' },
        { code: 'JPY', name: 'Japanese yen', symbol: '\u00a5' },
        { code: 'CAD', name: 'Canadian dollar', symbol: '$' },
        { code: 'AUD', name: 'Australian dollar', symbol: '$' },
        { code: 'CNY', name: 'Chinese yuan', symbol: '\u00a5' },
      ];
    }
    return [];
  }

  private quoteIdent(name: string): string {
    // Quote reserved words
    const reserved = ['order', 'key', 'group', 'type', 'class'];
    if (reserved.includes(name.toLowerCase())) {
      return `"${name}"`;
    }
    return name;
  }
}
