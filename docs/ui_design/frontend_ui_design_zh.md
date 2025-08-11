# Frontend User Interface Design Specification

Based on the system architecture and API interface specifications, this document details the prototype design of the frontend user interface, including interface elements, layout structure, and user interaction flows.

## 1. User Authentication Page (Login/Registration)

### 1.1 Page Overview
The user authentication page is the entry point for users to access the system, containing two functional modules: login and registration, using tab switching form.

### 1.2 Interface Elements

#### Login Module
- **Logo/Brand Identity**: Located at the top center of the page
- **Welcome Title**: Such as "Welcome Back"
- **Username/Email Input Field**:
  - Input Type: Text
  - Placeholder: Please enter username or email
  - Validation: Required field
- **Password Input Field**:
  - Input Type: Password
  - Placeholder: Please enter password
  - Validation: Required field, minimum length 6 characters
- **Login Button**:
  - Type: Primary button
  - Text: Login
  - Status: Enabled by default, shows loading state when submitting
- **Remember Me Checkbox**: Optional feature
- **Forgot Password Link**: Redirects to password reset page
- **Register New Account Link**: Switches to registration tab

#### Registration Module
- **Logo/Brand Identity**: Located at the top center of the page
- **Welcome Title**: Such as "Create New Account"
- **Username Input Field**:
  - Input Type: Text
  - Placeholder: Please enter username
  - Validation: Required field, uniqueness validation
- **Email Input Field**:
  - Input Type: Email
  - Placeholder: Please enter email address
  - Validation: Required field, email format, uniqueness validation
- **Password Input Field**:
  - Input Type: Password
  - Placeholder: Please enter password
  - Validation: Required field, minimum length 6 characters
- **Confirm Password Input Field**:
  - Input Type: Password
  - Placeholder: Please enter password again
  - Validation: Required field, must match password
- **Nickname Input Field** (Optional):
  - Input Type: Text
  - Placeholder: Please enter nickname
- **Phone Number Input Field** (Optional):
  - Input Type: Tel
  - Placeholder: Please enter phone number
- **Register Button**:
  - Type: Primary button
  - Text: Register
  - Status: Enabled by default, shows loading state when submitting
- **Already Have Account Link**: Switches to login tab

### 1.3 Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│                      Logo/Brand Identity                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Welcome Title                          │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  ┌─┬────────────┬─┐    ┌─┬────────────┬─┐               │ │
│  │  │ │   Login    │ │    │ │ Register   │ │               │ │
│  │  └─┴────────────┴─┘    └─┴────────────┴─┘               │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  [Username/Email Input Field]                           │ │
│  │  [Password Input Field]                                 │ │
│  │  [Remember Me][Forgot Password]                         │ │
│  │  [Login Button]                                         │ │
│  │  [Register New Account Link]                            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 User Interaction Flow

#### Login Flow
1. User enters username/email and password
2. Clicks login button
3. Frontend validates input format
4. Submits to backend API `/api/auth/login`
5. Based on response results:
   - Success: Save JWT Token to local storage, redirect to main interface
   - Failure: Display error message (such as incorrect username or password)

#### Registration Flow
1. User fills in registration information
2. Frontend validates input format
3. Clicks register button
4. Submits to backend API `/api/auth/register`
5. Based on response results:
   - Success: Display registration success message, auto-login or redirect to login page
   - Failure: Display error message (such as username already exists)

## 2. Main Interface (Conversation List and Current Conversation Window)

### 2.1 Page Overview
The main interface is the core page for daily user usage, divided into left conversation list area and right current conversation window area.

### 2.2 Interface Elements

#### Top Navigation Bar
- **Logo/Brand Identity**: Left side
- **User Avatar/Nickname**: Right dropdown menu
  - Profile
  - User Settings
  - History Records
  - Logout
- **New Conversation Button**: Primary button, located in center or right of navigation bar

#### Left Conversation List Area
- **Search Box**: Search conversations by title or content
- **Conversation List**:
  - Each conversation item includes:
    - Conversation title (default to "New Conversation" or first few sentences summary)
    - AI model name used
    - Last update time
    - Delete button (shown on hover)
- **Pagination Controls**: Supports pagination browsing for large number of conversations

#### Right Current Conversation Window Area
- **Conversation Title Bar**:
  - Editable conversation title
  - Display of AI model used
  - Conversation settings button
- **Message History Area**:
  - User messages (right-aligned, different background color)
  - AI assistant messages (left-aligned, different background color)
  - Support for multiple content type display:
    - Text content
    - Image content
    - Video content (thumbnail + play button)
- **Input Area**:
  - Multi-line text input box
  - Attachment upload button (images, videos)
  - Send button
  - Quick action buttons (such as clear input)

