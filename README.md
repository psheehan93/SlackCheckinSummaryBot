# SlackCheckinSummaryBot
This is a basic slack bot which collates daily check-in posts and passes them to ChatGPT's api to be summarized.

The intended usage of this is as follows:

- in your team's slack, everyone posts a daily check-in status update
- all check-in posts go in a dedicated channel, where only check-ins are posted
- set up the main.py script on some kind of serverless hosting like Google Functions or Firebase
- the way I used it, we set it up with Google Cloud Scheduling to run the script once a week, the morning of our weekly team meetings

You need the following permissions enabled in slack:
```
channels:history
channels:join
channels:read
chat:write
im:write
users:read
```

You'll need to replace the following placeholders with your own values:
```
your-slack-token
your-channel-id    - (Note its channel *id* not channel name.)
your-openai-api-key
```

You may wish to change which GPT model you are using, or to change the prompt. Here is the prompt I was using:

>This is a list of posts from a Slack channel where our team posts their daily status updates. Write a brief summary of the contents of these messages, perhaps with a bulleted list. If you can't write a summary, simply reply 'Error with summary. Tell Admin about it.'. This user's name is "+user_name+". Make sure you use their name in the summary rather than saying 'user' or 'member'. Remember all the posts in the following list are all from this one user! The posts you're reviewing are all by this user. Here is the content:"+messages_str


If you try to utilize this for a use-case where there will be >100 posts or with large amounts of text content, there may be issues with the slack bot or you may go over the GPT token limit.
