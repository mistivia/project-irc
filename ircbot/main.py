import socket
import time
import random
import subprocess
import json
import os
import datetime
import urllib.parse
import hashlib

config = None
with open('./config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
SERVER = config['server']
PORT = config['port']
NICKNAME = config['nickname']
REALNAME = config['realname']
CHANNELS = config['channels']
GREETINGS = config['greetings']
LOGPATH = config['logpath']
RELAYBOT = config['relaybot']

IDENT = NICKNAME

BUFFER_SIZE = 2048

commands = {}
def command(name):
    def decorator(func):
        commands[name] = func
        return func
    return decorator

@command("help")
def help_cmd(chan, sender, args):
    return """命令列表：
    1. 询问大模型：!gemini 问题
    2. 具有联网搜索的大模型：!google 问题
    3. 丢骰子： !dice [骰数]d[面数]
    4. 随机选择：!choice 选项1 选项2 ... 选项n
    5. 复读机：!say 复读内容
    6. AI词典: !dict 单词
    7. 查看聊天记录：!log
    8. 离线留言: !memo 收信人 消息
    9. 举办电话会议: !meet
    """

def load_memos():
    try:
        with open("memos", "r") as fp:
            return json.load(fp)
    except:
        return dict()

MEMOS = load_memos()

def save_memos():
    with open("memos", "w") as fp:
        json.dump(MEMOS, fp)

@command("memo")
def memo_cmd(chan, sender, args):
    if chan not in MEMOS:
        MEMOS[chan] = dict()
    if len(args) < 2:
        return '用法: !memo 收信人 消息'
    recver = args[0]
    msg = ' '.join(args[1:])
    if recver not in MEMOS[chan]:
        MEMOS[chan][recver] = []
    MEMOS[chan][recver].append('(来自' + sender + '的留言) ' + recver + ': ' + msg)
    save_memos()
    return '已留言'

@command("meet")
def meet_cmd(chan, sender, args):
    data_to_hash = SERVER + chan + '#' + str(int(time.time()) // 120)
    data_bytes = data_to_hash.encode('utf-8')
    hash_object = hashlib.sha256()
    hash_object.update(data_bytes)
    hex_digest = hash_object.hexdigest()
    return '加入会议: https://meet.jit.si/' + hex_digest[:24] + '#config.startWithVideoMuted=true'

@command("log")
def log_command(chan, sender, args):
    return f"https://raye.mistivia.com/irclog/view/?chan={chan[1:]}"

LAST_SEEN = dict()

def get_greeting(chan, sender, args):
    if sender == NICKNAME:
        return ''
    if not chan in GREETINGS:
        return ''
    if sender in config['no_greeting_nicks']:
        return ''
    if chan in LAST_SEEN \
            and sender in LAST_SEEN[chan] \
            and time.time() - LAST_SEEN[chan][sender] < 300:
        LAST_SEEN[chan][sender] = time.time()
        return ''
    if chan not in LAST_SEEN:
        LAST_SEEN[chan] = dict()
    LAST_SEEN[chan][sender] = time.time()
    return "Dōmo, " + sender + ' san.'

@command("join")
def join_command(chan, sender, args):
    resp = get_greeting(chan, sender, args)
    if chan in MEMOS and sender in MEMOS[chan]:
        for msg in MEMOS[chan][sender]:
            if resp != '':
                resp += '\n'
            resp += msg
        MEMOS[chan][sender] = []
        save_memos()
    return resp

@command("dict")
def dict_command(chan, sender, args):
    query = " ".join(args)
    prompt = """你是一个多语言到汉语的词典，你将针对用户输入的单词，给出中文的释义和原始语言的例句。回复要简单清晰简短。格式为：“释义：xxx；例句：xxx”。如果单词有多个意思，每个意思一行。

用户: """ + query + '\n\n词典: '
    command = ['/usr/local/bin/gemini']
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=prompt)
    return stdout

@command("google")
def gamini_command(chan, sender, args):
    query = " ".join(args)
    prompt = """你是一个人工智能助手，你将针对用户的问题或者指令给出明确、简短、简洁、优秀的回答，必要时使用Google搜索。你的回答对用户非常重要。

用户: """ + query + '\n\n助手: '
    command = ['/usr/local/bin/google']
    process = subprocess.Popen(
        command, 
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=prompt)
    return stdout

@command("gemini")
def gamini_command(chan, sender, args):
    query = " ".join(args)
    prompt = """你是一个人工智能助手，你将针对用户的问题或者指令给出明确、简短、简洁、优秀的回答。你的回答对用户非常重要。

用户: """ + query + '\n\n助手: '
    command = ['/usr/local/bin/gemini']
    process = subprocess.Popen(
        command, 
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=prompt)
    return stdout

@command("hello")
def hello_command(chan, sender, args):
    return f"Hello {sender}!"

@command("say")
def say_command(chan, sender, args):
    if args:
        return " ".join(args)
    else:
        return "What do you want me to say?"

@command("choice")
def choice_command(chan, sender, args):
    if not args:
        return "请提供至少一个选项供我选择。"
    selected_item = random.choice(args)

    return f"{selected_item}"

@command("dice")
def dice_command(chan, sender, args):
    if not args:
        return "请指定要掷的骰子。用法: dice [数量]d[面数]"

    try:
        if args[0][0] == 'd':
            num_dice = 1
            num_sides = int(args[0][1:])
        else:
            num_dice_str, num_sides_str = args[0].split('d')
            num_dice = int(num_dice_str)
            num_sides = int(num_sides_str)
    except ValueError:
        return "无效的骰子格式。请使用 [数量]d[面数] 的格式。"

    if num_dice <= 0 or num_sides <= 1:
        return "骰子数量必须大于0，面数必须大于1。"

    results = []
    for _ in range(num_dice):
        results.append(random.randint(1, num_sides))

    total = sum(results)
    return f"{total}"

@command("roll")
def roll_command(chan, sender, args):
    return dice_command(sender, args)

# ========================================================================

def cut_string(text, chunk_size=420):
    chunks = []
    current_chunk = []
    current_length = 0

    for char in text:
        char_bytes = char.encode('utf-8')
        char_length = len(char_bytes)
        if current_length + char_length > chunk_size:
            if len(current_chunk) > 0:
                chunks.append("".join(current_chunk))
            current_chunk = [char]
            current_length = char_length
        else:
            current_chunk.append(char)
            current_length += char_length
    if len(current_chunk) > 0:
        chunks.append("".join(current_chunk))
    return chunks

def write_log(channel, nick, msg):
    if msg.startswith('!log'):
        return
    if msg.startswith('！log'):
        return
    if msg.startswith('https://raye.mistivia.com/irclog/') and nick == NICKNAME:
        return
    now = datetime.datetime.now()
    base_dir = LOGPATH
    year = now.strftime("%Y")
    filename = now.strftime("%m-%d.txt")

    log_dir = os.path.join(base_dir, channel, year)
    file_path = os.path.join(log_dir, filename)

    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError:
        return

    time_str = now.strftime("%H:%M:%S")
    log_line = f"[{time_str}] <{nick}>: {msg}\n"

    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except IOError:
        pass

def save_topics():
    with open("topics", "w") as fp:
        json.dump(TOPICS, fp)

def load_topics():
    try:
        with open("topics", "r") as fp:
            return json.load(fp)
    except:
        return dict()

TOPICS = load_topics()

class IRCBot:
    def __init__(self, server, port, nickname, ident, realname):
        self.server = server
        self.port = port
        self.nickname = nickname
        self.ident = ident
        self.realname = realname
        self.socket = None
        self.running = True

    def send_raw(self, msg):
        try:
            self.socket.send(f"{msg}\r\n".encode("utf-8"))
            print(f">>> {msg}")
        except Exception as e:
            print(f"Error sending message: {e}")
            self.running = False

    def join_channel(self, channel):
        self.send_raw(f"JOIN {channel}")
        self.send_raw(f"TOPIC {channel}")

    def send_message(self, target, msg):
        if msg == '':
            return
        msg = msg.replace('\r', '')
        lines = msg.split('\n')
        for line in lines:
            self.send_line(target, line)

    def send_line(self, target, msg):
        chunks = cut_string(msg)
        max_length = 100
        message_length = len(msg)
        for chunk in chunks:
            self.send_raw(f"PRIVMSG {target} :{chunk}")
            write_log(target, NICKNAME, chunk)

    def connect(self):
        print(f"Connecting to {self.server}:{self.port}...")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(300) 
            self.socket.connect((self.server, self.port))
            print("Connection successful.")

            self.send_raw(f"NICK {self.nickname}")
            self.send_raw(f"USER {self.ident} 0 * :{self.realname}")
            
        except socket.error as e:
            print(f"Connection error: {e}")
            self.running = False
            return False
        return True

    def handle_command(self, sender, target, command, args):
        if command in commands:
            response = ""
            try:
                response = commands[command](target, sender, args)
                response = response.strip()
            except Exception as e:
                response = f"Error: {e}"
                response = response.strip()

            self.send_message(target, response)

    def parse_message(self, data):
        for line in data.split('\r\n'):
            if not line:
                continue
            
            print(f"<<< {line}")
            
            parts = line.split(' ', 2)
            
            if parts[0] == "PING":
                self.send_raw(f"PONG {parts[1]}")
                continue

            prefix = ""
            if parts[0].startswith(':'):
                prefix = parts.pop(0)[1:]

            if not parts:
                continue

            command = parts[0]
            
            params = []
            trailing = ""
            if len(parts) > 1:
                rest = parts[1]
                if ':' in rest:
                    index = rest.find(':')
                    params.extend(rest[:index].split())
                    trailing = rest[index+1:]
                else:
                    params.extend(rest.split())
            
            self.handle_irc_event(prefix, command, params, trailing)

    def handle_irc_event(self, prefix, command, params, trailing):
        sender_nick = prefix.split('!', 1)[0] if '!' in prefix else prefix
        
        if command == "376" or command == "422":
            print("Registered successfully. Joining channel...")
            for channel in CHANNELS:
                self.join_channel(channel)
        elif command == "331":
            channel = params[1]
            if channel in TOPICS:
                print("No topic, setting...")
                self.send_raw(f"TOPIC {channel} :{TOPICS[channel]}")
        elif command == "TOPIC" or command == "332":
            if command == "332":
                channel = params[1]
            else:
                channel = params[0]
            TOPICS[channel] = trailing
            save_topics()
        elif command == "QUIT":
            for chan in LAST_SEEN:
                if sender_nick in LAST_SEEN[chan]:
                    LAST_SEEN[chan][sender_nick] = time.time()
        elif command == 'PART':
            args = params
            if len(params) >= 1:
                chan = params[0]
            else:
                chan = trailing
            if chan in LAST_SEEN:
                LAST_SEEN[chan][sender_nick] = time.time()
        elif command == "PRIVMSG":
            if sender_nick == NICKNAME:
                return
            target = params[0]
            message = trailing
            
            print(f"[{target}] <{sender_nick}>: {message}")
            write_log(target, sender_nick, message)
            
            if message.startswith("!") or message.startswith("！"):
                try:
                    cmd_parts = message[1:].split()
                    cmd = cmd_parts[0].lower()
                    args = cmd_parts[1:]
                    reply_target = target if target.startswith('#') else sender_nick
                    self.handle_command(sender_nick, reply_target, cmd, args)
                except IndexError:
                    pass
            elif sender_nick == RELAYBOT:
                end_of_nick_index = message.find('>')
                nick = message[1:end_of_nick_index]
                msg_start_index = end_of_nick_index + 2
                msg = message[msg_start_index:].strip()
                if msg.startswith("!") or msg.startswith("！"):
                    try:
                        cmd_parts = msg[1:].split()
                        cmd = cmd_parts[0].lower()
                        args = cmd_parts[1:]
                        if target.startswith('#'):
                            reply_target = target 
                            self.handle_command(nick, reply_target, cmd, args)
                    except IndexError:
                        pass

        elif command == "JOIN":
            args = params
            if len(params) >= 1:
                reply_target = params[0]
            else:
                reply_target = trailing
            self.handle_command(sender_nick, reply_target, 'join', [])

    def run(self):
        if not self.connect():
            return

        buffer = ""
        
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
                
                if not data:
                    print("Connection lost (server closed socket).")
                    self.running = False
                    break
                buffer += data
                if '\r\n' in buffer:
                    messages, buffer = buffer.rsplit('\r\n', 1)
                    self.parse_message(messages)
                    
            except socket.timeout:
                continue
            except socket.error as e:
                print(f"Socket error occurred: {e}")
                self.running = False
                break
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                time.sleep(1)

        self.cleanup()

    def cleanup(self):
        if self.socket:
            print("Closing socket connection.")
            try:
                self.send_raw("QUIT :Bot shutting down")
            except Exception:
                pass
            finally:
                self.socket.close()

if __name__ == "__main__":
    while True:
        try:
            bot = IRCBot(SERVER, PORT, NICKNAME, IDENT, REALNAME)
            bot.run()
        except KeyboardInterrupt:
            print("Bot stopped by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(1)
