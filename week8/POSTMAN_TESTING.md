# Postman API Testing Guide

## Overview
This directory contains Postman collection and environment files for testing the week8 API.

## Files
- `API_Testing.postman_collection.json` - Postman collection with API test cases
- `API_Testing_Environment.postman_environment.json` - Environment variables

## Setup Instructions

### 1. Import Collection
1. Open Postman
2. Click **Import** (top left)
3. Select `API_Testing.postman_collection.json`
4. The collection will be added to your workspace

### 2. Import Environment
1. Click **Environments** (left sidebar)
2. Click **Import**
3. Select `API_Testing_Environment.postman_environment.json`
4. The environment will be added to your workspace

### 3. Select Environment
1. Click the environment dropdown (top right)
2. Select **API Testing Environment**

## Test Cases

### 1. **login** (POST)
- **Endpoint:** `/api/admin/login`
- **Body:** Admin credentials
- **Expected:** Returns `access_token` (status 200)

### 2. **books** (GET)
- **Endpoint:** `/api/books`
- **Auth:** Bearer token (from login)
- **Expected:** Returns books list (status 200)

### 3. **readers** (GET)
- **Endpoint:** `/api/readers`
- **Expected:** Returns 401 (Missing Authorization Header)

### 4. **authors** (POST)
- **Endpoint:** `/api/authors`
- **Auth:** Bearer token (from login)
- **Body:** Missing required `name` field
- **Expected:** Returns error "name required" (status 400)

### 5. **records** (GET)
- **Endpoint:** `/api/records`
- **Auth:** Bearer token (from login)
- **Expected:** Returns records list (status 200)

## Running Tests

1. Ensure your Flask API is running on `http://127.0.0.1:8003`
2. The **prerequest** script will automatically:
   - Login with admin credentials
   - Store the access token in the environment
3. Run individual tests or click **Run Collection**
4. View results in the **Test Results** tab

## Environment Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | http://127.0.0.1:8003 | API base URL |
| `admin_email` | admin@gmail.com | Admin login email |
| `admin_password` | 123456 | Admin login password |
| `access_token` | (auto-generated) | JWT token for authenticated requests |

## Notes
- The `access_token` is automatically generated before each test run
- All tests include assertions to validate responses
- Ensure the database is properly initialized with test data

