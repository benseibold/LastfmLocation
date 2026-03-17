import xml.etree.ElementTree as et
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime
import re

# Read SMS XML
sms_xml = open('Data/SmsDataTest.xml', 'r', encoding="utf8").read()
root = et.XML(sms_xml)

# Parse SMS data
sms_data = []
for child in root:
    if child.tag == 'sms':
        sms_data.append({
            'contact_name': child.attrib['contact_name'],
            'body': child.attrib['body'],
            'date': int(child.attrib['date']),  # Unix timestamp in milliseconds
            'type': child.attrib['type']  # 1=received, 2=sent
        })

# Create DataFrame
df = pd.DataFrame(sms_data)

# Convert timestamp to datetime
df['datetime'] = pd.to_datetime(df['date'], unit='ms')
df['year_month'] = df['datetime'].dt.to_period('M')

# --- Visualization 1: People Texted Most Over Time ---

# Get top contacts by total message count
contact_counts = df['contact_name'].value_counts()
top_contacts = contact_counts.head(10).index.tolist()

# Filter to top contacts
df_top = df[df['contact_name'].isin(top_contacts)]

# Count messages per contact per month
contact_time_data = df_top.groupby(['year_month', 'contact_name']).size().reset_index(name='count')
contact_time_data['year_month'] = contact_time_data['year_month'].astype(str)

# Create line chart
fig1 = px.line(
    contact_time_data,
    x='year_month',
    y='count',
    color='contact_name',
    title='Top 10 Contacts: Message Volume Over Time',
    labels={'year_month': 'Month', 'count': 'Number of Messages', 'contact_name': 'Contact'}
)
fig1.update_xaxes(tickangle=45)
fig1.show()

# --- Visualization 2: Most Common Words with Frequent Contacts ---

# Function to extract words from text
def extract_words(text):
    # Convert to lowercase and extract words (alphanumeric only)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())  # Only words 3+ chars
    return words

# Common stop words to exclude
stop_words = {
    'the', 'and', 'for', 'you', 'that', 'with', 'are', 'was', 'this',
    'but', 'not', 'have', 'from', 'they', 'can', 'will', 'your', 'all',
    'would', 'there', 'their', 'what', 'out', 'about', 'who', 'get', 'which',
    'when', 'make', 'can', 'like', 'time', 'just', 'know', 'take', 'people',
    'into', 'year', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
    'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well',
    'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
    'most', 'him', 'her', 'his', 'has', 'said', 'been', 'she', 'did', 'amp'
}

# Analyze word frequency per top contact
contact_word_freq = {}

for contact in top_contacts[:5]:  # Top 5 contacts for word analysis
    contact_messages = df_top[df_top['contact_name'] == contact]['body']

    all_words = []
    for message in contact_messages:
        words = extract_words(str(message))
        all_words.extend([w for w in words if w not in stop_words])

    word_counts = Counter(all_words)
    contact_word_freq[contact] = word_counts.most_common(15)

# Create bar charts for each contact
fig2 = go.Figure()

for i, (contact, words) in enumerate(contact_word_freq.items()):
    if words:  # Only if there are words
        word_list, counts = zip(*words)

        fig2.add_trace(go.Bar(
            name=contact,
            x=word_list,
            y=counts,
            visible=(i == 0)  # Only first contact visible by default
        ))

# Create dropdown menu
buttons = []
for i, contact in enumerate(contact_word_freq.keys()):
    visible = [False] * len(contact_word_freq)
    visible[i] = True
    buttons.append(
        dict(
            label=contact,
            method='update',
            args=[{'visible': visible}]
        )
    )

fig2.update_layout(
    updatemenus=[
        dict(
            active=0,
            buttons=buttons,
            x=0.17,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )
    ],
    title='Most Common Words by Contact (Select Contact from Dropdown)',
    xaxis_title='Word',
    yaxis_title='Frequency'
)

fig2.show()

# --- Visualization 3: Time of Day Analysis for Sent Messages ---

# Filter only sent messages (type='2')
df_sent = df_top[df_top['type'] == '2'].copy()
df_sent['hour'] = df_sent['datetime'].dt.hour

# Count messages by hour and contact
hourly_data = df_sent.groupby(['contact_name', 'hour']).size().reset_index(name='count')

# Create heatmap
fig3 = go.Figure()

for contact in top_contacts:
    contact_hourly = hourly_data[hourly_data['contact_name'] == contact]

    # Create full 24-hour range with zeros for missing hours
    hours_df = pd.DataFrame({'hour': range(24)})
    contact_hourly = hours_df.merge(contact_hourly, on='hour', how='left').fillna(0)

    fig3.add_trace(go.Bar(
        name=contact,
        x=contact_hourly['hour'],
        y=contact_hourly['count'],
        visible=(contact == top_contacts[0])
    ))

# Create dropdown for contacts
buttons = []
for i, contact in enumerate(top_contacts):
    visible = [False] * len(top_contacts)
    visible[i] = True
    buttons.append(
        dict(
            label=contact,
            method='update',
            args=[{'visible': visible}]
        )
    )

fig3.update_layout(
    updatemenus=[
        dict(
            active=0,
            buttons=buttons,
            x=0.17,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )
    ],
    title='Time of Day: When You Send Texts (by Hour)',
    xaxis_title='Hour of Day (0-23)',
    yaxis_title='Number of Messages Sent',
    xaxis=dict(tickmode='linear', tick0=0, dtick=1)
)

