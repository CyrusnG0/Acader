# Put the demo online (about 10 minutes)

The app is in this folder. It has been tested on this machine (8 web tests pass, a full session ran against the live model, the container builds and starts). It has not been put on a public host yet, because that needs your hosting login and your model key, and I am not allowed to copy the key.

## 1. Try it on your own computer first
```
cd /Users/micmic/Documents/GitHub/Acader/writing-room-kit/web
DEMO_CODE=letmein python3 -m uvicorn app:app --port 8780
```
Open http://localhost:8780 and enter `letmein`. (The key is picked up the way the other demos do it, from your environment or the repo-root `.env`.)

## 2. Put it on Fly.io (Hong Kong region)
Run these in a terminal, from the repo root `/Users/micmic/Documents/GitHub/Acader`. Type your own key and code. Do not paste the key into any chat.
```
flyctl auth login
flyctl apps create acader-room            # if the name is taken, pick another and change `app =` in writing-room-kit/web/fly.toml
flyctl secrets set DEEPSEEK_API_KEY=<your DeepSeek key> DEMO_CODE=<a code you choose> --app acader-room
flyctl deploy --config writing-room-kit/web/fly.toml --dockerfile writing-room-kit/web/Dockerfile --app acader-room
flyctl scale count 1 --app acader-room
```
Your link is then `https://acader-room.fly.dev`. Send investors the link and the code.

## 3. Cost and safety
- **One machine only.** Sessions are kept on that machine's disk and wiped when it restarts or you redeploy.
- **Spending caps** (in `fly.toml`): 3,000 model calls per day for everyone, 260 per session, 8 new sessions per hour per connection. A full session with a submitted essay uses roughly 50 to 80 calls.
- **Set a spend limit in your DeepSeek account as well.** That is the real backstop.
- **Access code.** Without the right code nobody can start a session. The "How it compares" page works without it, because it only shows stored results.
- **Privacy.** Messages go to DeepSeek. The page says not to enter personal or real student data.
- To take it down: `flyctl apps destroy acader-room`, or `flyctl scale count 0 --app acader-room`.

## 4. Changing things
- Edit the pages in `static/index.html`. The server is `app.py`.
- Rebuild the comparison cards from stored results: `python3 web/make_examples.py`.
- Tests: `cd writing-room-kit && ROOM_LLM=stub python3 -m pytest web/tests v04/tests -q`.
