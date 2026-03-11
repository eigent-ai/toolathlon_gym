# Canvas Course Parameters Fix Summary - v2.2.3

## 🐛 **Issue Fixed**
**GitHub Issue #9**: `restrict_enrollments_to_course_dates` not respected when creating Canvas courses

## ✅ **Root Cause**
The `restrict_enrollments_to_course_dates` parameter (and many other Canvas course parameters) were missing from the MCP tool input schemas for `canvas_create_course` and `canvas_update_course`. The MCP server filters out any parameters not explicitly defined in the inputSchema before passing them to the Canvas API, causing these parameters to be ignored.

## 🔧 **Fix Applied**

### **Files Modified:**
- `src/index.ts` - Updated tool input schemas
- `package.json` - Version bump to 2.2.3
- `CHANGELOG.md` - Documented the fix

### **Parameters Added to `canvas_create_course`:**
- ✅ `restrict_enrollments_to_course_dates` - The key missing parameter
- ✅ `is_public_to_auth_users`
- ✅ `public_syllabus` 
- ✅ `public_syllabus_to_auth`
- ✅ `public_description`
- ✅ `allow_student_wiki_edits`
- ✅ `allow_wiki_comments`
- ✅ `allow_student_forum_attachments`
- ✅ `open_enrollment`
- ✅ `self_enrollment`
- ✅ `term_id`
- ✅ `sis_course_id`
- ✅ `integration_id`
- ✅ `hide_final_grades`
- ✅ `apply_assignment_group_weights`
- ✅ `time_zone`

### **Parameters Added to `canvas_update_course`:**
- ✅ All the same parameters as create (except `account_id` which can't be changed)

## 🎯 **Impact**

### **Before Fix:**
```javascript
// This would NOT work
{
  "account_id": 123,
  "name": "Test Course",
  "start_at": "2025-09-01T09:00:00Z",
  "end_at": "2025-12-15T18:00:00Z", 
  "restrict_enrollments_to_course_dates": true  // IGNORED!
}
// Result: Course created but restrict_enrollments_to_course_dates = false
```

### **After Fix:**
```javascript
// This now WORKS correctly
{
  "account_id": 123,
  "name": "Test Course", 
  "start_at": "2025-09-01T09:00:00Z",
  "end_at": "2025-12-15T18:00:00Z",
  "restrict_enrollments_to_course_dates": true  // RESPECTED!
}
// Result: Course created with restrict_enrollments_to_course_dates = true
```

## 🚀 **Usage Example**

Now you can create courses with proper enrollment date restrictions:

```javascript
await canvas_create_course({
  account_id: 123,
  name: "Fall 2025 Computer Science",
  course_code: "CS101",
  start_at: "2025-08-25T08:00:00Z",
  end_at: "2025-12-15T17:00:00Z",
  restrict_enrollments_to_course_dates: true,  // Now works!
  is_public: false,
  hide_final_grades: false,
  apply_assignment_group_weights: true,
  time_zone: "America/Denver"
});
```

## 📋 **Verification**
- ✅ All missing parameters now included in inputSchema
- ✅ Parameters match corresponding TypeScript interfaces
- ✅ Backward compatible - no breaking changes
- ✅ Version updated to 2.2.3
- ✅ Changelog documented

## 🏁 **Status**
**RESOLVED** - The `restrict_enrollments_to_course_dates` parameter and all other missing Canvas course parameters are now properly supported by the MCP server tools.

---

**GitHub Issue**: https://github.com/DMontgomery40/mcp-canvas-lms/issues/9  
**Fix Version**: 2.2.3  
**Release Date**: 2025-06-27