fig3.show()

# --- Visualization 4: Response Time Analysis ---

# Sort by contact and datetime
df_sorted = df_top.sort_values(['contact_name', 'datetime']).reset_index(drop=True)

# Calculate response times
response_times = []
for i in range(1, len(df_sorted)):
    current = df_sorted.iloc[i]
    previous = df_sorted.iloc[i-1]

    # Check if same contact and if current is sent (type='2') and previous is received (type='1')
    if (current['contact_name'] == previous['contact_name'] and
        current['type'] == '2' and previous['type'] == '1'):

        time_diff = (current['datetime'] - previous['datetime']).total_seconds() / 60  # minutes

        # Only count responses within 24 hours (1440 minutes)
        if 0 < time_diff <= 1440:
            response_times.append({
                'contact_name': current['contact_name'],
                'response_time_minutes': time_diff
            })

if response_times:
    response_df = pd.DataFrame(response_times)
    avg_response = response_df.groupby('contact_name')['response_time_minutes'].agg(['mean', 'median', 'count']).reset_index()
    avg_response = avg_response[avg_response['count'] >= 5]  # At least 5 responses
    avg_response = avg_response.sort_values('median')

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=avg_response['contact_name'],
        y=avg_response['median'],
        name='Median Response Time',
        text=[f"{x:.1f} min" for x in avg_response['median']],
        textposition='outside'
    ))

    fig4.update_layout(
        title='Median Response Time to Received Messages (within 24hrs)',
        xaxis_title='Contact',
        yaxis_title='Response Time (minutes)',
        xaxis_tickangle=45
    )
    fig4.show()

# --- Visualization 5: Sent vs Received Ratio ---

sent_received_data = []
for contact in top_contacts:
    contact_data = df_top[df_top['contact_name'] == contact]
    sent_count = len(contact_data[contact_data['type'] == '2'])
    received_count = len(contact_data[contact_data['type'] == '1'])

    sent_received_data.append({
        'contact_name': contact,
        'sent': sent_count,
        'received': received_count,
        'total': sent_count + received_count
    })

sr_df = pd.DataFrame(sent_received_data).sort_values('total', ascending=True)

fig5 = go.Figure()
fig5.add_trace(go.Bar(
    name='Sent',
    y=sr_df['contact_name'],
    x=sr_df['sent'],
    orientation='h',
    marker_color='lightblue'
))
fig5.add_trace(go.Bar(
    name='Received',
    y=sr_df['contact_name'],
    x=sr_df['received'],
    orientation='h',
    marker_color='lightcoral'
))

fig5.update_layout(
    title='Sent vs Received Messages by Contact',
    xaxis_title='Number of Messages',
    yaxis_title='Contact',
    barmode='stack',
    height=500
)
fig5.show()

# --- Visualization 6: Peak Texting Hours Heatmap (Hour vs Day of Week) ---

df['hour'] = df['datetime'].dt.hour
df['day_of_week'] = df['datetime'].dt.day_name()

# Create pivot table
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
heatmap_pivot = heatmap_pivot.reindex(day_order)

fig6 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    colorscale='Blues',
    text=heatmap_pivot.values,
    texttemplate='%{text:.0f}',
    textfont={"size": 8},
    colorbar=dict(title="Message Count")
))

fig6.update_layout(
    title='Texting Activity Heatmap: Day of Week vs Hour of Day',
    xaxis_title='Hour of Day',
    yaxis_title='Day of Week',
    xaxis=dict(tickmode='linear', tick0=0, dtick=1),
    height=400
)
fig6.show()

# --- Visualization 7: Monthly Activity Calendar ---

df['date_only'] = df['datetime'].dt.date
daily_counts = df.groupby('date_only').size().reset_index(name='count')
daily_counts['date_only'] = pd.to_datetime(daily_counts['date_only'])

# Add day of week and week number for calendar layout
daily_counts['day_of_week'] = daily_counts['date_only'].dt.dayofweek
daily_counts['week'] = daily_counts['date_only'].dt.isocalendar().week
daily_counts['year'] = daily_counts['date_only'].dt.year
daily_counts['month'] = daily_counts['date_only'].dt.month

# Get the most recent year with data
latest_year = daily_counts['year'].max()
year_data = daily_counts[daily_counts['year'] == latest_year]

fig7 = px.density_heatmap(
    year_data,
    x='day_of_week',
    y='week',
    z='count',
    histfunc='sum',
    title=f'Activity Calendar - {latest_year}',
    labels={'day_of_week': 'Day of Week', 'week': 'Week of Year', 'count': 'Messages'},
    color_continuous_scale='Greens'
)

fig7.update_xaxes(
    ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    tickvals=[0, 1, 2, 3, 4, 5, 6]
)

fig7.update_layout(height=600)
fig7.show()

# Print summary statistics
print("\n=== SMS Summary Statistics ===")
print(f"Total messages: {len(df)}")
print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
print(f"\nTop 10 contacts by message count:")
for contact, count in contact_counts.head(10).items():
    print(f"  {contact}: {count} messages")

if response_times:
    print(f"\nAverage response times (median):")
    for _, row in avg_response.head(10).iterrows():
        print(f"  {row['contact_name']}: {row['median']:.1f} minutes ({row['count']:.0f} responses analyzed)")
