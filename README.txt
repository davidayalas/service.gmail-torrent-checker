This service checks your gmail account (or other imap server) and searches for messages with the substring "torrent email" (by default, but you can customize it) in the subject.

If it finds a message with this subject, then parses the body and gets the first link (http or magnet) and adds it to the trasmission host (it's mandatory to have a web interface for transmission, because torrents injection is via http).

SETUP:

- IMAP host, port, username and password
- Trasmission host, port, username and password
- Timeout between checks for new messages (in seconds, default 900, 15 minutes)
- Avoid certain strings in links or titles (e.g. "720p", "micromkv"). If email comes from torrent emailer (https://github.com/davidayalas/torrent-emailer) it has a title before the link
- Subject to search in email

DEFAULT SETTINGS:

- IMAP: imap.gmail.com:993
- Transmission: localhost:9091
- Timeout between executions: 900 seconds - 15 minutes
- Subject to search: "torrent email"

REQUIREMENTS:

- Transmission daemon and transmission web interface
- IMAP account (gmail, ...)