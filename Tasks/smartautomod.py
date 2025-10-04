import discord, re, time, json, hashlib, asyncio, aiohttp
import datetime as dt
from discord.ext import commands
from firebase_admin import credentials, firestore
import firebase_admin
import dotenv
import os

dotenv.load_dotenv(".env")
service = os.getenv("FIREBASE_JSON")
cred = credentials.Certificate(service)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref = db.collection("serverconfigs")
duration = None

FAST_BLOCK_PATTERNS = [
    re.compile(r"(?:https?://)?discord(?:\.gg|\.com/invite)/\w+", re.I),
    re.compile(r"\bfree\s+nitro\b", re.I),
    re.compile(r"@everyone|@here", re.I),
]

OBFUSCATED_DISCORD_COM = re.compile(r"d[\W_]*i[\W_]*s[\W_]*c[\W_]*o[\W_]*r[\W_]*d[\W_]*(?:\.|dot)?[\W_]*c[\W_]*o[\W_]*m", re.I)
OBFUSCATED_DISCORD_GG  = re.compile(r"d[\W_]*i[\W_]*s[\W_]*c[\W_]*o[\W_]*r[\W_]*d[\W_]*(?:\.|dot)?[\W_]*g[\W_]*g", re.I)
SCAM_JOIN_DISCORD      = re.compile(r"\bjoin\b.*\bdiscord\b.*\b(server|link|invite)\b", re.I)
SELF_HARM_INCITE       = re.compile(r"\b(kys|kill\s*yourself|go\s*kill\s*yourself|commit\s*suicide)\b", re.I)

ALLOW_OK_PATTERNS = [
    re.compile(r"^\s*(l+m+a*o+|l+o+l+|rofl|xd+)\s*$", re.I),
    re.compile(r"^[\W_😀-🙏😂🤣😅👌✨💀🔥❤️👍🏽👍🏿👍🏻👍]*$", re.I),
]

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT_S = 35
MAX_CONCURRENT = 1

CB_WINDOW = 20
CB_FAILS_OPEN = 6
CB_COOLDOWN_S = 30

SESSION_TIMEOUT_WARM = 25.0
SESSION_TIMEOUT_HOT  = 20.0
KEEPALIVE = "15m"

DUR_RE = re.compile(r"^\s*(\d+)\s*([smhd])\s*$", re.I)
MULT = {"s":1, "m":60, "h":3600, "d":86400}
RESULT_CACHE_TTL = 90

SYSTEM_PROMPT = (
    'Return ONLY one JSON object with all keys: {"label":"ok|delete","duration":null,"categories":[],"reason":""}\n'
    "Rules:\n"
    "- ok: normal chat, slang, memes, jokes, casual swearing not at a person.\n"
    #"- warn: targeted harassment or severe profanity at a person (no slurs).\n"
    "- delete: scam/spam/phishing domains. Included are discord domains like (discord.gg/xxxxxx) because these are invites. Legitemate links are (https://google.com/search?query=xxxxxxx-xxxxxxxxxxx, www.youtube.com/watch?url=xxxxxxxxxxx) whatever. Official domains you know are probably legitemate)\n"
    "- Always delete child pornography, extreme slurs (like the N word), and other bad things that shouldn be common knowledge."
)

def parse_duration(s: str|None, max_seconds: int = 7*86400) -> int|None:
    if not s: return None
    m = DUR_RE.match(s)
    if not m: return None
    n, unit = int(m.group(1)), m.group(2).lower()
    sec = n * MULT[unit]
    return min(sec, max_seconds)

def short_hash(s: str) -> str:
    return hashlib.blake2b(s.encode("utf-8"), digest_size=8).hexdigest()

def is_fast_ok(text: str) -> bool:
    s = (text or "").strip()
    if not s:
        return True
    for p in ALLOW_OK_PATTERNS:
        if p.match(s):
            return True
    return False

def has_obfuscated_discord(text: str) -> bool:
    if OBFUSCATED_DISCORD_COM.search(text) or OBFUSCATED_DISCORD_GG.search(text) or SCAM_JOIN_DISCORD.search(text):
        return True
    norm = re.sub(r"[\W_]+", "", (text or "").lower())
    if "discordcom" in norm or "discordgg" in norm or "discordappcom" in norm:
        return True
    return False

class SmartAutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sem = asyncio.Semaphore(MAX_CONCURRENT)
        self._model_ready = False
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=None, sock_connect=2.0, sock_read=SESSION_TIMEOUT_WARM)
        )
        asyncio.create_task(self._warm_ollama())
        self._cb_fail_times = []
        self._cb_open_until = 0.0
        self._cache = {}
        self._last_use = time.time()
        asyncio.create_task(self._keepalive_loop())

    def _normalize_result(self, obj: dict) -> dict:
        label = (obj.get("label") or "ok").lower()
        if label not in ("ok", "delete", "warn", "mute"):
            label = "ok"
        duration = obj.get("duration")
        if label != "mute":
            duration = None
        elif duration not in (None, "10m", "1h", "1d"):
            duration = "10m"
        cats = obj.get("categories")
        if not isinstance(cats, list):
            cats = []
        reason = obj.get("reason")
        if not isinstance(reason, str):
            reason = ""
        return {"label": label, "duration": duration, "categories": cats, "reason": reason}

    async def _keepalive_loop(self):
        while True:
            try:
                await asyncio.sleep(300)
                if not self._model_ready:
                    continue
                payload = {
                    "model": OLLAMA_MODEL,
                    "prompt": "ok",
                    "options": {"temperature": 0.0, "num_predict": 1},
                    "keep_alive": KEEPALIVE,
                    "stream": False,
                }
                async with self._session.post(
                    OLLAMA_URL, json=payload,
                    timeout=aiohttp.ClientTimeout(total=None, sock_connect=2.0, sock_read=5.0)
                ) as resp:
                    _ = await resp.text()
            except Exception:
                pass

    async def get_guild_config(self, guild_id: str):
        doc_ref = collection_ref.document(guild_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

    async def _warm_ollama(self):
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": "ok",
            "options": {"temperature": 0.0, "num_predict": 1},
            "keep_alive": KEEPALIVE,
            "stream": False,
        }
        try:
            async with self._session.post(OLLAMA_URL, json=payload) as resp:
                _ = await resp.text()
            self._model_ready = True
            await self._session.close()
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=None, sock_connect=2.0, sock_read=SESSION_TIMEOUT_HOT)
            )
        except Exception:
            await asyncio.sleep(3.0)
            asyncio.create_task(self._warm_ollama())

    def fast_violation(self, content: str) -> tuple[bool, str]:
        for pat in FAST_BLOCK_PATTERNS:
            if pat.search(content):
                return True, f"Matched rule: {pat.pattern}"
        if has_obfuscated_discord(content):
            return True, "Discord invite/domain detected (obfuscated or explicit)"
        if len(content) > 1200:
            return True, "Message too long"
        return False, ""

    def _cb_is_open(self) -> bool:
        return time.time() < self._cb_open_until

    def _cb_record(self, ok: bool):
        now = time.time()
        self._cb_fail_times = [t for t in self._cb_fail_times if now - t < CB_WINDOW]
        if ok:
            return
        self._cb_fail_times.append(now)
        if len(self._cb_fail_times) >= CB_FAILS_OPEN:
            self._cb_open_until = now + CB_COOLDOWN_S

    def cache_get(self, key: str):
        v = self._cache.get(key)
        if not v: return None
        exp, data = v
        if time.time() > exp:
            self._cache.pop(key, None)
            return None
        return data

    def cache_set(self, key: str, data: dict):
        self._cache[key] = (time.time() + RESULT_CACHE_TTL, data)

    def _best_effort_extract_json(self, text: str) -> dict | None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        depth = 0
        start = -1
        
        for i, ch in enumerate(text):
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start != -1:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        continue
        
        if start != -1:
            partial = text[start:].strip()
            
            partial = re.sub(r',\s*$', '', partial)
            partial = re.sub(r',\s*"[^"]*$', '', partial)
            
            if not partial.endswith('}'):
                partial += '}'
            
            try:
                return json.loads(partial)
            except json.JSONDecodeError:
                pass
        
        return None

    async def classify_with_ollama(self, content: str) -> dict | None:
        if self._cb_is_open() or not self._model_ready:
            return None

        async def _parse(body: str | None) -> dict | None:
            if not body:
                return None
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return self._best_effort_extract_json(body)

        async def _call(sock_read_timeout: float) -> dict | None:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{SYSTEM_PROMPT}\n\nUser message:\n{(content or '')[:700]}",
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "repeat_penalty": 1.0,
                    "num_predict": 48,
                    "num_ctx": 1024,
                    "stop": ["}"]
                },
                "keep_alive": KEEPALIVE
            }
            try:
                async with self._session.post(
                    OLLAMA_URL, json=payload,
                    timeout=aiohttp.ClientTimeout(total=None, sock_connect=2.0, sock_read=sock_read_timeout)
                ) as resp:
                    body_text = await resp.text()
                    if resp.status != 200:
                        print(f"[SmartAutoMod] generate non-200: {resp.status} body={body_text[:400]}")
                        return None
                    try:
                        data = json.loads(body_text)
                    except Exception:
                        print(f"[SmartAutoMod] generate returned non-JSON body: {body_text[:400]}")
                        return None
                    raw = (data or {}).get("response", "") or ""
                    print(f"[SmartAutoMod] raw LLM: {raw[:300].replace(chr(10),' ')}")
                    parsed = await _parse(raw)
                    if parsed:
                        parsed = self._normalize_result(parsed)
                        print(f"[SmartAutoMod] parsed LLM: {parsed}")
                    return parsed
            except (asyncio.TimeoutError, aiohttp.ServerDisconnectedError, aiohttp.ClientPayloadError) as e:
                print(f"[SmartAutoMod] request timeout/disconnect: {e!r}")
                return None
            except Exception as e:
                print(f"[SmartAutoMod] request error: {e!r}")
                return None

        async with self.sem:
            res = await _call(OLLAMA_TIMEOUT_S)
            if res is None:
                res = await _call(OLLAMA_TIMEOUT_S + 40)
            if res:
                self._last_use = time.time()
                self._cb_record(True)
                return res
            self._cb_record(False)
            return None

    @commands.Cog.listener()
    async def on_message(self, m: discord.Message):
        if m.guild is None or m.author.bot:
            return

        if SELF_HARM_INCITE.search(m.content or ""):
            dur_seconds = parse_duration("1d")
            print(f"[SmartAutoMod] action: mute (1d) reason=Self-harm incitement content={m.content!r}")
            await self._action_mute(m, "Self-harm incitement", dur_seconds)
            return

        if is_fast_ok(m.content):
            return

        violated, why = self.fast_violation(m.content or "")
        if violated:
            print(f"[SmartAutoMod] action: delete reason={why} content={m.content!r}")
            await self._action_delete(m, reason=f"Rule: {why}")
            return

        key = short_hash((m.content or "")[:2000])
        cached = self.cache_get(key)
        if cached:
            print(f"[SmartAutoMod] cache hit -> {cached}")
            await self._handle_llm_result(m, cached, cached=True)
            return

        result = await self.classify_with_ollama(m.content or "")
        if result:
            self.cache_set(key, result)
            await self._handle_llm_result(m, result)

    async def _handle_llm_result(self, m: discord.Message, result: dict, cached: bool=False):
        label = (result.get("label") or "").lower()
        reason = result.get("reason") or "Policy violation"
        duration = result.get("duration")
        print(f"[SmartAutoMod] decision: label={label} duration={duration} reason={reason!r} content={m.content!r}")

        if label == "delete":
            await self._action_delete(m, reason)
        elif label == "warn":
            await self._action_warn(m, reason)
        elif label == "mute":
            dur_seconds = parse_duration(duration)
            await self._action_mute(m, reason, dur_seconds)

    async def _action_delete(self, m: discord.Message, reason: str):
        try:
            await m.delete()
        except discord.HTTPException:
            pass
        await self._log(m, f"Deleted message from {m.author.mention}: {reason}")
        try:
            print("Deleted a message!")
        except discord.HTTPException:
            pass

    async def _action_warn(self, m: discord.Message, reason: str):
        await self._log(m, f"Warned {m.author.mention}: {reason}")
        try:
            await m.reply("Please keep it civil. Your message may violate the server rules.", delete_after=8)
        except discord.HTTPException:
            pass

    async def _action_mute(self, m: discord.Message, reason: str, dur_seconds: int|None):
        until = None
        if dur_seconds:
            until = discord.utils.utcnow() + dt.timedelta(seconds=dur_seconds)
        try:
            await m.author.timeout(until, reason=reason)
            await self._log(m, f"Muted {m.author.mention} for {duration or 'unspecified'}: {reason}")
            try:
                await m.author.send(f"You were muted in {m.guild.name}.\nReason: {reason}\nDuration: {duration or 'unspecified'}")
            except discord.HTTPException:
                pass
        except discord.Forbidden:
            await self._log(m, f"missing permission to mute {m.author.mention}")
        except discord.HTTPException as e:
            await self._log(m, f"Failed to mute {m.author.mention}: {e}")

    async def _log(self, m: discord.Message, text: str):
        config = await self.get_guild_config(str(m.guild.id))
        chan = None
        try:
            chan_id = config.get("logging_channel")
            if chan_id:
                chan = discord.utils.get(m.guild.text_channels, id=int(chan_id))
        except Exception:
            chan = None
        target = chan or m.channel
        try:
            await target.send(text)
        except discord.HTTPException:
            pass

async def setup(bot):
    await bot.add_cog(SmartAutoMod(bot))