### 2.3 Layout Structure
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Logo  [New Conversation]                                  [User Avatar▼]    │
├────────────────────────────────┬────────────────────────────────────────────┤
│ Conversation List Area         │ Current Conversation Window Area           │
│                                │                                            │
│ [Search Box]                   │ [Conversation Title Bar]                   │
│                                │                                            │
│ ┌────────────────────────────┐ │ ┌────────────────────────────────────────┐ │
│ │ Conversation 1             │ │ │ User Message                           │ │
│ │ Title: How to Learn AI     │ │ │                                        │ │
│ │ Model: qwen-vl-max-latest  │ │ └────────────────────────────────────────┘ │
│ │ Time: 2023-01-01 10:00     │ │ ┌────────────────────────────────────────┐ │
│ └────────────────────────────┘ │ │ AI Assistant Message                   │ │
│ ┌────────────────────────────┐ │ │                                        │ │
│ │ Conversation 2             │ │ └────────────────────────────────────────┘ │
│ │ Title: Image Recognition   │ │                                            │
│ │ Model: qwen-plus           │ │                                            │
│ │ Time: 2023-01-01 09:30     │ │                                            │
│ └────────────────────────────┘ │                                            │
│ ...                            │ [Input Area]                               │
│                                │ [Text Box][Attachment][Send]               │
└────────────────────────────────┴────────────────────────────────────────────┘
```

### 2.4 User Interaction Flow

#### New Conversation Flow
1. User clicks "New Conversation" button
2. Calls backend API `/api/conversations` to create new conversation
3. Upon success, refreshes conversation list and selects newly created conversation
4. Clears current conversation window content

#### Send Message Flow
1. User enters text or uploads attachment in input box
2. Clicks send button or presses Enter key
3. Frontend validates input content
4. Displays user message in conversation window
5. Calls backend API `/api/conversations/{conversation_id}/messages` to send message
6. Shows loading state
7. Receives AI assistant response and displays
8. Updates last update time in conversation list

#### Switch Conversation Flow
1. User clicks any conversation in left conversation list
2. Loads message history of that conversation (calls `/api/conversations/{conversation_id}/messages`)
3. Updates right conversation window content
4. Updates conversation title bar information

## 3. Conversation Details Page

### 3.1 Page Overview
The conversation details page displays complete information of a specific conversation, including conversation metadata and detailed message history.

### 3.2 Interface Elements

#### Top Breadcrumb Navigation
- Home > Conversation List > Conversation Details

#### Conversation Information Area
- **Conversation Title**: Editable
- **AI Model**: Displays model name used
- **Creation Time**: Conversation creation time
- **Last Update Time**: Conversation last update time
- **Conversation Status**: In Progress/Ended
- **Action Buttons**:
  - Edit conversation information
  - Export conversation records
  - Delete conversation

#### Message History Area
- **Message List**: Displays all messages in chronological order
  - Distinguishes display of user messages and AI assistant messages
  - Supports multiple content types (text, images, videos)
  - Displays message sending time
  - Message action menu (copy, delete, etc.)

#### Bottom Action Area
- **Continue Conversation Button**: Redirects to main interface and loads this conversation
- **Return to List Button**: Returns to conversation list page

### 3.3 Layout Structure
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Home > Conversation List > Conversation Details                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Conversation Information Area                                               │
│                                                                             │
│ Title: How to Learn AI                          [Edit][Export][Delete]     │
│ Model: qwen-vl-max-latest                                                   │
│ Creation Time: 2023-01-01 10:00                                             │
│ Last Update: 2023-01-01 10:15                                               │
│ Status: In Progress                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Message History Area                                                        │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ [User Avatar] User Message                                              │ │
│ │ Time: 2023-01-01 10:00                                                  │ │
│ │ Content: I want to learn AI, what suggestions do you have?              │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ AI Assistant Message [Avatar]                                           │ │
│ │ Time: 2023-01-01 10:01                                                  │ │
│ │ Content: Learning AI can start from several aspects...                  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ ...                                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ [Continue Conversation][Return to List]                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 User Interaction Flow

#### Edit Conversation Information Flow
1. User clicks "Edit" button
2. Pops up edit dialog, displays current conversation information
3. User modifies conversation title and other information
4. Submits to backend API `/api/conversations/{conversation_id}` to update conversation
5. Updates page display upon success

#### Delete Conversation Flow
1. User clicks "Delete" button
2. Pops up confirmation dialog
3. User confirms deletion
4. Calls backend API `/api/conversations/{conversation_id}` to delete conversation
5. Redirects to conversation list page upon success

## 4. History Records Page

### 4.1 Page Overview
The history records page displays users' API call history and conversation statistics, helping users understand usage patterns.

### 4.2 Interface Elements

#### Top Navigation Bar
- Page Title: History Records
- Time Filter: Filter by date range
- Model Filter: Filter by AI model

#### Statistics Information Area
- **Total Conversations**: Total number of conversations created by user
- **Total Messages**: Total number of sent and received messages
- **Total Tokens**: Total number of tokens consumed
- **Model Usage Statistics**: Chart display of model usage statistics

#### API Call History Area
- **Table View**:
  - Call Time
  - Model Used
  - API Endpoint
  - Status Code
  - Tokens Consumed
  - Call Duration
- **Pagination Controls**: Supports pagination browsing for large number of records
- **Export Button**: Export history records as CSV file

#### Chart Display Area
- **Daily Usage Statistics Chart**: Line chart showing daily conversation, message, and token usage
- **Model Usage Distribution Chart**: Pie chart showing model usage proportions

### 4.3 Layout Structure
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ History Records                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ [Time Filter][Model Filter][Export Button]                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Statistics Information Area                                                 │
│                                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│ │ Total       │ │ Total       │ │ Total       │ │ Model       │             │
│ │ Conversations││ Messages    │ │ Tokens      │ │ Statistics  │             │
│ │     15      │ │     128     │ │    2560     │ │             │             │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Chart Display Area                                                          │
│                                                                             │
│ [Daily Usage Statistics Chart]        [Model Usage Distribution Chart]      │
├─────────────────────────────────────────────────────────────────────────────┤
│ API Call History Area                                                       │
│                                                                             │
│ Time              Model              Endpoint         Status  Tokens  Duration│
│ 2023-01-01 10:00  qwen-vl-max...   /api/bailian...   200     21      1200ms  │
│ 2023-01-01 09:30  qwen-plus        /api/bailian...   200     15      800ms   │
│ ...                                                                         │
│                                                                             │
│ [Pagination Controls]                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 User Interaction Flow

#### Filtering Flow
1. User selects time range or model filter conditions
2. Automatically refreshes API call history and statistics
3. Calls backend APIs `/api/history/api-calls` and `/api/history/conversations/statistics` to get data
4. Updates page display

#### Export Flow
1. User clicks export button
2. Generates CSV file based on current filter conditions
3. Downloads file to local machine

## 5. User Settings Page

### 5.1 Page Overview
The user settings page allows users to manage personal information, account security, and system preferences.

### 5.2 Interface Elements

#### Side Navigation Menu
- Personal Information
- Account Security
- Notification Settings
- Privacy Settings

#### Personal Information Settings
- **Avatar Upload**: Upload and crop user avatar
- **Username**: Read-only display
- **Email Address**: Read-only display (requires specific process to modify)
- **Nickname**: Editable text box
- **Phone Number**: Editable text box
- **Save Button**: Save modified personal information

#### Account Security Settings
- **Change Password**:
  - Current Password Input Field
  - New Password Input Field
  - Confirm New Password Input Field
  - Change Password Button
- **Login History**: Display recent login records
  - Login Time
  - Login IP Address
  - Login Device Information

#### Notification Settings
- **Email Notifications**: Toggle options
  - System Announcement Notifications
  - Conversation Update Notifications
  - API Usage Reminders
- **In-App Notifications**: Toggle options
  - System Messages
  - Important Updates

#### Privacy Settings
- **Data Export**: Export user data
- **Data Deletion**: Delete account (dangerous operation, requires confirmation)

### 5.3 Layout Structure
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ User Settings                                                               │
├────────────────────────────────┬────────────────────────────────────────────┤
│ Side Navigation Menu           │ Settings Content Area                      │
│                                │                                            │
│ • Personal Information         │ ┌────────────────────────────────────────┐ │
│ • Account Security             │ │ [Avatar Upload]                        │ │
│ • Notification Settings        │ │                                        │ │
│ • Privacy Settings             │ │ Username: example_user (Read-only)     │ │
│                                │ │ Email: user@example.com (Read-only)    │ │
│                                │ │ Nickname: [Input Box]                  │ │
│                                │ │ Phone Number: [Input Box]              │ │
│                                │ │                                        │ │
│                                │ │ [Save]                                 │ │
│                                │ └────────────────────────────────────────┘ │
└────────────────────────────────┴────────────────────────────────────────────┘
```

### 5.4 User Interaction Flow

#### Modify Personal Information Flow
1. User modifies nickname or phone number
2. Clicks save button
3. Frontend validates input format
4. Submits to backend API `/api/auth/user` to update user information
5. Displays success message upon success

#### Change Password Flow
1. User enters current password, new password, and confirm new password
2. Frontend validates password strength and consistency
3. Clicks change password button
4. Submits to backend API (requires specific API endpoint)
5. Displays success message upon success, may require re-login

## Summary

This UI design specification is based on the system's API interface specifications and database design, covering core pages including user authentication, main interface, conversation details, history records, and user settings. The design focuses on user experience, providing clear interface elements, reasonable layout structure, and smooth interaction flows to meet users' core needs for interacting with AI models.