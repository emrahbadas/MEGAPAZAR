# Supabase Security Hardening Guide

## 📋 Implementation Steps

### Step 1: Run SQL Migration

1. Open **Supabase Dashboard** → **SQL Editor**
2. Click **New query**
3. Copy and paste the contents of `migrations/supabase_security_hardening.sql`
4. Click **Run**

This will:
- ✅ Enable RLS on all tables
- ✅ Create policies for listings (CRUD + service role)
- ✅ Create policies for orders (buyer/seller access)
- ✅ Create policies for notifications (user-specific)
- ✅ Create policies for conversations (user-specific)
- ✅ Create policies for users (profile management)
- ✅ Create policies for product_embeddings (public read)

### Step 2: Create Storage Buckets

**Option A: Via Supabase Dashboard (Recommended)**

1. Go to **Storage** in Supabase Dashboard
2. Click **New Bucket**
3. Create bucket: `product-images`
   - Name: `product-images`
   - Public: ✅ Yes
   - File size limit: 5 MB
   - Allowed MIME types: `image/jpeg, image/png, image/webp`
4. Create bucket: `user-documents`
   - Name: `user-documents`
   - Public: ❌ No
   - File size limit: 10 MB
   - Allowed MIME types: `application/pdf, image/jpeg, image/png`

**Option B: Via SQL**

Uncomment the storage bucket section in the SQL file and run.

### Step 3: Configure Storage Policies

After creating buckets, set up policies:

**For product-images:**
- ✅ Anyone can view (public read)
- ✅ Authenticated users can upload
- ✅ Only owner can update/delete their uploads

**For user-documents:**
- ✅ Only owner can view
- ✅ Only owner can upload
- ✅ Only owner can update/delete

These are in the SQL file (commented out) - uncomment and run if you want SQL-based bucket creation.

### Step 4: Verify RLS is Working

Run the test script:
```bash
python test_rls_policies.py
```

This will:
- Create test data for multiple users
- Attempt cross-user access (should fail)
- Verify service role can access everything
- Clean up test data

### Step 5: Update Backend Code

The backend already uses `SUPABASE_SERVICE_KEY` for operations, which bypasses RLS. This is correct for:
- Background jobs (price monitoring)
- Agent operations (creating listings)
- Admin operations

For user-facing API endpoints, consider implementing Supabase Auth:
```python
# Example: Get user from JWT token
from fastapi import Header, HTTPException

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = supabase.auth.get_user(token)
    return user
```

## 🔐 RLS Policy Summary

### Listings Table
| Action | Who Can Access | Condition |
|--------|---------------|-----------|
| SELECT | Everyone | status = 'active' |
| SELECT | Owner | user_id = auth.uid() |
| INSERT | Owner | user_id = auth.uid() |
| UPDATE | Owner | user_id = auth.uid() |
| DELETE | Owner | user_id = auth.uid() |
| ALL | Service Role | Always |

### Orders Table
| Action | Who Can Access | Condition |
|--------|---------------|-----------|
| SELECT | Buyer | buyer_id = auth.uid() |
| SELECT | Seller | seller owns listing |
| INSERT | Buyer | buyer_id = auth.uid() |
| UPDATE | Seller | seller owns listing |
| ALL | Service Role | Always |

### Notifications Table
| Action | Who Can Access | Condition |
|--------|---------------|-----------|
| SELECT | Owner | user_id = auth.uid() |
| UPDATE | Owner | user_id = auth.uid() |
| INSERT | Service Role | Always |
| ALL | Service Role | Always |

### Conversations Table
| Action | Who Can Access | Condition |
|--------|---------------|-----------|
| SELECT | Owner | user_id = auth.uid() |
| INSERT | Owner | user_id = auth.uid() |
| UPDATE | Owner | user_id = auth.uid() |
| ALL | Service Role | Always |

### Users Table
| Action | Who Can Access | Condition |
|--------|---------------|-----------|
| SELECT | Everyone | Public profiles |
| UPDATE | Owner | id = auth.uid() |
| ALL | Service Role | Always |

### Product Embeddings Table
| Action | Who Can Access | Condition |
|--------|---------------|-----------|
| SELECT | Everyone | For search |
| ALL | Service Role | Always |

## ⚠️ Important Notes

1. **Service Role Key**: Never expose `SUPABASE_SERVICE_KEY` to frontend. Only use in backend.

2. **Auth Integration**: For full RLS protection, implement Supabase Auth:
   - Sign up/sign in users
   - Pass JWT tokens in API requests
   - Verify tokens in backend

3. **Current State**: Backend uses service key (bypasses RLS). This is OK for:
   - Agent operations
   - Background jobs
   - Admin functions
   
4. **Future Enhancement**: Add user authentication layer when building frontend.

5. **Storage Upload**: Update backend to handle file uploads to Supabase Storage buckets.

## 🧪 Testing RLS

After running the SQL migration, test with:

```bash
# Run automated RLS tests
python test_rls_policies.py

# Manual testing in Supabase SQL Editor:
# Test 1: Try to access another user's draft listing
SELECT * FROM listings 
WHERE user_id != auth.uid() 
AND status = 'draft';
-- Should return empty (RLS blocks)

# Test 2: View active listings
SELECT * FROM listings 
WHERE status = 'active';
-- Should return results (public access)

# Test 3: Try to insert as another user
INSERT INTO listings (user_id, title, price, category, status)
VALUES ('some-other-user-id', 'Test', 100, 'Test', 'active');
-- Should fail (RLS blocks)
```

## 📚 Next Steps

After RLS is configured:

1. ✅ **Verify policies work** - Run test script
2. ✅ **Set up storage buckets** - For image uploads
3. ⏳ **Implement auth in frontend** - When building web UI
4. ⏳ **Add file upload endpoint** - For product images
5. ⏳ **Test with real users** - Create test accounts and verify isolation

## 🔗 Resources

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
