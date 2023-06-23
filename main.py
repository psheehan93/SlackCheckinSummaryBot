import os
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai

def weekly_check_in(request):
    client = WebClient(token='your-slack-token')

    # Get the current timestamp
    now = datetime.now()

    # Get the timestamp for last Monday
    last_monday = now - timedelta(days=now.weekday())

    # Get all messages in the channel since last Monday
    try:
        result = client.conversations_history(
            channel='your-channel-id',
            oldest=last_monday.timestamp(),  # Python uses seconds, just like Slack
            inclusive=True,
        )
        messages = result.data.get('messages')
    except SlackApiError as e:
        print(f"Error fetching conversations history: {e}")

    # Group the messages by user
    user_messages = {}

    for message in messages:
        user = message.get('user')
        if user:
            if user not in user_messages:
                user_messages[user] = []
            user_messages[user].append(message.get('text'))

    # Initialize OpenAI client
    openai.api_key = 'your-openai-api-key'

    # Send each user their messages
    for user, user_message_list in user_messages.items():
        user_message_list.reverse()  # reverse the list of messages

        # Join messages into a single string
        messages_str = '\n'.join(user_message_list)


        try:
            user_info = client.users_info(user=user).data
            user_name = user_info['user']['real_name']
        except SlackApiError as e:
            print(f"Error fetching user info: {e}")
            user_name = 'Unknown'

        # Generate summary with OpenAI API
        if user_message_list:
            try:
                summary_result = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", 
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "This is a list of posts from a Slack channel where our team posts their daily status updates. Write a brief summary of the contents of these messages, perhaps with a bulleted list. If you can't write a summary, simply reply 'Error with summary. Tell Pete about it.'. This user's name is "+user_name+". Make sure you use their name in the summary rather than saying 'user' or 'member'. Remember all the posts in the following list are all from this one user! The posts you're reviewing are all by this user. Here is the content:"+messages_str}
                    ],
                )
                summary = summary_result.choices[0].message['content']

                # Append summary to the message list
                user_message_list.append('\nSummary:\n' + summary)
            except Exception as e:
                print(f"Error generating summary: {e}")
                user_message_list.append('\nThere was an error with the summary. My bad! Tell Pete about it.\n')
            text = 'Greetings human known as '+user_name+'. Here are your check-ins from this week with an AI generated summary:\n\n' + '\n'.join(user_message_list)

            try:
                client.chat_postMessage(
                    channel=user,
                    text=text
                )
            except SlackApiError as e:
                print(f"Error sending message: {e}")

    return '', 204
