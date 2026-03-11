// tests/client.test.ts

import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { CanvasClient } from '../src/client.js';
import { CanvasAPIError } from '../src/types.js';
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('CanvasClient', () => {
  let client: CanvasClient;
  const mockToken = 'test-token';
  const mockDomain = 'test.instructure.com';

  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    
    // Mock axios.create
    const mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    };
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);
    
    client = new CanvasClient(mockToken, mockDomain);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('constructor', () => {
    test('should create client with correct base URL', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: `https://${mockDomain}/api/v1`,
        headers: {
          'Authorization': `Bearer ${mockToken}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      });
    });

    test('should setup interceptors', () => {
      const mockInstance = mockedAxios.create.mock.results[0].value;
      expect(mockInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('healthCheck', () => {
    test('should return ok status when API is accessible', async () => {
      const mockProfile = { id: 1, name: 'Test User' };
      const mockInstance = mockedAxios.create.mock.results[0].value;
      mockInstance.get.mockResolvedValue({ data: mockProfile });

      const result = await client.healthCheck();

      expect(result.status).toBe('ok');
      expect(result.user).toEqual({ id: 1, name: 'Test User' });
      expect(result.timestamp).toBeDefined();
    });

    test('should return error status when API is not accessible', async () => {
      const mockInstance = mockedAxios.create.mock.results[0].value;
      mockInstance.get.mockRejectedValue(new Error('Network error'));

      const result = await client.healthCheck();

      expect(result.status).toBe('error');
      expect(result.timestamp).toBeDefined();
    });
  });

  describe('listCourses', () => {
    test('should fetch courses with default parameters', async () => {
      const mockCourses = [
        { id: 1, name: 'Course 1', course_code: 'CS101' },
        { id: 2, name: 'Course 2', course_code: 'CS102' }
      ];
      const mockInstance = mockedAxios.create.mock.results[0].value;
      mockInstance.get.mockResolvedValue({ data: mockCourses });

      const result = await client.listCourses();

      expect(mockInstance.get).toHaveBeenCalledWith('/courses', {
        params: {
          include: ['total_students', 'teachers', 'term', 'course_progress'],
          state: ['available', 'completed']
        }
      });
      expect(result).toEqual(mockCourses);
    });

    test('should include ended courses when requested', async () => {
      const mockInstance = mockedAxios.create.mock.results[0].value;
      mockInstance.get.mockResolvedValue({ data: [] });

      await client.listCourses(true);

      expect(mockInstance.get).toHaveBeenCalledWith('/courses', {
        params: {
          include: ['total_students', 'teachers', 'term', 'course_progress']
        }
      });
    });
  });

  describe('submitAssignment', () => {
    test('should submit text assignment', async () => {
      const mockSubmission = { id: 1, assignment_id: 1, user_id: 1 };
      const mockInstance = mockedAxios.create.mock.results[0].value;
      mockInstance.post.mockResolvedValue({ data: mockSubmission });

      const args = {
        course_id: 1,
        assignment_id: 1,
        submission_type: 'online_text_entry' as const,
        body: 'Test submission content'
      };

      const result = await client.submitAssignment(args);

      expect(mockInstance.post).toHaveBeenCalledWith(
        '/courses/1/assignments/1/submissions',
        {
          submission: {
            submission_type: 'online_text_entry',
            body: 'Test submission content'
          }
        }
      );
      expect(result).toEqual(mockSubmission);
    });

    test('should submit URL assignment', async () => {
      const mockInstance = mockedAxios.create.mock.results[0].value;
      mockInstance.post.mockResolvedValue({ data: {} });

      const args = {
        course_id: 1,
        assignment_id: 1,
        submission_type: 'online_url' as const,
        url: 'https://example.com'
      };

      await client.submitAssignment(args);

      expect(mockInstance.post).toHaveBeenCalledWith(
        '/courses/1/assignments/1/submissions',
        {
          submission: {
            submission_type: 'online_url',
            url: 'https://example.com'
          }
        }
      );
    });
  });

  describe('error handling', () => {
    test('should throw CanvasAPIError for API errors', async () => {
      const mockInstance = mockedAxios.create.mock.results[0].value;
      const mockError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      };
      mockInstance.get.mockRejectedValue(mockError);

      await expect(client.getUserProfile()).rejects.toThrow(CanvasAPIError);
    });
  });
});

// tests/integration.test.ts

import { describe, test, expect, beforeAll, afterAll } from 'vitest';
import { CanvasClient } from '../src/client.js';
import { CanvasMCPServer } from '../src/index.js';

describe('Integration Tests', () => {
  let client: CanvasClient;
  let server: any; // CanvasMCPServer type

  beforeAll(async () => {
    // Only run integration tests if we have real credentials
    const token = process.env.CANVAS_TEST_TOKEN;
    const domain = process.env.CANVAS_TEST_DOMAIN;

    if (!token || !domain) {
      console.log('Skipping integration tests - no test credentials provided');
      return;
    }

    client = new CanvasClient(token, domain);
  });

  afterAll(async () => {
    // Cleanup if needed
  });

  test('should connect to Canvas API', async () => {
    if (!client) return;

    const health = await client.healthCheck();
    expect(health.status).toBe('ok');
    expect(health.user).toBeDefined();
  });

  test('should list user courses', async () => {
    if (!client) return;

    const courses = await client.listCourses();
    expect(Array.isArray(courses)).toBe(true);
  });

  test('should get user profile', async () => {
    if (!client) return;

    const profile = await client.getUserProfile();
    expect(profile).toBeDefined();
    expect(profile.id).toBeDefined();
    expect(profile.name).toBeDefined();
  });
});

// tests/mcp-server.test.ts

import { describe, test, expect, beforeEach, vi } from 'vitest';
import { MCPServerConfig } from '../src/types.js';

describe('MCP Server', () => {
  let config: MCPServerConfig;

  beforeEach(() => {
    config = {
      name: 'test-canvas-mcp',
      version: '1.0.0',
      canvas: {
        token: 'test-token',
        domain: 'test.instructure.com'
      }
    };
  });

  test('should validate configuration', () => {
    expect(config.name).toBe('test-canvas-mcp');
    expect(config.canvas.token).toBe('test-token');
    expect(config.canvas.domain).toBe('test.instructure.com');
  });

  test('should have default retry settings', () => {
    expect(config.canvas.maxRetries).toBeUndefined(); // Will use default
  });
});

// tests/setup.ts

import { beforeAll, afterAll } from 'vitest';
import dotenv from 'dotenv';

beforeAll(async () => {
  // Load test environment variables
  dotenv.config({ path: '.env.test' });
});

afterAll(async () => {
  // Global cleanup
});

// tests/utils/canvas-mock.ts

export const mockCanvasResponse = (data: any, headers: Record<string, string> = {}) => ({
  data,
  status: 200,
  statusText: 'OK',
  headers,
  config: {}
});

export const mockPaginatedResponse = (data: any[], hasNext: boolean = false) => {
  const headers: Record<string, string> = {};
  
  if (hasNext) {
    headers.link = '</api/v1/courses?page=2>; rel="next"';
  }
  
  return mockCanvasResponse(data, headers);
};

export const mockCourse = (id: number = 1) => ({
  id,
  name: `Test Course ${id}`,
  course_code: `TEST${id}`,
  workflow_state: 'available',
  account_id: 1,
  start_at: '2024-01-01T00:00:00Z',
  end_at: '2024-12-31T23:59:59Z'
});

export const mockAssignment = (id: number = 1, courseId: number = 1) => ({
  id,
  course_id: courseId,
  name: `Test Assignment ${id}`,
  description: 'Test assignment description',
  due_at: '2024-06-15T23:59:59Z',
  points_possible: 100,
  position: 1,
  submission_types: ['online_text_entry'],
  html_url: `https://test.instructure.com/courses/${courseId}/assignments/${id}`,
  published: true,
  grading_type: 'points'
});

export const mockSubmission = (id: number = 1, assignmentId: number = 1, userId: number = 1) => ({
  id,
  assignment_id: assignmentId,
  user_id: userId,
  submitted_at: '2024-06-10T10:00:00Z',
  score: 85,
  grade: '85',
  attempt: 1,
  workflow_state: 'graded',
  late: false,
  missing: false
});

// vitest.config.ts

import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/**',
        'build/**',
        'tests/**',
        '**/*.d.ts'
      ]
    },
    testTimeout: 10000,
    hookTimeout: 10000
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});