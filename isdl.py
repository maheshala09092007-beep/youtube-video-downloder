import os
import instaloader

SESSION_ID = input("Paste your Instagram sessionid cookie value: ").strip()
# Enter numeric ID (or hit enter to use username fallback)
target_id_input = input("Enter TARGET Numeric User ID (or press Enter for username): ").strip()

L = instaloader.Instaloader(
    dirname_pattern=os.path.expanduser("~/Downloads"),
    filename_pattern="{target}_{date_utc}_UTC",
    download_video_thumbnails=False,
    save_metadata=False,
    download_comments=False
)

# Inject sessionid
L.context._session.cookies.set("sessionid", SESSION_ID, domain=".instagram.com")

try:
    username = L.test_login()
    print(f"\nSuccessfully authenticated as @{username}!")
except Exception as e:
    print(f"\nAuthentication failed: {e}")
    exit()

# Obtain target user ID
if target_id_input.isdigit():
    target_id = int(target_id_input)
else:
    target_username = target_id_input if target_id_input else input("Enter TARGET username: ").strip()
    print("Resolving username to User ID...")
    profile = instaloader.Profile.from_username(L.context, target_username)
    target_id = profile.userid

print(f"Fetching active stories for User ID: {target_id}...")
story_count = 0

# Download stories using direct User ID
for story in L.get_stories(userids=[target_id]):
    for item in story.get_items():
        L.download_storyitem(item, target=str(target_id))
        story_count += 1

if story_count == 0:
    print("No active stories found.")
else:
    print(f"\nDone! Saved {story_count} story file(s) to Downloads!")
