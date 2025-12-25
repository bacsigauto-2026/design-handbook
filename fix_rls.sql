-- RLS FIX SCRIPT

-- 1. DISABLE Row Level Security on 'users' table.
-- This is necessary because "Simulate Login" does not provide a real Authentication session
-- to the database, so standard RLS policies would block the application from reading the user's role.
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 2. (Optional) If you want to keep RLS enabled (for Production), you must run this to fix the Infinite Recursion error:
/*
-- Fix recursion by using a security definer function
CREATE OR REPLACE FUNCTION is_admin() 
RETURNS BOOLEAN LANGUAGE sql SECURITY DEFINER AS $$
  SELECT EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin');
$$;

DROP POLICY IF EXISTS "Enable read access for admins" ON users;
CREATE POLICY "Enable read access for admins" ON users FOR SELECT USING (is_admin());
*/
