import smtplib
from email.message import Message
from email.utils import formatdate


class Mailer:
	def __init__(self, host, port=587, user=None, passwd=None):
		self.host = host
		self.port = port
		self.user = user
		self.passwd = passwd

	def connect(self):
		self.server = smtplib.SMTP(self.host)
		try:
			self.server.starttls()
		except:
			pass
		if self.user:
			self.server.login(self.user, self.passwd)
	
	def send_email(self, frm=None, to=None, cc=None, bcc=None, subject=None, text=None, date=None):
		messages = []
		rl = recipient_list(to, cc)
		to = recipient_list(to)
		cc = recipient_list(cc)
		if rl:
			messages.append((rl, create_email(frm, to, cc, None, subject, text, date)))

		if isinstance(bcc, list):
			for recip in bcc:
				messages.append((recip, create_email(frm, to, cc, recip, subject, text, date)))
		
		for m in messages:
			self.server.sendmail(frm, m[0], m[1].as_string())


def recipient_list(*args):
	out = []
	for arg in args:
		if isinstance(arg, str):
			out.append(arg)
		elif isinstance(arg, list):
			out += arg
	if len(out) > 0:
		return "; ".join(out)


def create_email(frm=None, to=None, cc=None, bcc=None, subject=None, text=None, date=None):
	msg = Message()
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
		msg.set_payload(text)
	if date is None:
		msg["Date"] = formatdate(localtime=True)
	else:
		msg["Date"] = formatdate(date, localtime=True)
	return msg

