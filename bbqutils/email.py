import smtplib
from email import encoders
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from threading import Lock, Thread
from subprocess import Popen, PIPE

class Mailer:
    def __init__(self, host='localhost', port=587, user=None, passwd=None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.lock = Lock()

    def connect(self):
        self.server = smtplib.SMTP(self.host)
        try:
            self.server.starttls()
        except:
            pass
        if self.user:
            self.server.login(self.user, self.passwd)

    def disconnect(self):
        return self.server.quit()

    def send_email(self, frm=None, to=None, cc=None, bcc=None, subject=None, text='', date=None, reply_to=None, attachments=[]):
        x = 0
        while x < 3:
            x += 1
            try:
                self.lock.acquire()
                messages = []
                rl = recipient_list(to, cc)
                to = recipient_list(to)
                cc = recipient_list(cc)
                if rl:
                    messages.append((rl, create_email(frm, to, cc, None, subject, text, date, reply_to, attachments)))

                if isinstance(bcc, list):
                    for recip in bcc:
                        messages.append((recip, create_email(frm, to, cc, recip, subject, text, date, reply_to, attachments)))

                for m in messages:
                    self.server.sendmail(frm, m[0], m[1].as_string())
                return
            except smtplib.SMTPServerDisconnected:
                self.connect()
            finally:
                self.lock.release()
        raise Exception("Failed to send email three times.")


def sendmail(mail):
    p = Popen(["sendmail", "-t", "-i"], stdin=PIPE)
    return p.communicate(mail.as_string().encode())


def create_attachment(filename, data, mimetype="application/octet-stream"):
    main, sub = mimetype.split('/')
    msg = MIMEBase(main, sub)
    msg.set_payload(data)
    encoders.encode_base64(msg)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    return msg


def recipient_list(*args):
    out = []
    for arg in args:
        if isinstance(arg, str):
            out.append(arg)
        elif isinstance(arg, list):
            out += arg
    if len(out) > 0:
        return ", ".join(out)


def create_email(frm=None, to=None, cc=None, bcc=None, subject=None, text=None, date=None, reply_to=None, attachments=[]):
    msg = MIMEMultipart()
    if frm:
        msg["From"] = frm
    if to:
        msg["To"] = to
    if cc:
        msg["Cc"] = cc
    if bcc:
        msg["Bcc"] = bcc
    if subject:
        msg["Subject"] = subject
    if text:
        textmsg = MIMEText(text, _charset='utf-8')
        msg.attach(textmsg)
    if date is None:
        msg["Date"] = formatdate(localtime=True)
    else:
        msg["Date"] = formatdate(date, localtime=True)
    if reply_to:
        msg["Reply-To"] = reply_to
    for attachment in attachments:
        msg.attach(attachment)
    return msg

