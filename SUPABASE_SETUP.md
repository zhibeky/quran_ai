# Supabase Setup for User Tracking

This guide will help you set up Supabase to track your Quran AI bot users.

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Choose your organization
5. Enter project details:
   - Name: `quran-ai-bot` (or your preferred name)
   - Database Password: Choose a strong password
   - Region: Choose closest to your users
6. Click "Create new project"

## Step 2: Get Your Credentials

1. In your project dashboard, go to **Settings** → **API**
2. Copy your **Project URL** and **anon public** key
3. Add these to your `.env` file:
   ```
   SUPABASE_URL=your_project_url_here
   SUPABASE_ANON_KEY=your_anon_key_here
   ```

## Step 3: Create the Database Table

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `supabase_setup.sql`
3. Paste it in the SQL editor and click "Run"
4. This will create the `users` table with proper indexes and security

## Step 4: Test the Setup

1. Make sure your `.env` file has the Supabase credentials
2. Run your bot - it should now track users automatically
3. Check the **Table Editor** in Supabase to see users being tracked

## What Gets Tracked

- **User ID**: Telegram user ID (unique identifier)
- **Username**: Telegram username (if available)
- **First/Last Name**: User's display name
- **First Seen**: When user first interacted with bot
- **Last Seen**: Last interaction timestamp
- **Message Count**: Total messages sent to bot
- **Timestamps**: Created/updated timestamps

## Security Notes

- The table uses Row Level Security (RLS)
- Currently allows all operations (you can restrict this later)
- Uses the `anon` key (public, safe for client-side use)

## Next Steps

After this basic setup, you can:
1. Add more tracking fields (language preferences, etc.)
2. Create analytics dashboards
3. Implement user segmentation
4. Add more sophisticated tracking features