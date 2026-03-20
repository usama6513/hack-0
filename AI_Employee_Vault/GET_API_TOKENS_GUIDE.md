# HOW TO GET REAL API TOKENS FOR SOCIAL MEDIA

## 📘 FACEBOOK TOKENS

### Step 1: Create a Facebook App
1. Go to https://developers.facebook.com/
2. Click "My Apps" > "Create App"
3. Choose "Business" as app type
4. Enter display name and contact email

### Step 2: Add Facebook Pages Product
1. In your app dashboard, click "+ Add Product"
2. Select "Facebook Pages"
3. Go to "Settings" > "Basic" and copy your:
   - App ID
   - App Secret

### Step 3: Get Page Access Token
1. Go to "Graph API Explorer" (Tools > Graph API Explorer)
2. Select your app from the dropdown
3. Select "pages_manage_posts", "pages_read_engagement", "pages_manage_engagement" permissions
4. Click "Generate Access Token"
5. Go to your Facebook Page > Settings > About > Copy Page ID
6. Use these credentials in credentials.json

## 📷 INSTAGRAM TOKENS

### Prerequisites:
- Facebook Page connected to Instagram Business Account

### Step 1: Use the same Facebook App
1. In your Facebook developer app
2. Add "Instagram Basic Display" product
3. Go to "Instagram" > "Basic Display" settings

### Step 2: Get Instagram Access Token
1. Use Graph API Explorer again
2. Select "instagram_basic" permission
3. Generate token
4. Go to your Instagram Business profile to get Account ID
5. Use credentials in credentials.json

## 🐦 TWITTER TOKENS

### Step 1: Apply for Twitter Developer Account
1. Go to https://developer.twitter.com/
2. Apply for a developer account
3. Create a new app

### Step 2: Get API Credentials
1. In your app, go to "Keys and tokens"
2. Copy these:
   - API Key
   - API Secret
   - Bearer Token
   - Access Token
   - Access Token Secret
3. Use these in credentials.json

## 🔐 SECURITY TIPS:
- Never share your tokens publicly
- Store them securely in credentials.json
- Use environment variables for production
- Rotate tokens periodically

## 📋 Example credentials.json format:
```json
{
  "facebook": {
    "access_token": "your_facebook_access_token",
    "page_id": "your_facebook_page_id",
    "app_id": "your_app_id",
    "app_secret": "your_app_secret"
  },
  "instagram": {
    "access_token": "your_instagram_access_token",
    "account_id": "your_instagram_account_id"
  },
  "twitter": {
    "bearer_token": "your_bearer_token",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "your_access_token",
    "access_token_secret": "your_access_token_secret"
  }
}
```

Once you have these tokens, your posts will go directly to your real social media profiles!