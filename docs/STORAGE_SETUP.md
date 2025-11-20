# Supabase Storage Bucket Setup

## Create Buckets via Dashboard

### 1. Product Images Bucket (Public)

1. Go to **Storage** → **New Bucket**
2. Settings:
   - **Name:** `product-images`
   - **Public bucket:** ✅ Yes
   - **File size limit:** 5 MB
   - **Allowed MIME types:** `image/jpeg, image/png, image/webp, image/jpg`

3. Set up policies (after creating bucket):
   - Go to **Policies** tab
   - Add policy: **Public Read Access**
     ```
     Target roles: public
     Policy command: SELECT
     Policy definition: (bucket_id = 'product-images')
     ```
   - Add policy: **Authenticated Upload**
     ```
     Target roles: authenticated
     Policy command: INSERT
     WITH CHECK: (bucket_id = 'product-images')
     ```

### 2. User Documents Bucket (Private)

1. Go to **Storage** → **New Bucket**
2. Settings:
   - **Name:** `user-documents`
   - **Public bucket:** ❌ No
   - **File size limit:** 10 MB
   - **Allowed MIME types:** `application/pdf, image/jpeg, image/png`

3. Policies are automatically set for private bucket (owner only access)

## Verify Buckets

Run this SQL to check:
```sql
SELECT id, name, public
FROM storage.buckets
ORDER BY name;
```

Expected output:
```
product-images  | true
user-documents  | false
```

## Next Steps

After creating buckets:
1. ✅ Run RLS test: `python test_rls_policies.py`
2. ✅ Test file upload endpoint (if implemented)
3. ✅ Verify bucket permissions work correctly
