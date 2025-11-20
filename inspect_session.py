import pickle

s = pickle.load(open('sessions/session__905551234567.pkl', 'rb'))
print('Stage:', s.stage)
print('Intent:', s.intent)
print('Product:', s.product_info)
print('Missing:', s.missing_fields)
print('History:', len(s.conversation_history), 'messages')
print('\nAll messages:')
for i, m in enumerate(s.conversation_history):
    print(f"{i+1}. {m['role']}: {m['content'][:100]}")
