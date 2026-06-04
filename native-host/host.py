import json
import os
import struct
import subprocess
import sys


def get_download_dir() -> str:
  home = os.path.expanduser('~')
  default_downloads = os.path.join(home, 'Downloads')
  return default_downloads if os.path.isdir(default_downloads) else home


def read_message() -> dict | None:
  raw_length = sys.stdin.buffer.read(4)
  if len(raw_length) == 0:
    return None
  if len(raw_length) < 4:
    raise ValueError('Invalid message length header.')

  message_length = struct.unpack('<I', raw_length)[0]
  message_data = sys.stdin.buffer.read(message_length)
  if len(message_data) < message_length:
    raise ValueError('Incomplete message payload.')

  return json.loads(message_data.decode('utf-8'))


def send_message(payload: dict) -> None:
  encoded = json.dumps(payload, ensure_ascii=False).encode('utf-8')
  sys.stdout.buffer.write(struct.pack('<I', len(encoded)))
  sys.stdout.buffer.write(encoded)
  sys.stdout.buffer.flush()


def handle_download(url: str) -> dict:
  download_dir = get_download_dir()

  try:
    subprocess.Popen(
      ['yt-dlp', url],
      cwd=download_dir,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
      creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    return {
      'ok': True,
      'message': f'已開始下載：{url}'
    }
  except Exception as error:
    return {
      'ok': False,
      'error': f'執行 yt-dlp 失敗：{error}'
    }


def main() -> None:
  try:
    message = read_message()
    if message is None:
      return

    url = message.get('url')
    if not isinstance(url, str) or not url.strip():
      send_message({'ok': False, 'error': '缺少有效網址。'})
      return

    send_message(handle_download(url.strip()))
  except Exception as error:
    send_message({'ok': False, 'error': str(error)})


if __name__ == '__main__':
  main()
