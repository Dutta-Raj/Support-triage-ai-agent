import pandas as pd

df = pd.read_csv('support_tickets/output.csv')

print('=== Tickets with Generic Responses ===')
count = 0
for i, row in df.iterrows():
    if 'Thank you for contacting' in row['response'] and row['status'] == 'replied':
        print(f'{i}: {row["issue"][:60]}...')
        count += 1

print(f'\nTotal generic responses: {count}')
print(f'Total escalated: {len(df[df["status"] == "escalated"])}')
print(f'Total replied: {len(df[df["status"] == "replied"])}')
print(f'Total tickets: {len(df)}')
